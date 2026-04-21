#!/usr/bin/env bash
set -euo pipefail
python -V
python - <<'INNERPY'
import importlib
mods = ['numpy','pandas','scipy','sklearn','river','yaml']
missing=[]
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as exc:
        missing.append((m,str(exc)))
if missing:
    print(missing)
    raise SystemExit(1)
print('Environment OK')
INNERPY
