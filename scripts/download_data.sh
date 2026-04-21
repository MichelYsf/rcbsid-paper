#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/raw/unsw_nb15 data/raw/cicids2017_engelen data/raw/litnet2020
cat <<'INNERTXT'
Manual dataset download required.

UNSW-NB15:
  https://research.unsw.edu.au/projects/unsw-nb15-dataset
  Place CSV files under data/raw/unsw_nb15/

CICIDS2017 Engelen-corrected:
  https://intrusion-detection.distrinet-research.be/WTMC2021/tools_datasets.html
  Place corrected regenerated CSV files under data/raw/cicids2017_engelen/

LITNET-2020:
  https://www.mdpi.com/2079-9292/9/5/800
  Place CSV files under data/raw/litnet2020/
INNERTXT
