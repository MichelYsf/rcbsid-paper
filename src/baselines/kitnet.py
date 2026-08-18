from __future__ import annotations
import numpy as np
from .common import as_array, RunningStandardizer, BaselineDependencyError
from .score_utils import scalar_score


class _NumpyAutoencoder:
    def __init__(self, n_features: int, hidden: int, seed: int = 42, lr: float = 1e-3):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 0.05, size=(n_features, hidden))
        self.b1 = np.zeros(hidden)
        self.W2 = rng.normal(0, 0.05, size=(hidden, n_features))
        self.b2 = np.zeros(n_features)
        self.lr = lr

    def forward(self, x):
        h = np.tanh(x @ self.W1 + self.b1)
        y = h @ self.W2 + self.b2
        return h, y

    def score(self, x) -> float:
        _, y = self.forward(x)
        return float(np.mean((x - y) ** 2))

    def learn(self, x) -> None:
        h, y = self.forward(x)
        err = y - x
        dW2 = np.outer(h, err)
        db2 = err
        dh = (err @ self.W2.T) * (1 - h * h)
        dW1 = np.outer(x, dh)
        db1 = dh
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1


class KitNETWrapper:
    """Kitsune/KitNET-style online autoencoder baseline.

    If ymirsky/KitNET-py is available on PYTHONPATH, this wrapper uses it. If
    not, it uses a deterministic shallow online autoencoder fallback with the
    same score_one/learn_one interface so the full pipeline remains executable.
    Final paper results should use the native KitNET implementation and report
    the commit hash in the artifact log.
    """
    def __init__(self, n_features: int, seed: int = 42, max_ae: int = 10, fm_grace: int = 100, ad_grace: int = 200, allow_fallback: bool = True):
        self.uses_fallback = False
        self.native = False
        self.grace = max(1, min(ad_grace, 1000))
        self.i = 0
        self._last_native_score = 0.0
        try:
            import KitNET as kit  # type: ignore
            self.model = kit.KitNET(n_features, max_ae, fm_grace, ad_grace)
            self.native = True
        except Exception as exc:
            if not allow_fallback:
                raise BaselineDependencyError("KitNET requires ymirsky/KitNET-py or a compatible KitNET module on PYTHONPATH. Clone it before publication runs, or enable fallback only for smoke tests.") from exc
            self.uses_fallback = True
            hidden = max(1, min(max_ae, max(2, n_features // 2)))
            self.scaler = RunningStandardizer(n_features)
            self.model = _NumpyAutoencoder(n_features=n_features, hidden=hidden, seed=seed)
            self.err_mean = 0.0
            self.err_m2 = 0.0
            self.err_n = 0

    def _normalize_error(self, err: float) -> float:
        if self.err_n < 30:
            return 0.0
        var = max(self.err_m2 / max(self.err_n - 1, 1), 1e-12)
        z = max(0.0, (err - self.err_mean) / np.sqrt(var))
        return float(z / (1.0 + z))

    def score_one(self, x) -> float:
        """Score the CURRENT observation.

        A7 fix: this previously returned the score cached by the PREVIOUS
        learn_one() call, so every reported KitNET number was shifted by one
        observation. KitNET-py's process(x) is fused (score+update), so it is
        called here and learn_one() becomes a no-op for the same point.
        """
        x = as_array(x)
        if self.native:
            s = self.model.process(x)
            self._last_native_score = scalar_score(s) if s is not None else 0.0
            self._consumed = True
            return float(self._last_native_score)
        z = self.scaler.transform(x)
        err = self.model.score(z)
        return self._normalize_error(err)

    def learn_one(self, x) -> None:
        """No-op when native: score_one() already ran the fused process(x)."""
        x = as_array(x)
        if self.native:
            if getattr(self, "_consumed", False):
                self._consumed = False
                return
            s = self.model.process(x)
            self._last_native_score = scalar_score(s) if s is not None else 0.0
            return
        z = self.scaler.transform(x)
        err = self.model.score(z)
        self.err_n += 1
        delta = err - self.err_mean
        self.err_mean += delta / self.err_n
        self.err_m2 += delta * (err - self.err_mean)
        self.model.learn(z)
        self.scaler.learn_one(x)
        self.i += 1
