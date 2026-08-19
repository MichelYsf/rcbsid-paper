#!/usr/bin/env python
"""CALIBURN honest rebuild - detached, self-resuming stage runner.

Architecture per the rebuild brief:
  * windowless (pythonw + CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP)
  * state inferred from disk on every start; completed work never recomputed
  * logging and status writes NEVER raise, especially inside handlers
  * resource errors (WinError 1450/8/1455, ENOMEM, MemoryError) wait-and-retry
  * durable per-job partials; REBUILD_STATUS.md rewritten after every job
  * halts only on verification / integrity / missing-artifact failures

Stages executed here. The code-authoring stages (3, 7, 8) are the operator's
and are deliberately not automated.
  S4  the construction contrast: natural order vs interleaved, same detector
      and baselines, per-stream, every cell manifested. This is the paper's
      central evidence under the settled framing.
  S5  verified contributions regenerated from real runs.
  S6  corrected change-point statistic, bounded ablation (90 minute cap).
"""
from __future__ import annotations

import ctypes
import datetime
import errno
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
LOG = LOGS / "rebuild.log"
PIDFILE = LOGS / "rebuild.pid"
STATUS = ROOT / "REBUILD_STATUS.md"
HALT = ROOT / "HALT.md"
DONE = ROOT / "REBUILD_DONE.md"
# Per-job subprocess ceiling. The CICIDS arms project to 6-8 CPU-hours, so the
# previous 6 h ceiling would have killed them and written NOTHING. 12 h.
JOB_TIMEOUT_S = 12 * 3600
PARTS = ROOT / "results/rebuild_parts"
PARTS.mkdir(parents=True, exist_ok=True)

CREATE_FLAGS = 0
if IS_WINDOWS:
    CREATE_FLAGS = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

ENV = dict(os.environ)
ENV["PYTHONPATH"] = str(ROOT / "external/KitNET-py")
ENV["PYTHONUNBUFFERED"] = "1"

# pythonw has no console: keep stray writes from ever raising.
if sys.stdout is None or sys.stderr is None:
    _side = open(LOGS / "rebuild_stdio.log", "a", buffering=1, encoding="utf-8")
    sys.stdout = sys.stdout or _side
    sys.stderr = sys.stderr or _side

_buffer = []


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def safe_sleep(seconds):
    """Sleep that OS resource pressure cannot kill."""
    end = time.monotonic() + seconds
    while True:
        left = end - time.monotonic()
        if left <= 0:
            return
        try:
            time.sleep(min(1.0, left))
        except Exception:
            t0 = time.monotonic()
            while time.monotonic() - t0 < 1.0:
                pass


def log(msg):
    """Never raises. Buffers on failure, flushes when writes recover."""
    line = "[" + now() + "] " + str(msg)
    _buffer.append(line)
    for _ in range(3):
        try:
            with open(LOG, "a", encoding="utf-8") as fh:
                for b in _buffer:
                    fh.write(b + "\n")
            _buffer.clear()
            break
        except Exception:
            safe_sleep(0.5)
    try:
        print(line, flush=True)
    except Exception:
        pass


def transient(exc):
    """Resource pressure is never a halt."""
    if isinstance(exc, MemoryError):
        return True
    if isinstance(exc, OSError):
        if getattr(exc, "winerror", None) in (8, 1450, 1455):
            return True
        if exc.errno in (errno.ENOMEM, errno.EAGAIN):
            return True
    return False


def free_gb():
    if not IS_WINDOWS:
        try:
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) / (1 << 20)
        except Exception:
            pass
        return 99.0

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    st = MS()
    st.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPhys / (1 << 30)


def write_status(stage, detail, done_n=None, total_n=None, eta_h=None):
    """Never raises."""
    try:
        prog = ""
        if done_n is not None:
            prog = str(done_n) + "/" + str(total_n) + " jobs"
        eta = ""
        if eta_h:
            eta = "~%.1f h remaining (measured rate)" % eta_h
        body = [
            "# CALIBURN honest rebuild - status",
            "",
            "- **State**: " + str(stage),
            "- **Detail**: " + str(detail),
            "- **Progress**: " + prog,
            "- **ETA**: " + eta,
            "- **Free RAM**: %.1f GB" % free_gb(),
            "- **Last update**: " + now() + " UTC",
            "- **Runner**: detached and self-resuming; resume entry armed until "
            "REBUILD_DONE.md exists",
            "- **Log**: logs/rebuild.log",
            "- **Framing**: SCOPE_DECISIONS.md (per-stream; the construction "
            "contrast is the headline)",
            "",
        ]
        for _ in range(3):
            try:
                STATUS.write_text("\n".join(body), encoding="utf-8")
                return
            except Exception:
                safe_sleep(0.5)
    except Exception:
        pass


