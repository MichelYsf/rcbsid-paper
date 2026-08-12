#!/usr/bin/env bash
# CALIBURN EC2 bootstrap — Ubuntu 24.04 x86_64, run as ubuntu, non-interactive.
# Installs python3.11 + deps, clones the branch, verifies native baselines,
# rebuilds datasets from the OFFICIAL sources (no UNSW), enforces the
# integrity gates, and leaves the repo ready for the autopilot runner.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev git unzip build-essential curl

cd "$HOME"
[ -d rcbsid-paper ] || git clone https://github.com/MichelYsf/rcbsid-paper.git
cd rcbsid-paper
git fetch origin
git checkout exp/prevalence-and-tuning
git pull --ff-only origin exp/prevalence-and-tuning

python3.11 -m venv .venv
.venv/bin/pip -q install --upgrade pip
.venv/bin/pip -q install -r requirements.txt
bash scripts/setup_kitnet_py.sh
export PYTHONPATH="$PWD/external/KitNET-py"
.venv/bin/python scripts/verify_native_baselines.py

# ---- datasets from official sources (CICIDS Engelen-improved + LITNET three attack sets)
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
for f in data/downloads/BLASTER_WORM_FLOWS.zip data/downloads/BLASTER_WORM_v2_ATTACKERS_ONLY.zip \
         data/downloads/UDP_FLOOD_FLOWS.zip data/downloads/UDP_FLOOD_v2_ATTACKERS_ONLY.zip \
         data/downloads/SPAM_FLOWS.zip data/downloads/SPAM_v2_ATTACKERS_ONLY.zip; do
  unzip -o -q "$f" -d /tmp/litnet_unzipped/
done

# ---- integrity gates: byte sizes, exactly-six LITNET files, Attempted Category fingerprint
python3 - <<'EOF'
from pathlib import Path
exp = {
 'CICIDS2017_improved.zip': 343549013,
 'BLASTER_WORM_FLOWS.zip': 74424976, 'BLASTER_WORM_v2_ATTACKERS_ONLY.zip': 314485,
 'UDP_FLOOD_FLOWS.zip': 17491937, 'UDP_FLOOD_v2_ATTACKERS_ONLY.zip': 1766862,
 'SPAM_FLOWS.zip': 42726018, 'SPAM_v2_ATTACKERS_ONLY.zip': 15758}
for name, size in exp.items():
    actual = Path('data/downloads', name).stat().st_size
    assert actual == size, f'{name}: size {actual} != expected {size}'
six = sorted(p.name for p in Path('/tmp/litnet_unzipped').glob('*.csv'))
assert six == ['BLASTER_WORM_v2.csv','BLASTER_WORM_v2_ATTACKERS_FLOWS.csv',
               'SPAM_v2.csv','SPAM_v2_ATTACKERS_FLOWS.csv',
               'UDP_FLOOD_v2.csv','UDP_FLOOD_v2_ATTACKERS_FLOWS.csv'], six
for day in ('monday','tuesday','wednesday','thursday','friday'):
    header = open(f'data/raw/cicids2017_original/{day}.csv').readline()
    assert 'Attempted Category' in header, f'{day}: Attempted Category fingerprint missing'
print('INTEGRITY GATES PASSED (sizes, six LITNET files, Engelen fingerprint)')
EOF

.venv/bin/python scripts/build_cicids_labeled.py
.venv/bin/python scripts/interleave_cicids.py
.venv/bin/python scripts/build_litnet_labeled.py

python3 - <<'EOF'
import subprocess
for f, n in (('data/raw/cicids2017/cicids2017_labeled.csv', 1_600_001),
             ('data/raw/litnet2020/litnet2020_labeled.csv', 1_500_001)):
    c = int(subprocess.check_output(['wc', '-l', f]).split()[0])
    assert c == n, f'{f}: {c} lines != expected {n}'
print('BUILT-STREAM ROW COUNTS OK (1.6M CICIDS + 1.5M LITNET, +1 header each)')
EOF

git config user.name "MichelYsf"
git config user.email "camich289@gmail.com"
echo BOOTSTRAP_COMPLETE
