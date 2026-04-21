#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
mkdir -p external
if [ ! -d external/KitNET-py ]; then
  git clone https://github.com/ymirsky/KitNET-py external/KitNET-py
else
  echo "external/KitNET-py already exists; pulling latest."
  git -C external/KitNET-py pull --ff-only || true
fi

# Common compatibility patches for old NumPy aliases.
# These patches are idempotent and harmless if the aliases are not present.
find external/KitNET-py -type f -name '*.py' -print0 | xargs -0 sed -i \
  -e 's/np\.int\b/int/g' \
  -e 's/np\.float\b/float/g' \
  -e 's/np\.bool\b/bool/g'

cat <<MSG

KitNET-py is installed under:
  $ROOT/external/KitNET-py

Use this before verification and real runs:
  export PYTHONPATH="$ROOT/external/KitNET-py:\$PYTHONPATH"

Then run:
  python scripts/verify_native_baselines.py
MSG