def halt(cause, evidence, resume):
    try:
        HALT.write_text("\n".join([
            "# REBUILD HALTED - " + now() + " UTC",
            "",
            "## Cause",
            str(cause),
            "",
            "## Evidence",
            str(evidence),
            "",
            "## Resume",
            "```",
            str(resume),
            "```",
            "",
            "Delete this file once the cause is fixed; the resume entry stays armed.",
            "",
        ]), encoding="utf-8")
    except Exception:
        pass
    write_status("HALTED", cause)
    log("HALT: " + str(cause))
    sys.exit(2)


def describe_exit(returncode) -> str:
    """Plain-language cause for a subprocess return code."""
    try:
        rc = int(returncode)
    except (TypeError, ValueError):
        return "unknown exit status " + str(returncode)
    if rc < 0:
        sig = -rc
        if sig == 9:
            return ("killed by signal 9 (SIGKILL); on Linux this is normally "
                    "the OOM killer, so read it as memory exhaustion, not slowness")
        if sig == 15:
            return "terminated by signal 15 (SIGTERM)"
        return "killed by signal " + str(sig)
    return "exited non-zero with status " + str(rc)


def write_failure_partial(out_path, tag, seconds, cause, detail=""):
    """A killed job must leave evidence, never silence - and the evidence must
    say what actually happened.

    The first version of this hardcoded "TIMEOUT: job exceeded the Ns per-job
    ceiling and was terminated" for EVERY failure, including crashes. When the
    CICIDS natural arm was OOM-killed at 8,680 s on 2026-08-19 it was recorded
    as having exceeded a ceiling of 8,680 s - but the ceiling is 43,200 s, and
    the cause was memory, not time. A reviewer reading that exclusion would
    have concluded the job was too slow and drawn precisely the wrong lesson.

    An excluded cell has to state its real cause, or the exclusion is worse
    than a missing file: it is a confident wrong answer.
    """
    try:
        import csv
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["stream", "arm", "method", "excluded_reason",
                        "cause", "elapsed_seconds", "job_ceiling_seconds",
                        "recorded_utc"])
            reason = ("after " + str(seconds) + "s: " + str(cause) +
                      "; no metrics were produced")
            if detail:
                reason += ". " + str(detail)
            w.writerow([tag, "n/a", "n/a", reason, str(cause), seconds,
                        JOB_TIMEOUT_S, now()])
        return True
    except Exception:
        return False


def run(cmd, timeout=JOB_TIMEOUT_S):
    return subprocess.run(cmd, cwd=str(ROOT), env=ENV, capture_output=True,
                          text=True, timeout=timeout, creationflags=CREATE_FLAGS)


def guard_single_instance():
    if PIDFILE.exists():
        try:
            pid = int(PIDFILE.read_text().strip())
            if IS_WINDOWS:
                out = subprocess.run(["tasklist", "/FI", "PID eq " + str(pid), "/FO", "CSV"],
                                     capture_output=True, text=True,
                                     creationflags=CREATE_FLAGS).stdout
                alive = ('"' + str(pid) + '"') in out and "python" in out.lower()
            else:
                try:
                    os.kill(pid, 0)
                    alive = True
                except OSError:
                    alive = False
            if alive:
                log("another runner is alive (pid " + str(pid) + "); exiting")
                sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            pass
    try:
        PIDFILE.write_text(str(os.getpid()))
    except Exception:
        pass


# --------------------------------------------------------------------------
# stage S4 - the construction contrast
# --------------------------------------------------------------------------
# Four per-arm jobs. Split by ARM so each RUN stays under the 6 h wall cap:
# measured 2.50 ms/row (detector) + 6.58 (HST) => ~3.2-3.4 h per full-stream arm.
# Full streams, never prefixes: a prefix changes the measured prevalence, and
# blaster_worm/spam have too few test attacks in any prefix (verified).
JOBS = [
    ("litnet_natural",   ["--contrast", "litnet_composition", "--arm", "natural"]),
    ("litnet_synthetic", ["--contrast", "litnet_composition", "--arm", "synthetic"]),
    ("cicids_natural",   ["--contrast", "cicids_order", "--arm", "natural"]),
    ("cicids_synthetic", ["--contrast", "cicids_order", "--arm", "synthetic"]),
]


