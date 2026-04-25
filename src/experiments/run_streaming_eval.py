from __future__ import annotations
import argparse, json, time, datetime
from pathlib import Path
import yaml
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve

from src.bocpd.slo import posterior_threshold, MultiWindowBurnRateAlert, BurnRateWindow
from src.bocpd.truncated_bocpd import TruncatedBOCPDConfig, TruncatedGaussianBOCPD
from src.baselines.registry import make_streaming_baseline, score_streaming_model
from src.baselines.batch import run_batch_reference
from src.data.loaders import load_dataset_folder, prepare_xy
from src.eval.metrics import classification_metrics, bootstrap_ci, wilcoxon_against_reference, holm_bonferroni
from src.eval.latency import detection_latencies, latency_summary


def _threshold_from_validation(y_val, scores_val, default_threshold: float) -> float:
    y_val = np.asarray(y_val, dtype=int)
    scores_val = np.asarray(scores_val, dtype=float)
    if len(np.unique(y_val)) < 2 or len(scores_val) == 0:
        return float(default_threshold)
    precision, recall, thresholds = precision_recall_curve(y_val, scores_val)
    if len(thresholds) == 0:
        return float(default_threshold)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.nanargmax(f1))])


def _split_chronological(X, y, train_ratio, val_ratio):
    n = len(y)
    i_train = int(n * train_ratio)
    i_val = i_train + int(n * val_ratio)
    return (X[:i_train], y[:i_train]), (X[i_train:i_val], y[i_train:i_val]), (X[i_val:], y[i_val:])


def _make_bocpd(cfg, seed: int):
    # seed is accepted for API symmetry; BOCPD itself is deterministic.
    return TruncatedGaussianBOCPD(TruncatedBOCPDConfig(
        hazard=float(cfg['hazard_grid'][2]),
        max_run_length=int(cfg['run_length_truncation']),
        incident_prior=float(cfg['default_incident_prior']),
    ))


def _score_stream_with_warmup(model, X_warm, X_score):
    for row in X_warm:
        model.update_score(row) if hasattr(model, 'update_score') else model.learn_one(row)
    scores = []
    for row in X_score:
        if hasattr(model, 'update_score'):
            scores.append(float(model.update_score(row)))
        else:
            scores.append(float(model.score_one(row)))
            model.learn_one(row)
    return np.asarray(scores, dtype=float)


def _burn_rate_count(y_true, y_pred, cfg):
    rules_cfg = cfg.get('burn_rate_alerting', {})
    slo = float(rules_cfg.get('slo', 0.999))
    rules = []
    for key in ['page_fast', 'page_slow', 'ticket']:
        if key in rules_cfg:
            r = rules_cfg[key]
            rules.append(BurnRateWindow(
                long_window=max(1, int(r['long_window_minutes'])),
                short_window=max(1, int(r['short_window_minutes'])),
                threshold=float(r['burn_rate']),
            ))
    if not rules:
        return 0
    alert = MultiWindowBurnRateAlert(slo=slo, rules=rules)
    count = 0
    for yt, yp in zip(np.asarray(y_true).astype(int), np.asarray(y_pred).astype(int)):
        # Budget event when the detector either pages unnecessarily or misses an incident.
        budget_event = float((yp == 1 and yt == 0) or (yp == 0 and yt == 1))
        count += int(alert.update(budget_event))
    return count


def _evaluate_row(dataset_name, method, seed, y_test, scores_test, threshold, elapsed, cfg, fallback=False):
    scores_arr = np.asarray(scores_test, dtype=float)
    metrics = classification_metrics(y_test, scores_arr, threshold)
    y_pred = (scores_arr >= threshold).astype(int)
    metrics.update(latency_summary(detection_latencies(y_test, y_pred)))
    metrics['throughput_eps'] = float(len(y_test) / elapsed) if elapsed > 0 else float('nan')
    metrics['burn_rate_alerts'] = _burn_rate_count(y_test, y_pred, cfg)
    metrics['score_std'] = float(np.nanstd(scores_arr)) if len(scores_arr) else float('nan')
    metrics['score_min'] = float(np.nanmin(scores_arr)) if len(scores_arr) else float('nan')
    metrics['score_max'] = float(np.nanmax(scores_arr)) if len(scores_arr) else float('nan')
    metrics['score_finite_frac'] = float(np.isfinite(scores_arr).mean()) if len(scores_arr) else float('nan')
    metrics.update({
        'dataset': dataset_name,
        'method': method,
        'seed': seed,
        'threshold': float(threshold),
        'n_test': int(len(y_test)),
        'uses_fallback': bool(fallback),
    })
    return metrics


