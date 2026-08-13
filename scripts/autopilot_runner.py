#!/usr/bin/env python
"""CALIBURN autopilot: file-driven state machine for the remaining pipeline.

On every start, state is inferred solely from durable artifacts on disk and
execution continues from the first incomplete step. Idempotent: finished work
is never recomputed. Designed to run detached and WINDOWLESS (pythonw +
CREATE_NO_WINDOW workers): no console exists anywhere for a human to close
and no Ctrl event can propagate (2026-08-08 incident: a visible console was
closed, STATUS_CONTROL_C_EXIT killed all workers).

Stages: S2-RESUME -> S2-MERGE -> S2-DELIVER -> S3-CAL -> S3-RUN ->
S3-DELIVER -> S4-CONDITIONAL -> WRAP. Halt protocol: HALT.md + status HALTED
on control mismatch / integrity failure / missing required artifact.
"""
from __future__ import annotations

import ctypes
import datetime
import itertools
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

IS_WINDOWS = os.name == "nt"
ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / (".venv/Scripts/python.exe" if IS_WINDOWS else ".venv/bin/python"))
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
JOBLOGS = LOGS / "jobs"
JOBLOGS.mkdir(exist_ok=True)
LOG = LOGS / "autopilot.log"
PIDFILE = LOGS / "autopilot.pid"
STATUS = ROOT / "PIPELINE_STATUS.md"
HALTFILE = ROOT / "HALT.md"
DONE = ROOT / "DONE_ALL.md"
STAGE_TIMES = LOGS / "stage_times.json"
PARTS = ROOT / "results/sweep_parts"
TPARTS = ROOT / "results/tuning_parts"
MAX_WORKERS = int(os.environ.get("CALIBURN_WORKERS", "4"))
LOW_RAM_WORKERS = 3
LOW_RAM_GB = 5.0
TASK_NAME = "CALIBURN-AUTOPILOT"

# Windows: no window + separate process group so no Ctrl event reaches
# workers. POSIX: plain subprocesses (run the runner itself under nohup/tmux).
CREATE_FLAGS = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) \
    if IS_WINDOWS else 0

# Under pythonw there is no console: stdout/stderr are invalid. Redirect them
# to a file so stray prints and tracebacks are never lost.
if sys.stdout is None or sys.stderr is None:
    _side = open(LOGS / "autopilot_stdio.log", "a", buffering=1, encoding="utf-8")
    sys.stdout = sys.stdout or _side
    sys.stderr = sys.stderr or _side

ENV = dict(os.environ)
ENV["PATH"] = str(ROOT / ".venv/Scripts") + os.pathsep + ENV.get("PATH", "")
ENV["PYTHONPATH"] = str(ROOT / "external/KitNET-py")
ENV["PYTHONUNBUFFERED"] = "1"

_last_workers: int | None = None


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_sleep(seconds: float) -> None:
    """Sleep that cannot be killed by OS resource pressure: one-second slices,
    any failure of sleep itself is absorbed with a busy-wait slice."""
    deadline = time.monotonic() + seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        try:
            time.sleep(min(1.0, remaining))
        except Exception:
            t0 = time.monotonic()
            while time.monotonic() - t0 < 1.0:
                pass


def _write_with_retries(write_fn, attempts: int = 3, delay: float = 0.5) -> bool:
    for _ in range(attempts):
        try:
            write_fn()
            return True
        except Exception:
            safe_sleep(delay)
    return False


_log_buffer: list[str] = []


def log(msg: str) -> None:
    """Append to the log. NEVER raises: on persistent write failure the lines
    are buffered in memory and flushed when writes succeed again (2026-08-12
    incident: log() raising EINVAL inside the pressure handler escaped the
    resilience wrapper and halted the pipeline)."""
    line = f"[{now()}] {msg}"
    _log_buffer.append(line)

    def flush():
        with open(LOG, "a", encoding="utf-8") as fh:
            for buffered in _log_buffer:
                fh.write(buffered + "\n")

    if _write_with_retries(flush):
        _log_buffer.clear()
    try:
        print(line, flush=True)
    except Exception:
        pass


def free_ram_gb() -> float:
    if not IS_WINDOWS:
        try:
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) / (1 << 20)
        except Exception:
            return 99.0  # no meminfo -> do not throttle
        return 99.0

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPhys / (1 << 30)


def pick_workers(stage: str) -> int:
    global _last_workers
    free = free_ram_gb()
    if stage.startswith("S3"):
        # Laptop (2026-08-12 directive): capped flat at 2 — the pressure
        # events originate outside the pipeline. Dedicated cloud hardware:
        # CALIBURN_WORKERS governs (migration directive: 6 on c7i.2xlarge).
        w = 2 if IS_WINDOWS else MAX_WORKERS
    else:
        w = LOW_RAM_WORKERS if free < LOW_RAM_GB else MAX_WORKERS
    if w != _last_workers:
        log(f"{stage}: worker limit -> {w} (free RAM {free:.1f} GB, "
            f"profile {'S3: 2, 3 above 8GB' if stage.startswith('S3') else f'default: {LOW_RAM_WORKERS} under {LOW_RAM_GB}GB else {MAX_WORKERS}'})")
        _last_workers = w
    return w


