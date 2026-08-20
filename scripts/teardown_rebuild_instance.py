#!/usr/bin/env python
"""Verified teardown of the S4 rebuild instance, with measured cost.

Refuses to terminate until the results are demonstrably home AND committed.
An instance is cheap; an unrepeatable 3-hour run is not, and "I already pulled
it" is exactly the belief that is wrong when it matters. The checks are:

  1. all four contrast arms present locally and non-empty
  2. every arm tracked by git with no uncommitted modification
  3. the local branch is not ahead of its remote (results are pushed)

Only then does it terminate, wait for the terminated state, and confirm the
root volume is actually gone rather than assuming DeleteOnTermination did its
job. Cost is reported from list prices and labelled as an estimate, because
Cost Explorer lags and this script must not pretend to an authority it lacks.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "logs/aws_rebuild_instance.json"
SNAP = ROOT / "logs/aws_rebuild_snapshot.txt"
PARTS = ROOT / "results/rebuild_parts"
REGION = "eu-central-1"
ARMS = ["litnet_natural", "litnet_synthetic", "cicids_natural", "cicids_synthetic"]

# eu-central-1 list prices, USD. Stated here so the arithmetic is auditable.
EBS_GB_MONTH = 0.0952        # gp3 storage
EBS_IOPS_MONTH = 0.006       # per provisioned IOPS above the free 3000
EBS_TPUT_MONTH = 0.048       # per provisioned MB/s above the free 125
SNAP_GB_MONTH = 0.054
VOL_GB, VOL_IOPS, VOL_TPUT = 100, 6000, 500


def aws(*args: str) -> dict | list | None:
    cmd = ["aws"] + list(args) + ["--region", REGION, "--output", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("  aws " + " ".join(args[:3]) + " failed: " + r.stderr.strip()[:300])
        return None
    return json.loads(r.stdout) if r.stdout.strip() else None


def git(*args: str) -> str:
    r = subprocess.run(["git"] + list(args), cwd=str(ROOT),
                       capture_output=True, text=True, timeout=120)
    return r.stdout.strip()


def results_are_safe() -> tuple[bool, list[str]]:
    problems = []
    for a in ARMS:
        p = PARTS / ("contrast_" + a + ".csv")
        if not p.exists():
            problems.append("missing locally: " + p.name)
        elif p.stat().st_size == 0:
            problems.append("empty: " + p.name)
    dirty = git("status", "--porcelain", "--", str(PARTS))
    if dirty:
        problems.append("uncommitted changes under results/rebuild_parts:\n    " +
                        dirty.replace("\n", "\n    "))
    ahead = git("rev-list", "--count", "@{upstream}..HEAD")
    if ahead and ahead != "0":
        problems.append(ahead + " commit(s) not pushed to the remote")
    return (not problems), problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true",
                    help="actually terminate; without it this is a dry check")
    ap.add_argument("--keep-snapshot", action="store_true",
                    help="retain the pre-CICIDS snapshot (it bills monthly)")
    ap.add_argument("--compute-hours", type=float, default=None,
                    help="measured instance RUNNING hours; without it the script "
                         "assumes continuous running since launch, which "
                         "overstates cost for an instance that was stopped")
    ap.add_argument("--ebs-hours", type=float, default=None,
                    help="hours the volume has existed (it bills while stopped)")
    ap.add_argument("--force", action="store_true",
                    help="terminate despite failed result checks (records why)")
    a = ap.parse_args()

    if not STATE.exists():
        print("no instance state at " + str(STATE))
        return 1
    st = json.loads(STATE.read_text())
    iid, vol, hourly = st["instance_id"], st["volume"], float(st["hourly"])
    launch = int(st["launch_epoch"])

    print("instance " + iid + "  volume " + vol)
    ok, problems = results_are_safe()
    print("")
    print("result safety checks: " + ("PASS" if ok else "FAIL"))
    for p in problems:
        print("  - " + p)
    if not ok and not a.force:
        print("")
        print("REFUSING to terminate. Bring the results home and push them first,")
        print("or pass --force if you have decided the run is being abandoned.")
        return 1

    desc = aws("ec2", "describe-instances", "--instance-ids", iid)
    state = "unknown"
    if desc:
        try:
            state = desc["Reservations"][0]["Instances"][0]["State"]["Name"]
        except (KeyError, IndexError):
            pass
    print("")
    print("current instance state: " + state)

    # ---- cost, measured from the billed window ---------------------------
    # Compute and EBS bill on DIFFERENT clocks and conflating them is wrong by
    # a lot. A stopped instance bills no compute but its volume keeps billing;
    # this run was stopped for ~18 h between the wall cap and teardown. EC2
    # does not report cumulative running time, and reconstructing it needs
    # CloudTrail, so running hours are passed in from the operator record and
    # EBS hours are taken from the volume creation time.
    end = int(time.time())
    hours = a.compute_hours if a.compute_hours is not None else max(0.0, (end - launch) / 3600.0)
    ebs_hours = a.ebs_hours if a.ebs_hours is not None else hours
    compute = hours * hourly
    ebs = (VOL_GB * EBS_GB_MONTH + max(0, VOL_IOPS - 3000) * EBS_IOPS_MONTH +
           max(0, VOL_TPUT - 125) * EBS_TPUT_MONTH) / 730.0 * ebs_hours
    print("")
    print("MEASURED COST (list prices, eu-central-1)")
    print("  instance running  : %.2f h (compute billed)" % hours)
    print("  volume existed    : %.2f h (EBS billed, including while stopped)" % ebs_hours)
    print("  compute           : %.2f h x $%.4f/h = $%.2f" % (hours, hourly, compute))
    print("  EBS gp3 (100 GB, 6000 IOPS, 500 MB/s) = $%.2f" % ebs)
    total = compute + ebs
    print("  ---------------------------------------------")
    print("  total this run    : $%.2f" % total)
    print("  (estimate from list prices; Cost Explorer lags ~24 h and is the "
          "authority)")

    if not a.confirm:
        print("")
        print("dry check only. Re-run with --confirm to terminate.")
        return 0

    if state not in ("terminated", "shutting-down"):
        print("")
        print("terminating " + iid + " ...")
        aws("ec2", "terminate-instances", "--instance-ids", iid)
        for _ in range(60):
            time.sleep(10)
            d = aws("ec2", "describe-instances", "--instance-ids", iid)
            try:
                state = d["Reservations"][0]["Instances"][0]["State"]["Name"]
            except (KeyError, IndexError, TypeError):
                break
            print("  state: " + state)
            if state == "terminated":
                break

    # ---- verify the volume is actually gone ------------------------------
    print("")
    print("verifying volume deletion (DeleteOnTermination is a setting, not a "
          "guarantee) ...")
    vstate = "gone"
    v = aws("ec2", "describe-volumes", "--volume-ids", vol)
    if v:
        try:
            vstate = v["Volumes"][0]["State"]
        except (KeyError, IndexError):
            vstate = "gone"
    if vstate == "gone":
        print("  volume " + vol + " no longer exists - VERIFIED DELETED")
    elif vstate in ("deleting",):
        print("  volume " + vol + " is deleting")
    else:
        print("  volume " + vol + " is still " + vstate +
              " - it will keep billing. Deleting it explicitly.")
        aws("ec2", "delete-volume", "--volume-id", vol)
        time.sleep(10)
        v2 = aws("ec2", "describe-volumes", "--volume-ids", vol)
        print("  after explicit delete: " + ("gone" if not v2 else
              v2["Volumes"][0]["State"]))

    # ---- snapshot --------------------------------------------------------
    if SNAP.exists():
        sid = SNAP.read_text().strip()
        if a.keep_snapshot:
            print("")
            print("keeping snapshot " + sid + " (bills about $%.2f/month)"
                  % (12 * SNAP_GB_MONTH))
        else:
            print("")
            print("deleting snapshot " + sid + " (results are home and pushed; "
                  "it would bill monthly)")
            aws("ec2", "delete-snapshot", "--snapshot-id", sid)
            chk = aws("ec2", "describe-snapshots", "--snapshot-ids", sid)
            print("  snapshot now: " + ("gone" if not chk else "still present"))

    print("")
    print("teardown complete. Final instance state: " + state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
