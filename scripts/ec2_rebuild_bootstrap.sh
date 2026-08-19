#!/usr/bin/env bash
# EC2 bootstrap for the S4 construction contrast (honest rebuild).
#
# Rebuilds the natural-order streams ON THE INSTANCE and verifies every
# SHA-256 against the sidecars committed from the laptop. A mismatch means the
# instance is not evaluating the same data the paper will describe, so it is a
# HALT, not a warning.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev git unzip build-essential curl

cd "$HOME"
[ -d rcbsid-paper ] || git clone https://github.com/MichelYsf/rcbsid-paper.git
cd rcbsid-paper
git fetch origin
git checkout rebuild/honest-v1
git pull --ff-only origin rebuild/honest-v1

python3.11 -m venv .venv
.venv/bin/pip -q install --upgrade pip
.venv/bin/pip -q install -r requirements.txt
bash scripts/setup_kitnet_py.sh
export PYTHONPATH="$PWD/external/KitNET-py"
.venv/bin/python scripts/verify_native_baselines.py

# ---- source data ---------------------------------------------------------
mkdir -p data/downloads data/raw/cicids2017_original /tmp/litnet_unzipped
cd data/downloads
[ -s CICIDS2017_improved.zip ] || curl -fSL --retry 3 --retry-delay 5 -o CICIDS2017_improved.zip \
  "https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/CICIDS2017_improved.zip"
for f in BLASTER_WORM_FLOWS.zip BLASTER_WORM_v2_ATTACKERS_ONLY.zip \
         UDP_FLOOD_FLOWS.zip UDP_FLOOD_v2_ATTACKERS_ONLY.zip \
         SPAM_FLOWS.zip SPAM_v2_ATTACKERS_ONLY.zip; do
  [ -s "$f" ] || curl -fsSL --retry 3 --retry-delay 5 -o "$f" \
    "https://raw.githubusercontent.com/Grigaliunas/electronics9050800/main/dataset/$f"
done
cd "$HOME/rcbsid-paper"
unzip -o -q data/downloads/CICIDS2017_improved.zip -d data/raw/cicids2017_original/
for f in data/downloads/*FLOWS.zip data/downloads/*ATTACKERS_ONLY.zip; do
  unzip -o -q "$f" -d /tmp/litnet_unzipped/
done

# ---- rebuild labeled streams, then the natural-order streams -------------
.venv/bin/python scripts/build_cicids_labeled.py
.venv/bin/python scripts/interleave_cicids.py
.venv/bin/python scripts/build_litnet_labeled.py
.venv/bin/python scripts/interleave_litnet.py
.venv/bin/python scripts/check_stream_health.py
.venv/bin/python scripts/build_natural_streams.py

# ---- SHA-256 GATE: identical bytes, or halt -----------------------------
.venv/bin/python - <<'EOF'
import hashlib, sys
from pathlib import Path

nat = Path("data/raw/natural")
exp_file = nat / "EXPECTED_SHA256.txt"
if not exp_file.exists():
    print("SHA GATE FAILED: EXPECTED_SHA256.txt is missing; nothing to verify against")
    sys.exit(1)

expected = {}
for line in exp_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    digest, name = line.split()[0], line.split()[-1]
    expected[name] = digest

bad, checked = [], 0
for name, exp in sorted(expected.items()):
    target = nat / name
    if not target.exists():
        bad.append((name, exp, "FILE ABSENT"))
        continue
    h = hashlib.sha256()
    with open(target, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    checked += 1
    print(f"  {'OK' if got == exp else 'MISMATCH':9} {name}  {got[:16]}")
    if got != exp:
        bad.append((name, exp, got))

if checked == 0:
    print("SHA GATE FAILED: no streams were verified")
    sys.exit(1)
if bad:
    print("SHA GATE FAILED - the instance is not evaluating the committed data:")
    for n, e, g in bad:
        print("  " + n + " expected " + e + " got " + g)
    sys.exit(1)
print("SHA GATE PASSED - " + str(checked) + " stream(s) byte-identical to the committed expectation")
EOF

git config user.name "MichelYsf"
git config user.email "camich289@gmail.com"
echo REBUILD_BOOTSTRAP_COMPLETE