def _summaries(rows):
    df = pd.DataFrame([r for r in rows if 'auc_pr' in r])
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    metrics = ['auc_pr', 'auc_roc', 'f1', 'precision', 'recall', 'brier', 'ece_10', 'latency_mean', 'throughput_eps', 'score_std', 'score_min', 'score_max', 'score_finite_frac']
    summary_rows = []
    for (dataset, method), g in df.groupby(['dataset', 'method']):
        row = {'dataset': dataset, 'method': method, 'n_runs': int(len(g))}
        for m in metrics:
            vals = g[m].dropna().to_numpy(dtype=float)
            if len(vals) == 0:
                row[f'{m}_mean'] = np.nan; row[f'{m}_ci_low'] = np.nan; row[f'{m}_ci_high'] = np.nan
            elif len(vals) == 1:
                row[f'{m}_mean'] = float(vals[0]); row[f'{m}_ci_low'] = np.nan; row[f'{m}_ci_high'] = np.nan
            else:
                mean, lo, hi = bootstrap_ci(vals, seed=42)
                row[f'{m}_mean'] = mean; row[f'{m}_ci_low'] = lo; row[f'{m}_ci_high'] = hi
        summary_rows.append(row)
    tests = []
    for dataset, g in df.groupby('dataset'):
        ref = g[g['method'] == 'bocpd_slo'].sort_values('seed')
        pvals = {}
        for method, gm in g.groupby('method'):
            if method == 'bocpd_slo':
                continue
            merged = ref[['seed', 'auc_pr']].merge(gm[['seed', 'auc_pr']], on='seed', suffixes=('_ref', '_base'))
            if len(merged) >= 2:
                try:
                    stat, p = wilcoxon_against_reference(merged['auc_pr_ref'], merged['auc_pr_base'])
                    pvals[method] = p
                    tests.append({'dataset': dataset, 'method': method, 'metric': 'auc_pr', 'wilcoxon_stat': stat, 'p_value': p})
                except Exception as exc:
                    tests.append({'dataset': dataset, 'method': method, 'metric': 'auc_pr', 'error': str(exc)})
        corrected = holm_bonferroni(pvals) if pvals else {}
        for t in tests:
            if t.get('dataset') == dataset and t.get('method') in corrected:
                t['holm_p_value'] = corrected[t['method']]
    return pd.DataFrame(summary_rows), pd.DataFrame(tests)


