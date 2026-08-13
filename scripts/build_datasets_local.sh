#!/usr/bin/env bash
# Canonical local Stage 0 dataset build. USE THIS instead of calling the
# builders by hand.
#
# It exists because the by-hand path on 2026-08-06/08-13 ran the builders but
# skipped scripts/interleave_litnet.py, leaving LITNET as three contiguous
# attack-type blocks. Validation and test became pure `spam` (6 and 132
# attacks), and every LITNET number produced from it was garbage. The
# interleave is mandatory for BOTH datasets, and the health gate below refuses
# to hand over a stream that is still blocked.
set -euo pipefail

PY="${PY:-python}"
cd "$(dirname "$0")/.."

echo "=== CICIDS2017: build + interleave ==="
"$PY" scripts/build_cicids_labeled.py
"$PY" scripts/interleave_cicids.py

echo "=== LITNET-2020: build + interleave (BOTH steps are required) ==="
"$PY" scripts/build_litnet_labeled.py
"$PY" scripts/interleave_litnet.py

echo "=== stream health gate ==="
"$PY" scripts/check_stream_health.py

echo "Datasets built and verified. Safe to run experiments."