def is_transient_os_error(exc: BaseException) -> bool:
    """Resource-flavored OS errors that warrant wait-and-retry, never HALT.

    HALT stays reserved for verification failures, data integrity failures,
    and missing artifacts. FileNotFoundError and friends are NOT transient.
    """
    if isinstance(exc, MemoryError):
        return True
    if isinstance(exc, OSError):
        win = getattr(exc, "winerror", None)
        if win in (8, 1450, 1455):  # NOT_ENOUGH_MEMORY / NO_SYSTEM_RESOURCES / COMMITMENT_LIMIT
            return True
        import errno
        if exc.errno in (errno.ENOMEM, errno.EAGAIN):
            return True
    return False


def write_status(stage: str, detail: str, done_n: int | None = None,
                 total_n: int | None = None, eta_h: float | None = None) -> None:
    """Rewrite the status file. NEVER raises; silently skipped on persistent
    write failure (the next status write refreshes it)."""
    try:
        progress = f"{done_n}/{total_n} jobs done" if done_n is not None else ""
        eta = f"~{eta_h:.1f} h remaining (measured rates)" if eta_h else ""
        workers = f"{_last_workers} (free RAM {free_ram_gb():.1f} GB)" if _last_workers else "n/a"
    except Exception:
        progress = eta = ""
        workers = "n/a"
    _write_with_retries(lambda: STATUS.write_text(f"""# CALIBURN pipeline status

- **State**: {stage}
- **Detail**: {detail}
- **Progress**: {progress}
- **ETA**: {eta}
- **Workers**: {workers}
- **Last update**: {now()}
- **Resume registration**: Startup folder CALIBURN-AUTOPILOT.vbs (hidden; removes itself when DONE_ALL.md exists)
- **Live log**: logs/autopilot.log (per-job logs under logs/jobs/)
""", encoding="utf-8"))


def halt(cause: str, evidence: str, resume_cmd: str) -> None:
    # Reserved for verification / integrity / missing-artifact failures only.
    # The HALT.md write itself gets extended retries; if it still cannot be
    # written, exit anyway — the logon relaunch will re-reach the same
    # verification failure and halt again (self-consistent).
    _write_with_retries(lambda: HALTFILE.write_text(f"""# PIPELINE HALTED — {now()}

## Cause
{cause}

## Evidence
{evidence}

## Resume after fixing the cause
```
{resume_cmd}
```
Delete this file after fixing; the pipeline resumes at next logon (or run the command).
""", encoding="utf-8"), attempts=10, delay=2.0)
    write_status("HALTED", cause)
    log(f"HALT: {cause}")
    sys.exit(2)


def record_stage(name: str, seconds: float) -> None:
    data = json.loads(STAGE_TIMES.read_text()) if STAGE_TIMES.exists() else {}
    data[name] = data.get(name, 0.0) + seconds
    STAGE_TIMES.write_text(json.dumps(data, indent=2))


def run(cmd: list[str], timeout: int = 7200, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), env=ENV, capture_output=True,
                          text=True, timeout=timeout, creationflags=CREATE_FLAGS)


def single_instance_guard() -> None:
    if PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
            if IS_WINDOWS:
                out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                     capture_output=True, text=True,
                                     creationflags=CREATE_FLAGS).stdout
                alive = f'"{pid}"' in out and "python" in out.lower()
            else:
                try:
                    os.kill(pid, 0)
                    alive = True
                except OSError:
                    alive = False
            if alive:
                log(f"another autopilot instance is alive (pid {pid}); exiting")
                sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            pass
    PIDFILE.write_text(str(os.getpid()))


def spend_deadline_epoch() -> float | None:
    """Convert a spend cap into a wall-clock instant.

    CALIBURN_SPEND_CAP_USD with CALIBURN_HOURLY_USD and CALIBURN_START_EPOCH
    (instance launch). The effective deadline is whichever of the wall and
    spend limits arrives first; neither is ever extended.
    """
    try:
        cap = float(os.environ["CALIBURN_SPEND_CAP_USD"])
        rate = float(os.environ["CALIBURN_HOURLY_USD"])
        start = float(os.environ["CALIBURN_START_EPOCH"])
    except (KeyError, ValueError):
        return None
    if rate <= 0:
        return None
    return start + (cap / rate) * 3600.0


def deadline_epoch() -> float | None:
    """Hard wall-clock deadline (UTC epoch) from CALIBURN_DEADLINE_UTC.

    Set when the run is bounded by an external terminator (e.g. the cloud
    watchdog). Without it the pipeline behaves exactly as before.
    """
    v = os.environ.get("CALIBURN_DEADLINE_UTC", "").strip()
    wall = None
    if v:
        try:
            wall = float(v)
        except ValueError:
            try:
                wall = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=datetime.timezone.utc).timestamp()
            except Exception:
                wall = None
    spend = spend_deadline_epoch()
    # Whichever cap arrives first binds. Neither is ever extended.
    candidates = [x for x in (wall, spend) if x]
    return min(candidates) if candidates else None


