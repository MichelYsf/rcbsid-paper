#!/usr/bin/env python
"""Detached puller: bring S4 contrast results home from the EC2 instance.

Runs windowless on the laptop and survives session death. The instance's own
watchdog only STOPS the box at the wall cap, so nothing is destroyed if this
puller dies - but a live puller means results are never more than 15 minutes
from being safe on the laptop, and the run can be closed out immediately.

Exits when all four arms are on disk locally, or 45 minutes past the cap.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = ROOT / "caliburn-s3-key.pem"
HOST = "ubuntu@35.158.242.107"
REMOTE = "/home/ubuntu/rcbsid-paper"
DEADLINE = 1787149285          # 8 h wall cap
STOP_AT = DEADLINE + 45 * 60
INTERVAL = 15 * 60
LOG = ROOT / "logs/puller.log"
PARTS = ROOT / "results/rebuild_parts"
ARMS = ["litnet_natural", "litnet_synthetic", "cicids_natural", "cicids_synthetic"]


def log(msg: str) -> None:
    line = time.strftime("[%Y-%m-%d %H:%M:%S] ", time.gmtime()) + msg
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def scp(remote_glob: str, local_dir: Path) -> bool:
    local_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["scp", "-i", str(KEY), "-o", "StrictHostKeyChecking=no",
           "-o", "ConnectTimeout=30", "-q",
           HOST + ":" + remote_glob, str(local_dir)]
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                           creationflags=flags)
        if r.returncode != 0 and r.stderr.strip():
            log("  scp " + remote_glob + ": " + r.stderr.strip()[:200])
        return r.returncode == 0
    except Exception as exc:
        log("  scp " + remote_glob + " raised " + repr(exc)[:200])
        return False


def have_all() -> bool:
    return all((PARTS / ("contrast_" + a + ".csv")).exists() for a in ARMS)


def main() -> int:
    log("puller up (pid " + str(os.getpid()) + "), interval " +
        str(INTERVAL // 60) + " min, stop at epoch " + str(STOP_AT))
    while True:
        scp(REMOTE + "/results/rebuild_parts/*.csv", PARTS)
        scp(REMOTE + "/results/manifests/*", ROOT / "results/manifests")
        scp(REMOTE + "/logs/*.log", ROOT / "logs/instance")
        scp(REMOTE + "/REBUILD_STATUS.md", ROOT / "logs/instance")
        present = [a for a in ARMS if (PARTS / ("contrast_" + a + ".csv")).exists()]
        log("pulled; arms on disk " + str(len(present)) + "/4: " + ", ".join(present))
        if have_all():
            log("ALL FOUR ARMS HOME - puller exiting")
            return 0
        if time.time() > STOP_AT:
            log("past cap + 45 min - puller exiting with " + str(len(present)) + "/4")
            return 1
        time.sleep(INTERVAL)


if __name__ == "__main__":
    raise SystemExit(main())
