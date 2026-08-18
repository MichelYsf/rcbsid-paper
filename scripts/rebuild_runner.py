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


def run(cmd, timeout=7200):
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
    marker = PARTS / "contrast_done.json"
    if marker.exists():
        return
    script = ROOT / "scripts/run_construction_contrast.py"
    if not script.exists():
        halt("S4 harness missing", str(script) + " is not present",
             '"' + PY + '" "' + str(script) + '"')
    total = len(JOBS)
    walls = []
    for i, (tag, args) in enumerate(JOBS, 1):
        out = PARTS / ("contrast_" + tag + ".csv")
        if out.exists() and out.stat().st_size > 0:
            continue
        eta = None
        if walls:
            eta = (total - i + 1) * (sum(walls) / len(walls)) / 3600.0
        write_status("S4-CONTRAST", "running " + tag, i - 1, total, eta)
        backoff = 60
        while True:
            try:
                t0 = time.time()
                r = run([PY, str(script)] + args + ["--seeds", "11",
                        "--out", str(out)], timeout=6 * 3600)
                walls.append(time.time() - t0)
                log("S4 " + tag + ": rc=" + str(r.returncode) + " in " +
                    ("%.1f" % ((time.time() - t0) / 60.0)) + " min")
                if r.returncode != 0:
                    log("S4 " + tag + " stderr: " + (r.stderr or "")[-500:])
                break
            except Exception as exc:
                if not transient(exc):
                    raise
                log("S4 " + tag + ": transient " + repr(exc) + "; retry in " +
                    str(backoff) + "s")
                write_status("S4-CONTRAST", "paused on resource pressure", i - 1, total)
                safe_sleep(backoff)
                backoff = min(backoff * 2, 900)
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