def run_pool(stage: str, jobs: list, make_cmd, job_key, total_done0: int,
             total: int, spawn_cutoff: float | None = None,
             hard_cutoff: float | None = None) -> dict:
    """Windowless adaptive worker pool. Returns {key: returncode}.

    Worker count is re-evaluated from free RAM at every job handoff (reap or
    spawn opportunity). Each job's output goes to logs/jobs/<key>.log.
    """
    pending = list(jobs)
    active: dict = {}
    walls: list[float] = []
    results: dict = {}
    backoff = 60
    while pending or active:
        try:
            limit = pick_workers(stage)
            for p in list(active):
                if p.poll() is None:
                    continue
                job, t0, fh = active.pop(p)
                fh.close()
                mins = (time.time() - t0) / 60
                walls.append(mins)
                results[job_key(job)] = p.returncode
                done_n = total_done0 + len(results)
                eta = ((len(pending) + len(active)) * (sum(walls) / len(walls))
                       / max(1, limit) / 60) if walls else None
                log(f"{stage} job {job_key(job)}: rc={p.returncode} {mins:.1f} min")
                write_status(stage, f"last: {job_key(job)} rc={p.returncode}",
                             done_n, total, eta_h=eta)
            if hard_cutoff and active and time.time() > hard_cutoff:
                # Stopping spawns is not enough: a single multi-hour job still
                # in flight would block this pool past the deadline, so the
                # later phases (finals, merge, deliverables) would never run
                # and the bounded window would yield raw partials only. Its
                # result could not land before the terminator anyway.
                log(f"{stage}: hard cutoff — abandoning {len(active)} in-flight job(s); "
                    f"their work cannot land before the deadline")
                for p, (job, _t0, fh) in list(active.items()):
                    results[job_key(job)] = "abandoned_at_deadline"
                    try:
                        p.terminate()
                    except Exception:
                        pass
                    try:
                        fh.close()
                    except Exception:
                        pass
                active.clear()
                pending = []
                write_status(stage, "hard cutoff: in-flight jobs abandoned",
                             total_done0 + len(results), total)
                break
            if spawn_cutoff and pending and time.time() > spawn_cutoff:
                # Bounded run: stop starting new work so the remaining budget
                # goes to draining in-flight jobs and producing deliverables.
                log(f"{stage}: spawn cutoff reached — {len(pending)} job(s) will not "
                    f"start; draining {len(active)} in flight")
                write_status(stage, f"spawn cutoff: {len(pending)} job(s) skipped",
                             total_done0 + len(results), total)
                for j in pending:
                    results[job_key(j)] = "not_started"
                pending = []
            below_floor = free_ram_gb() < 2.0
            if below_floor and pending:
                log(f"{stage}: free RAM below 2 GB floor; pausing new spawns, "
                    f"rechecking in 60s ({len(active)} in flight)")
                write_status(stage, "spawns paused: free RAM under 2 GB floor",
                             total_done0 + len(results), total)
                safe_sleep(60)
            else:
                while pending and len(active) < limit and free_ram_gb() >= 2.0:
                    job = pending[0]
                    fh = open(JOBLOGS / f"{job_key(job)}.log", "a", encoding="utf-8")
                    try:
                        p = subprocess.Popen(make_cmd(job), cwd=str(ROOT), env=ENV,
                                             stdout=fh, stderr=subprocess.STDOUT,
                                             creationflags=CREATE_FLAGS)
                    except BaseException:
                        fh.close()
                        raise
                    pending.pop(0)
                    active[p] = (job, time.time(), fh)
                backoff = 60  # healthy iteration resets the backoff
                safe_sleep(10)
        except Exception as exc:
            if not is_transient_os_error(exc):
                raise
            # Everything inside this handler is never-raise (buffered log,
            # retried status write, sliced sleep). Belt and suspenders: any
            # failure inside handling is treated as continued pressure and
            # extends the backoff — it can never escape to the halt path.
            try:
                log(f"{stage}: transient OS resource pressure ({exc!r}); "
                    f"waiting {backoff}s before retry (in-flight jobs keep running)")
                write_status(stage, f"paused {backoff}s on OS resource pressure",
                             total_done0 + len(results), total)
            except Exception:
                backoff = min(backoff * 2, 900)
            safe_sleep(backoff)
            backoff = min(backoff * 2, 900)
    return results


# ---------------------------------------------------------------- Stage 2
S2_LEVELS = ["64", "40", "5", "10"]
S2_SEEDS = [11, 23, 47]
S2_GROUPS = {"bocpd": ["bocpd"], "loda": ["loda"], "hst": ["hst"],
             "lof_ecod": ["lof", "ecod"]}


def s2_part_path(level: str, seed: int, group: str) -> Path:
    p = PARTS / f"cicids_L{level}_s{seed}_{group}.csv"
    if group == "lof_ecod":
        legacy = PARTS / f"cicids_L{level}_s{seed}_batch.csv"
        if legacy.exists() and legacy.stat().st_size > 0:
            return legacy
    return p


def s2_jobs() -> list[dict]:
    jobs = []
    for level, seed, group in itertools.product(S2_LEVELS, S2_SEEDS, S2_GROUPS):
        jobs.append({"level": level, "seed": seed, "group": group,
                     "out": s2_part_path(level, seed, group)})
    jobs.append({"level": "natural", "seed": 11, "group": "bocpd",
                 "out": PARTS / "cicids_Lnat_s11_bocpd.csv"})
    return jobs


