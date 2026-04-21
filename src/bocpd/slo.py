from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Iterable

MINUTES_PER_30_DAY_MONTH = 30 * 24 * 60

def error_budget_minutes(slo: float, period_minutes: int = MINUTES_PER_30_DAY_MONTH) -> float:
    if not (0 < slo < 1):
        raise ValueError('slo must be between 0 and 1')
    return (1.0 - slo) * period_minutes

def posterior_threshold(false_positive_cost: float, false_negative_cost: float, incident_prior: float) -> float:
    if false_positive_cost <= 0 or false_negative_cost <= 0:
        raise ValueError('costs must be positive')
    if not (0 < incident_prior < 1):
        raise ValueError('incident_prior must be between 0 and 1')
    numerator = false_positive_cost * (1.0 - incident_prior)
    denominator = numerator + false_negative_cost * incident_prior
    return numerator / denominator

def burn_rate(observed_error_ratio: float, slo: float) -> float:
    return observed_error_ratio / (1.0 - slo)

@dataclass
class BurnRateWindow:
    long_window: int
    short_window: int
    threshold: float

class MultiWindowBurnRateAlert:
    def __init__(self, slo: float, rules: Iterable[BurnRateWindow]):
        self.slo = slo
        self.rules = list(rules)
        self.max_window = max(r.long_window for r in self.rules)
        self.events = deque(maxlen=self.max_window)

    def update(self, budget_event: float) -> bool:
        self.events.append(float(budget_event))
        snapshot = list(self.events)
        for rule in self.rules:
            if len(snapshot) < rule.long_window:
                continue
            long_rate = sum(snapshot[-rule.long_window:]) / rule.long_window
            short_rate = sum(snapshot[-rule.short_window:]) / rule.short_window
            if burn_rate(long_rate, self.slo) > rule.threshold and burn_rate(short_rate, self.slo) > rule.threshold:
                return True
        return False
