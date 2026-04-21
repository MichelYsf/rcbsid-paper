from __future__ import annotations
import numpy as np

def detection_latencies(y_true, y_pred):
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    latencies = []
    in_attack = False
    start = 0
    detected = False
    for i, y in enumerate(y_true):
        if y == 1 and not in_attack:
            in_attack = True
            start = i
            detected = False
        if in_attack and y_pred[i] == 1 and not detected:
            latencies.append(i - start)
            detected = True
        if y == 0 and in_attack:
            if not detected:
                latencies.append(np.nan)
            in_attack = False
    return np.asarray(latencies, dtype=float)

def latency_summary(latencies):
    finite = np.asarray(latencies, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) == 0:
        return {'latency_mean': np.nan, 'latency_p50': np.nan, 'latency_p95': np.nan, 'latency_p99': np.nan}
    return {'latency_mean': float(np.mean(finite)), 'latency_p50': float(np.percentile(finite, 50)), 'latency_p95': float(np.percentile(finite, 95)), 'latency_p99': float(np.percentile(finite, 99))}