def s2_missing() -> list[dict]:
    return [j for j in s2_jobs() if not (j["out"].exists() and j["out"].stat().st_size > 0)]


def s2_key(job: dict) -> str:
    return f"L{job['level']}_s{job['seed']}_{job['group']}"


def s2_cmd(job: dict) -> list[str]:
    out = PARTS / ("cicids_Lnat_s11_bocpd.csv" if job["level"] == "natural" else
                   f"cicids_L{job['level']}_s{job['seed']}_{job['group']}.csv")
    return [PY, str(ROOT / "scripts/run_prevalence_sweep.py"), "--level", job["level"],
            "--seed", str(job["seed"]), "--methods", *S2_GROUPS[job["group"]],
            "--out", str(out)]


def stage_s2_resume() -> None:
    total = len(s2_jobs())
    missing = s2_missing()
    if not missing:
        return
    log(f"S2-RESUME: {len(missing)} of {total} jobs remaining")
    t_stage = time.time()
    fail_counts: dict[str, int] = {}
    while missing:
        run_pool("S2-RESUME", missing, s2_cmd, s2_key, total - len(missing), total)
        still = s2_missing()
        for j in still:
            k = s2_key(j)
            fail_counts[k] = fail_counts.get(k, 0) + 1
            if fail_counts[k] >= 2:
                tail = ""
                jl = JOBLOGS / f"{k}.log"
                if jl.exists():
                    tail = jl.read_text(encoding="utf-8", errors="replace")[-1500:]
                halt(f"Stage 2 job {k} failed twice", tail,
                     f'"{PY}" "{ROOT / "scripts/autopilot_runner.py"}"')
        missing = still
    record_stage("S2-RESUME", time.time() - t_stage)
    log("S2-RESUME complete")


def stage_s2_merge() -> None:
    merged = ROOT / "results/prevalence_sweep_cicids.csv"
    if merged.exists():
        return
    log("S2-MERGE: merging cells + internal control check")
    r = run([PY, str(ROOT / "scripts/merge_sweep_with_stage1.py")])
    log(r.stdout[-2000:])
    if r.returncode != 0:
        halt("Stage 2 internal control failed (natural cell vs Stage 1)",
             r.stdout[-2000:] + r.stderr[-1000:],
             f'"{PY}" "{ROOT / "scripts/merge_sweep_with_stage1.py"}"')
    write_status("S2-MERGE", "merged, control OK")


def stage_s2_deliver() -> None:
    targets = {
        "table": ROOT / "results/prevalence_sweep_table.tex",
        "fig": ROOT / "figures/fig6_prevalence_sweep.pdf",
        "findings": ROOT / "findings_prevalence.md",
    }
    if all(p.exists() for p in targets.values()):
        return
    log("S2-DELIVER: table, figure, findings")
    for script in ("make_prevalence_table.py", "figures/fig6_prevalence_sweep.py",
                   "make_findings_prevalence.py"):
        r = run([PY, str(ROOT / "scripts" / script)])
        if r.returncode != 0:
            halt(f"S2 deliverable generator {script} failed",
                 r.stderr[-1500:], f'"{PY}" "{ROOT / "scripts" / script}"')
    write_status("S2-DELIVER", "deliverables written")


# ---------------------------------------------------------------- Stage 3
S3_DATASETS = ["litnet2020", "cicids2017"]
S3_ALL_METHODS = ["hst", "loda", "rrcf", "iforest_asd", "kitnet", "lof"]


def s3_methods(decision: dict | None = None) -> list[str]:
    """Tunable methods minus any documented reduction.

    A method listed in reductions.json's `skip_methods` is dropped from the
    grid and from the finals, and carries its documented DEFAULT configuration
    in the tables (as ECOD/COPOD always do). The reason lives in the same file
    so the reduction is auditable rather than implicit.
    """
    skip = set(os.environ.get("CALIBURN_SKIP_METHODS", "").split(",")) - {""}
    if decision:
        skip |= set(decision.get("skip_methods", []))
    return [m for m in S3_ALL_METHODS if m not in skip]


S3_METHODS = S3_ALL_METHODS  # back-compat for callers that do not pass a decision
REDUCTIONS = TPARTS / "reductions.json"
S3_CEILING_H = 36.0


