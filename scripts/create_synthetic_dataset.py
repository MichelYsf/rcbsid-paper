#!/usr/bin/env python
from pathlib import Path
import numpy as np
import pandas as pd

out = Path('data/raw/synthetic_mean_shift')
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)
segments = [
    (rng.normal(0, 1, size=(700, 3)), 0),
    (rng.normal(3, 1, size=(120, 3)), 1),
    (rng.normal(0, 1, size=(160, 3)), 0),
    (rng.normal(3, 1, size=(120, 3)), 1),
    (rng.normal(0, 1, size=(100, 3)), 0),
]
X = np.vstack([s[0] for s in segments])
y = np.concatenate([np.full(len(s[0]), s[1], dtype=int) for s in segments])
df = pd.DataFrame(X, columns=['f0', 'f1', 'f2'])
df['label'] = y
df.to_csv(out / 'synthetic.csv', index=False)
print(out / 'synthetic.csv')
