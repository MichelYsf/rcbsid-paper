from __future__ import annotations


def available_baselines():
    return {
        'hst': 'river.anomaly.HalfSpaceTrees online baseline',
        'kitnet': 'Kitsune/KitNET online autoencoder ensemble',
        'loda': 'LODA online random projection histogram baseline',
        'xstream': 'xStream streaming baseline',
        'rrcf': 'Robust Random Cut Forest streaming baseline',
        'iforest_asd': 'Streaming Isolation Forest ASD baseline',
        'lof': 'Batch reference only',
        'ecod': 'Batch reference only',
        'copod': 'Batch reference only',
    }


def make_streaming_baseline(name: str, n_features: int, seed: int = 42, allow_fallback: bool = True):
    name = name.lower()
    if name == 'hst':
        from .hst import HalfSpaceTreesWrapper
        return HalfSpaceTreesWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    if name == 'kitnet':
        from .kitnet import KitNETWrapper
        return KitNETWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    if name == 'loda':
        from .loda import LODAWrapper
        return LODAWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    if name == 'xstream':
        from .xstream import XStreamWrapper
        return XStreamWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    if name == 'rrcf':
        from .rrcf import RRCFWrapper
        return RRCFWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    if name == 'iforest_asd':
        from .iforest_asd import IForestASDWrapper
        return IForestASDWrapper(n_features=n_features, seed=seed, allow_fallback=allow_fallback)
    raise KeyError(f'Unknown streaming baseline: {name}')


def score_streaming_model(model, X):
    scores = []
    for row in X:
        scores.append(float(model.score_one(row)))
        model.learn_one(row)
    return scores