def s3_probe_rates() -> dict:
    probe_file = TPARTS / "probe_rates.json"
    if probe_file.exists():
        return json.loads(probe_file.read_text())
    log("S3-CAL: probing per-flow rates (both datasets)")
    code = r"""
import sys, time, json
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import numpy as np
from run_baseline_tuning import load_stream, GRIDS, grid_points, to_wrapper_params
from src.baselines.registry import make_streaming_baseline
out = {}
for ds in ('litnet2020','cicids2017'):
    cfg, X, y = load_stream(ds)
    out[ds+'_n'] = int(len(y))
    Xp = np.asarray(X[3000:8000])
    for m in ('hst','loda','rrcf','iforest_asd','kitnet'):
        try:
            mm = make_streaming_baseline(m, n_features=X.shape[1], seed=11,
                 allow_fallback=False, **to_wrapper_params(m, grid_points(m)[0], stream_len=len(y)))
            for r in np.asarray(X[:600]): mm.score_one(r); mm.learn_one(r)
            t0 = time.perf_counter()
            for r in Xp: mm.score_one(r); mm.learn_one(r)
            out[f'{ds}_{m}_ms'] = (time.perf_counter()-t0)/len(Xp)*1e3
        except Exception as e:
            out[f'{ds}_{m}_ms'] = None; out[f'{ds}_{m}_err'] = str(e)
print(json.dumps(out))
"""
    r = run([PY, "-c", code], timeout=3600)
    if r.returncode != 0:
        halt("S3 probe failed", r.stderr[-1500:],
             f'"{PY}" "{ROOT / "scripts/autopilot_runner.py"}"')
    rates = json.loads(r.stdout.strip().splitlines()[-1])
    TPARTS.mkdir(parents=True, exist_ok=True)
    probe_file.write_text(json.dumps(rates, indent=2))
    log(f"S3 probe: {rates}")
    return rates


def s3_decide_reductions() -> dict:
    if REDUCTIONS.exists():
        return json.loads(REDUCTIONS.read_text())
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_baseline_tuning import grid_points  # noqa: E402
    rates = s3_probe_rates()
    decision = {"train_frac": 1.0, "grid": "full", "datasets": S3_DATASETS,
                "ladder_log": [], "projection_h": None}

    def project(train_frac: float, grids_scale: float, datasets: list[str]) -> float:
        total_s = 0.0
        for ds in datasets:
            n = rates.get(f"{ds}_n", 1_500_000)
            stream = n * (0.70 * train_frac + 0.15)
            for m in ("hst", "loda", "rrcf", "iforest_asd", "kitnet"):
                ms = rates.get(f"{ds}_{m}_ms")
                if ms is None:
                    continue
                pts = max(1, int(round(len(grid_points(m)) * grids_scale)))
                total_s += stream * ms / 1000.0 * pts
            total_s += 45 * 60 * 4 * grids_scale  # lof grid allowance
            for m in ("hst", "loda", "rrcf", "iforest_asd"):
                ms = rates.get(f"{ds}_{m}_ms") or 0
                total_s += n * 0.85 * ms / 1000.0 * 3
        return total_s / 3600 / MAX_WORKERS

    p = project(1.0, 1.0, S3_DATASETS)
    decision["ladder_log"].append(f"full protocol projection: {p:.1f} h wall")
    if p > S3_CEILING_H:
        decision["train_frac"] = 0.4
        p = project(0.4, 1.0, S3_DATASETS)
        decision["ladder_log"].append(f"rung 1 (40% train substream tuning): {p:.1f} h wall")
    if p > S3_CEILING_H:
        decision["grid"] = "coarse"
        p = project(decision["train_frac"], 0.45, S3_DATASETS)
        decision["ladder_log"].append(f"rung 2 (drop middle grid values): {p:.1f} h wall")
    if p > S3_CEILING_H:
        decision["datasets"] = ["litnet2020"]
        p = project(decision["train_frac"], 0.45 if decision["grid"] == "coarse" else 1.0,
                    ["litnet2020"])
        decision["ladder_log"].append(f"rung 3 (LITNET-2020 only): {p:.1f} h wall")
    decision["projection_h"] = p
    REDUCTIONS.write_text(json.dumps(decision, indent=2))
    for line in decision["ladder_log"]:
        log(f"S3-CAL: {line}")
    return decision


def coarse_grid(method: str) -> list[dict]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_baseline_tuning import GRIDS
    grid = GRIDS[method]
    coarse = {k: ([v[0], v[-1]] if len(v) > 2 else v) for k, v in grid.items()}
    keys = list(coarse)
    return [dict(zip(keys, combo)) for combo in itertools.product(*(coarse[k] for k in keys))]