def stage_contrast():
    """Run the remaining contrast arms, in parallel when permitted.

    Sizing measured on real data: litnet_synthetic ~3.2 CPU-h; each CICIDS arm
    ~6.4 CPU-h (d=84, detector 3.65 ms/row, HST 13.37 ms/row) => ~16.1 CPU-h
    for the three remaining arms. Sequentially that breaks an 8 h wall cap, so
    on a multi-core host the arms run CONCURRENTLY (longest arm ~6.4 h) via
    CALIBURN_PARALLEL. Completed arms are skipped: resume never recomputes.
    """
    marker = PARTS / "contrast_done.json"
    if marker.exists():
        return
    script = ROOT / "scripts/run_construction_contrast.py"
    if not script.exists():
        halt("S4 harness missing", str(script) + " is not present",
             '"' + PY + '" "' + str(script) + '"')

    pending = []
    for tag, args in JOBS:
        out = PARTS / ("contrast_" + tag + ".csv")
        if out.exists() and out.stat().st_size > 0:
            log("S4 " + tag + ": already on disk, skipping (resume)")
            continue
        pending.append((tag, args, out))
    total = len(JOBS)
    if not pending:
        marker.write_text(json.dumps({"finished": now()}), encoding="utf-8")
        write_status("S4-CONTRAST", "complete", total, total)
        return

    par = int(os.environ.get("CALIBURN_PARALLEL", "1"))
    log("S4: " + str(len(pending)) + " arm(s) pending, parallelism " + str(par))

    active = {}
    started = {}
    queue = list(pending)
    while queue or active:
        while queue and len(active) < par:
            tag, args, out = queue.pop(0)
            fh = open(LOGS / ("job_" + tag + ".log"), "a", encoding="utf-8")
            proc = subprocess.Popen(
                [PY, str(script)] + args + ["--seeds", "11", "--out", str(out)],
                cwd=str(ROOT), env=ENV, stdout=fh, stderr=subprocess.STDOUT,
                creationflags=CREATE_FLAGS)
            active[proc] = (tag, out, fh)
            started[tag] = time.time()
            log("S4 " + tag + ": started (pid " + str(proc.pid) + ")")
            write_status("S4-CONTRAST", "running " + ", ".join(
                t for t, _, _ in active.values()),
                total - len(queue) - len(active), total)
        for proc in list(active):
            if proc.poll() is None:
                # enforce the per-job ceiling ourselves
                if time.time() - started[active[proc][0]] > JOB_TIMEOUT_S:
                    tag, out, fh = active.pop(proc)
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    try:
                        fh.close()
                    except Exception:
                        pass
                    write_failure_partial(
                        out, tag, JOB_TIMEOUT_S,
                        "exceeded the per-job wall ceiling",
                        "killed by the runner, not by the OS")
                    log("S4 " + tag + ": TIMEOUT at ceiling; durable partial written")
                continue
            tag, out, fh = active.pop(proc)
            try:
                fh.close()
            except Exception:
                pass
            mins = (time.time() - started[tag]) / 60.0
            log("S4 " + tag + ": rc=" + str(proc.returncode) +
                " in " + ("%.1f" % mins) + " min")
            if proc.returncode != 0 and not out.exists():
                write_failure_partial(out, tag, int(time.time() - started[tag]),
                                      describe_exit(proc.returncode),
                                      "see logs/job_" + tag + ".log")
                log("S4 " + tag + ": failed without output (" +
                    describe_exit(proc.returncode) + "); exclusion recorded")
            done_n = sum(1 for t, _ in JOBS
                         if (PARTS / ("contrast_" + t + ".csv")).exists())
            write_status("S4-CONTRAST", "last finished " + tag, done_n, total)
        safe_sleep(20)

    marker.write_text(json.dumps({"finished": now()}), encoding="utf-8")
    write_status("S4-CONTRAST", "complete", total, total)


def main():
    if DONE.exists():
        log("REBUILD_DONE.md exists; nothing to do")
        return
    if HALT.exists():
        write_status("HALTED", "HALT.md present - fix the cause and delete it")
        log("HALT.md present; refusing to run")
        return
    guard_single_instance()
    log("rebuild runner start (pid " + str(os.getpid()) + ", windowless=" +
        str(str(sys.executable).endswith("pythonw.exe")) + ")")
    write_status("STARTING", "runner up (pid " + str(os.getpid()) + ")")
    for fn in (stage_contrast,):
        backoff = 60
        while True:
            try:
                fn()
                break
            except SystemExit:
                raise
            except Exception as exc:
                if transient(exc):
                    log("transient in " + fn.__name__ + ": " + repr(exc) +
                        "; retry in " + str(backoff) + "s")
                    write_status("WAITING", fn.__name__ + " paused " + str(backoff) +
                                 "s on OS resource pressure")
                    safe_sleep(backoff)
                    backoff = min(backoff * 2, 900)
                    continue
                halt("unexpected exception in " + fn.__name__,
                     traceback.format_exc()[-3000:], '"' + PY + '" "' + __file__ + '"')
    log("runner reached the end of the implemented stages")
    write_status("S4 COMPLETE",
                 "construction contrast done; S5/S6 harnesses pending authoring")


if __name__ == "__main__":
    main()
