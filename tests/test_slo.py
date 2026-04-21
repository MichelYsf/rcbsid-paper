from src.bocpd.slo import error_budget_minutes, posterior_threshold

def test_error_budget_999():
    assert abs(error_budget_minutes(0.999) - 43.2) < 1e-9

def test_threshold_example():
    assert round(posterior_threshold(1, 10, 0.01), 2) == 0.91