def stage_s3() -> None:
    final_csv = ROOT / "results/baseline_tuning.csv"
    if final_csv.exists():
        return
    TPARTS.mkdir(parents=True, exist_ok=True)
    decision = s3_decide_reductions()
    write_status("S3-RUN", f"reductions: train_frac={decision['train_frac']} "
                           f"grid={decision['grid']} datasets={decision['datasets']}")
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_baseline_tuning import grid_points as full_points

    t_stage = time.time()
    methods = s3_methods(decision)
    if set(S3_ALL_METHODS) - set(methods):
        log(f"S3: documented reduction — skipping "
            f"{sorted(set(S3_ALL_METHODS) - set(methods))} (see reductions.json)")
    jobs = []
    for ds in decision["datasets"]:
        for method in methods:
            pts = coarse_grid(method) if decision["grid"] == "coarse" else full_points(method)
            full = full_points(method)
            for i, pt in enumerate(pts):
                idx = full.index(pt) if pt in full else i
                out = TPARTS / f"grid_{ds}_{method}_{idx:03d}.csv"
                if not (out.exists() and out.stat().st_size > 0):
                    jobs.append({"ds": ds, "method": method, "idx": idx})
    # Cheapest method first. Job order cannot affect any result (each point is
    # independent and seed-deterministic), but under a bounded window it
    # decides WHICH points get evaluated: measured per-point costs span
    # ~2.3 min (hst) to ~5 h (rrcf), so method order alone is the difference
    # between selections for five methods and selections for two.
    grid_cost = {"hst": 0, "kitnet": 1, "lof": 2, "iforest_asd": 3, "loda": 4, "rrcf": 5}
    jobs.sort(key=lambda j: (grid_cost.get(j["method"], 9), j["idx"]))
    log(f"S3-RUN: {len(jobs)} grid jobs to run (cheapest method first: "
        f"{', '.join(dict.fromkeys(j['method'] for j in jobs))})")

    def cmd(j):
        return [PY, str(ROOT / "scripts/run_baseline_tuning.py"), "--phase", "grid",
                "--dataset", j["ds"], "--method", j["method"], "--point", str(j["idx"]),
                "--train-frac", str(decision["train_frac"])]

    def key(j):
        return f"grid_{j['ds']}_{j['method']}_{j['idx']:03d}"

    # Bounded-run budgeting: reserve time for finals and for the deliverable
    # generation, so a run that cannot finish everything still produces the
    # tuning tables and findings rather than nothing at all.
    dl = deadline_epoch()
    grid_cutoff = finals_cutoff = None
    if dl:
        finals_reserve = float(os.environ.get("CALIBURN_FINALS_RESERVE_S", 5400))
        deliver_reserve = float(os.environ.get("CALIBURN_DELIVER_RESERVE_S", 1500))
        grid_cutoff = dl - finals_reserve - deliver_reserve
        finals_cutoff = dl - deliver_reserve
        log(f"S3 deadline budgeting: grid spawns stop "
            f"{datetime.datetime.utcfromtimestamp(grid_cutoff):%H:%M}Z, finals stop "
            f"{datetime.datetime.utcfromtimestamp(finals_cutoff):%H:%M}Z, "
            f"hard deadline {datetime.datetime.utcfromtimestamp(dl):%H:%M}Z")

    if jobs:
        run_pool("S3-RUN", jobs, cmd, key, 0, len(jobs), spawn_cutoff=grid_cutoff,
                 hard_cutoff=(grid_cutoff + 600) if grid_cutoff else None)

    # Finals go through the same pool as the grid. They are independent per
    # (dataset, method) full-stream passes, so running them sequentially left
    # most of the machine idle — the single biggest lever on wall time, and
    # therefore on cloud cost. The pool already enforces the RAM floor.
    final_jobs = []
    for ds in decision["datasets"]:
        for method in s3_methods(decision):
            if not (TPARTS / f"final_{ds}_{method}_tuned.csv").exists():
                final_jobs.append({"ds": ds, "method": method, "default": False})
        for method in ("ecod", "copod"):  # no tunables: carried forward, documented
            if not (TPARTS / f"final_{ds}_{method}_default.csv").exists():
                final_jobs.append({"ds": ds, "method": method, "default": True})

    def final_cmd(j):
        c = [PY, str(ROOT / "scripts/run_baseline_tuning.py"), "--phase", "final",
             "--dataset", j["ds"], "--method", j["method"]]
        if j["default"]:
            c += ["--params-json", "{}"]
        return c

    def final_key(j):
        return f"final_{j['ds']}_{j['method']}_{'default' if j['default'] else 'tuned'}"

    if final_jobs:
        # Cheapest-first so a truncated window still yields tuned rows for as
        # many methods as possible (batch references and light streamers land
        # long before rrcf/iforest_asd on the full stream).
        order = {"lof": 0, "ecod": 1, "copod": 2, "kitnet": 3, "hst": 4,
                 "loda": 5, "iforest_asd": 6, "rrcf": 7}
        final_jobs.sort(key=lambda j: order.get(j["method"], 9))
        log(f"S3-FINALS: {len(final_jobs)} final jobs to run (pooled, cheapest first)")
        run_pool("S3-FINALS", final_jobs, final_cmd, final_key, 0, len(final_jobs),
                 spawn_cutoff=finals_cutoff,
                 hard_cutoff=(finals_cutoff + 300) if finals_cutoff else None)

    r = run([PY, str(ROOT / "scripts/run_baseline_tuning.py"), "--merge", str(TPARTS),
             "--out", str(final_csv)])
    if r.returncode != 0 or not final_csv.exists():
        halt("S3 merge failed", r.stderr[-1500:],
             f'"{PY}" "{ROOT / "scripts/run_baseline_tuning.py"}" --merge "{TPARTS}" --out "{final_csv}"')
    record_stage("S3", time.time() - t_stage)


def stage_s3_deliver() -> None:
    targets = [ROOT / "results/table4_litnet_tuned.tex",
               ROOT / "results/tuning_delta_summary.tex",
               ROOT / "results/appendix_a_replacement.tex",
               ROOT / "findings_tuning.md"]
    if all(p.exists() for p in targets):
        return
    log("S3-DELIVER: tables, appendix, findings")
    for script in ("make_tuning_tables.py", "make_findings_tuning.py"):
        r = run([PY, str(ROOT / "scripts" / script)])
        if r.returncode != 0:
            halt(f"S3 deliverable generator {script} failed", r.stderr[-1500:],
                 f'"{PY}" "{ROOT / "scripts" / script}"')
    write_status("S3-DELIVER", "deliverables written")