def run(config_path, output):
    cfg = yaml.safe_load(Path(config_path).read_text())
    allow_fallback_baselines = bool(cfg.get('allow_fallback_baselines', False))
    out = Path(output)
    (out / 'tables').mkdir(parents=True, exist_ok=True)
    rows = []
    default_threshold = posterior_threshold(
        cfg['proposed_method']['default_false_positive_cost'],
        cfg['proposed_method']['default_false_negative_cost'],
        cfg['proposed_method']['default_incident_prior'],
    )

    for dataset in cfg['datasets']:
        try:
            df = load_dataset_folder(dataset['path'], dataset['label_column'])
        except Exception as exc:
            rows.append({'dataset': dataset['name'], 'method': 'SKIPPED', 'reason': str(exc)})
            continue
        # Honor time_column: sort by timestamp before chronological split so the
        # stream truly represents temporal ordering rather than file-read order.
        tcol = dataset.get('time_column')
        if tcol and tcol in df.columns:
            df = df.sort_values(tcol, kind='mergesort').reset_index(drop=True)
            print(f'[runner] sorted {dataset["name"]} by time_column={tcol}; '
                  f'range {df[tcol].iloc[0]} to {df[tcol].iloc[-1]}', flush=True)
        X, y, features = prepare_xy(df, dataset['label_column'])
        if len(y) < 100:
            rows.append({'dataset': dataset['name'], 'method': 'SKIPPED', 'reason': 'dataset has fewer than 100 rows after preprocessing'})
            continue
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = _split_chronological(
            X, y, float(cfg['splits']['train']), float(cfg['splits']['validation'])
        )
        X_warm = np.vstack([X_train, X_val]) if len(X_val) else X_train
        n_features = X.shape[1]

        for seed in cfg.get('random_seeds', [42]):
            # Proposed method.
            model = _make_bocpd(cfg['proposed_method'], int(seed))
            # First score validation after training for possible threshold diagnostics.
            _ = _score_stream_with_warmup(model, X_train, X_val)
            start = time.perf_counter()
            scores_test = _score_stream_with_warmup(model, np.empty((0, n_features)), X_test)
            elapsed = time.perf_counter() - start
            rows.append(_evaluate_row(dataset['name'], 'bocpd_slo', int(seed), y_test, scores_test, default_threshold, elapsed, cfg))

            # Streaming baselines.
            for method in cfg.get('streaming_baselines', []):
                start = time.perf_counter()
                try:
                    model = make_streaming_baseline(method, n_features=n_features, seed=int(seed), allow_fallback=allow_fallback_baselines)
                    # Warm on train, select threshold on validation, then continue to test.
                    for row in X_train:
                        model.learn_one(row)
                    scores_val = []
                    for row in X_val:
                        scores_val.append(float(model.score_one(row)))
                        model.learn_one(row)
                    threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
                    scores_test = np.asarray(score_streaming_model(model, X_test), dtype=float)
                    fallback = bool(getattr(model, 'uses_fallback', False))
                    elapsed = time.perf_counter() - start
                    rows.append(_evaluate_row(dataset['name'], method, int(seed), y_test, scores_test, threshold, elapsed, cfg, fallback=fallback))
                except Exception as exc:
                    rows.append({'dataset': dataset['name'], 'method': method, 'seed': int(seed), 'error': str(exc)})

            # Batch reference baselines.
            X_batch_train = X_train[y_train == 0] if np.any(y_train == 0) else X_train
            X_eval = np.vstack([X_val, X_test])
            for method in cfg.get('batch_reference_baselines', []):
                start = time.perf_counter()
                try:
                    scores_eval = run_batch_reference(method, X_batch_train, X_eval, seed=int(seed))
                    scores_val = scores_eval[:len(X_val)]
                    scores_test = scores_eval[len(X_val):]
                    threshold = _threshold_from_validation(y_val, scores_val, default_threshold)
                    elapsed = time.perf_counter() - start
                    rows.append(_evaluate_row(dataset['name'], f'{method}_batch_ref', int(seed), y_test, scores_test, threshold, elapsed, cfg))
                except Exception as exc:
                    rows.append({'dataset': dataset['name'], 'method': f'{method}_batch_ref', 'seed': int(seed), 'error': str(exc)})

    raw = pd.DataFrame(rows)
    raw.to_csv(out / 'tables' / 'main_metrics_raw.csv', index=False)
    summary, tests = _summaries(rows)
    summary.to_csv(out / 'tables' / 'main_metrics_summary.csv', index=False)
    tests.to_csv(out / 'tables' / 'wilcoxon_tests.csv', index=False)
    (out / 'run_summary.json').write_text(json.dumps({
        'created_utc': datetime.datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
        'config_path': str(config_path),
        'allow_fallback_baselines': allow_fallback_baselines,
        'datasets': [d.get('name') for d in cfg.get('datasets', [])],
        'streaming_baselines': cfg.get('streaming_baselines', []),
        'batch_reference_baselines': cfg.get('batch_reference_baselines', []),
        'n_rows': len(rows),
        'rows': rows,
    }, indent=2, default=str))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    run(a.config, a.output)


if __name__ == '__main__':
    main()