# ---------------------------------------------------------------- Stage 4
def stage_s4() -> None:
    scope = ROOT / "results/burnrate_scope.json"
    fig = ROOT / "figures/fig7_burnrate_litnet.pdf"
    out_csv = ROOT / "results/burnrate_litnet.csv"
    if (out_csv.exists() and fig.exists()) or (ROOT / "findings_burnrate.md").exists():
        return
    dl = deadline_epoch()
    if dl and time.time() > dl - 2400:
        (ROOT / "findings_burnrate.md").write_text(
            f"# Burn-rate validation scoping\n\nStage 4 was not run. The bounded "
            f"cloud window (hard deadline "
            f"{datetime.datetime.utcfromtimestamp(dl):%Y-%m-%d %H:%M} UTC) was "
            f"consumed by the Stage 3 tuning grid and finals, which carry higher "
            f"priority. No burn-rate numbers are reported rather than rushed ones; "
            f"the harness (scripts/run_burnrate_litnet.py, the span check, and "
            f"scripts/figures/fig7_burnrate_litnet.py) is committed and ready to run "
            f"when hardware time is available.\n")
        log("S4: skipped — insufficient time before the hard deadline")
        return
    rates = s3_probe_rates()
    n = rates.get("litnet2020_n", 1_500_000)
    bocpd_ms = 4.8  # measured in-situ mixed-schedule rate on CICIDS; same order on LITNET
    proj_h = n * bocpd_ms / 1000 / 3600 + 0.5
    scope.parent.mkdir(parents=True, exist_ok=True)
    scope.write_text(json.dumps({"projection_h": proj_h, "fits": proj_h <= 12.0}))
    if proj_h > 12.0:
        (ROOT / "findings_burnrate.md").write_text(
            f"# Burn-rate validation scoping\n\nStage 4 was scoped out: the CALIBURN "
            f"scoring pass over the LITNET-2020 stream projects to ~{proj_h:.1f} h wall "
            f"on this hardware, exceeding the 12 additional-hour budget the autopilot "
            f"allows after Stage 3. No burn-rate numbers are reported rather than "
            f"reporting rushed ones.\n")
        log(f"S4: scoped out at projection {proj_h:.1f} h")
        return
    log(f"S4: running (projection {proj_h:.1f} h)")
    t0 = time.time()
    r = run([PY, str(ROOT / "scripts/run_burnrate_litnet.py")], timeout=14 * 3600)
    log(r.stdout[-3000:])
    if r.returncode != 0:
        halt("S4 burn-rate run failed", r.stderr[-1500:],
             f'"{PY}" "{ROOT / "scripts/run_burnrate_litnet.py"}"')
    for script in ("figures/fig7_burnrate_litnet.py", "make_burnrate_table.py"):
        rr = run([PY, str(ROOT / "scripts" / script)])
        if rr.returncode != 0:
            halt(f"S4 deliverable {script} failed", rr.stderr[-1500:],
                 f'"{PY}" "{ROOT / "scripts" / script}"')
    record_stage("S4", time.time() - t0)


# ---------------------------------------------------------------- Wrap-up
def stage_wrap() -> None:
    if DONE.exists():
        return
    log("WRAP: pytest + smoke test")
    r = run([PY, "-m", "pytest", "-q"], timeout=3600)
    if r.returncode != 0:
        halt("pytest failed at wrap-up", r.stdout[-2000:], f'"{PY}" -m pytest -q')
    bash = r"C:\Program Files\Git\bin\bash.exe" if IS_WINDOWS else "bash"
    if IS_WINDOWS and not Path(bash).exists():
        bash = "bash"
    r = subprocess.run([bash, "scripts/run_smoke_test.sh"], cwd=str(ROOT), env=ENV,
                       capture_output=True, text=True, timeout=3600,
                       creationflags=CREATE_FLAGS)
    if r.returncode != 0:
        halt("smoke test failed at wrap-up", (r.stdout + r.stderr)[-2000:],
             "bash scripts/run_smoke_test.sh")

    log("WRAP: RUN_REPORT completion")
    freeze = run([PY, "-m", "pip", "freeze"]).stdout
    stage_times = json.loads(STAGE_TIMES.read_text()) if STAGE_TIMES.exists() else {}
    reductions = json.loads(REDUCTIONS.read_text()) if REDUCTIONS.exists() else {}
    findings = ""
    for f in ("findings_prevalence.md", "findings_tuning.md", "findings_burnrate.md",
              "findings_paper_overlap.md"):
        p = ROOT / f
        if p.exists():
            findings += f"\n\n---\n\n<!-- inlined {f} -->\n\n" + p.read_text(encoding="utf-8")
    with open(ROOT / "RUN_REPORT.md", "a", encoding="utf-8") as fh:
        fh.write(f"""

## Autopilot completion — {now()}

Wall clock per stage (seconds, cumulative across restarts):
```json
{json.dumps(stage_times, indent=2)}
```

Stage 3 reductions decision:
```json
{json.dumps(reductions, indent=2)}
```

2026-08-08 incident: the first detached launch used a cmd/python chain with a
visible console; closing that window sent STATUS_CONTROL_C_EXIT to all
workers. Relaunched windowless (pythonw + CREATE_NO_WINDOW +
CREATE_NEW_PROCESS_GROUP everywhere) with a RAM-adaptive worker pool
(3 workers under 5 GB free, else 4, re-checked at every job handoff).

Power settings: NOT modified by the agent (system-settings policy). The
pre-authorized commands are staged in scripts/apply_power_settings.cmd for
the operator; resilience is provided by the logon Startup entry instead.

pip freeze:
```
{freeze}
```
{findings}
""")

    log("WRAP: commit + push")

    def git(*args):
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                              text=True, creationflags=CREATE_FLAGS)
    git("add", "-A")
    git("add", "-f", "results/")
    git("commit", "-m", "exp: autopilot completion — Stage 2/3(/4) results, "
        "deliverables, RUN_REPORT\n\nCo-Authored-By: Claude Fable 5 <noreply@anthropic.com>")
    push = git("push", "-u", "origin", "exp/prevalence-and-tuning")
    push_note = "pushed" if push.returncode == 0 else \
        f"PUSH FAILED (auth?) — commits are local only: {push.stderr[-300:]}"
    log(f"WRAP: {push_note}")

    deliverables = [str(p.relative_to(ROOT)) for p in [
        ROOT / "results/prevalence_sweep_cicids.csv",
        ROOT / "results/prevalence_sweep_table.tex",
        ROOT / "figures/fig6_prevalence_sweep.pdf",
        ROOT / "findings_prevalence.md",
        ROOT / "results/baseline_tuning.csv",
        ROOT / "results/table4_litnet_tuned.tex",
        ROOT / "results/table5_cicids_tuned.tex",
        ROOT / "results/tuning_delta_summary.tex",
        ROOT / "results/appendix_a_replacement.tex",
        ROOT / "findings_tuning.md",
        ROOT / "results/burnrate_litnet.csv",
        ROOT / "results/burnrate_litnet_table.tex",
        ROOT / "figures/fig7_burnrate_litnet.pdf",
        ROOT / "findings_burnrate.md",
        ROOT / "findings_paper_overlap.md",
        ROOT / "RUN_REPORT.md",
    ] if p.exists()]
    DONE.write_text(f"""# DONE_ALL — {now()}

Branch: exp/prevalence-and-tuning ({push_note})

## Deliverables
""" + "\n".join(f"- {d}" for d in deliverables) + """

## Paste into the Claude chat for manuscript integration
- findings_prevalence.md
- findings_tuning.md
- results/prevalence_sweep_table.tex
- results/table4_litnet_tuned.tex
- results/table5_cicids_tuned.tex
- results/tuning_delta_summary.tex
- results/appendix_a_replacement.tex
- RUN_REPORT.md (the reductions + gate sections)
""", encoding="utf-8")
    if IS_WINDOWS:
        subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
                       capture_output=True, text=True, creationflags=CREATE_FLAGS)
        startup_dir = Path(os.environ.get("APPDATA", "")) / \
            "Microsoft/Windows/Start Menu/Programs/Startup"
        for name in ("CALIBURN-AUTOPILOT.cmd", "CALIBURN-AUTOPILOT.vbs"):
            f = startup_dir / name
            if f.exists():
                f.unlink()
    write_status("COMPLETE", "all stages done; resume registration removed")
    log("WRAP complete — DONE_ALL.md written")


def main() -> None:
    if DONE.exists():
        log("DONE_ALL.md exists; nothing to do")
        return
    if HALTFILE.exists():
        write_status("HALTED", "HALT.md present — fix the cause and delete HALT.md")
        log("HALT.md present; refusing to run until it is removed")
        return
    single_instance_guard()
    if "--infer" in sys.argv:
        miss = s2_missing()
        print(f"S2 remaining jobs: {len(miss)}")
        for j in miss:
            print(f"  L{j['level']} s{j['seed']} {j['group']}")
        return
    log(f"autopilot start (pid {os.getpid()}, windowless={sys.executable.endswith('pythonw.exe')})")
    pick_workers("startup")
    write_status("STARTING", f"runner up (pid {os.getpid()}); "
                             f"{len(s2_missing())} of {len(s2_jobs())} S2 jobs remaining")
    for stage_fn in (stage_s2_resume, stage_s2_merge, stage_s2_deliver,
                     stage_s3, stage_s3_deliver, stage_s4, stage_wrap):
        backoff = 60
        while True:
            try:
                stage_fn()
                break
            except SystemExit:
                raise
            except Exception as exc:
                if is_transient_os_error(exc):
                    # Stages are idempotent; wait out the resource pressure and
                    # re-enter. Only verification/integrity/missing-artifact
                    # conditions may write HALT.md.
                    try:
                        log(f"transient OS resource error in {stage_fn.__name__}: "
                            f"{exc!r}; retrying in {backoff}s")
                        write_status("WAITING", f"{stage_fn.__name__} paused {backoff}s "
                                                f"on OS resource pressure")
                    except Exception:
                        backoff = min(backoff * 2, 900)
                    safe_sleep(backoff)
                    backoff = min(backoff * 2, 900)
                    continue
                halt("unexpected exception in autopilot",
                     traceback.format_exc()[-3000:],
                     f'"{PY}" "{ROOT / "scripts/autopilot_runner.py"}"')


if __name__ == "__main__":
    main()
