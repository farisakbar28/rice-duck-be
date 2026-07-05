import pytest
from app.engines.formula_engine import compute_penalty_rate
from app.data.seed import DSS_CONSTANTS

def test_penalty_rate_safe():
    rate = compute_penalty_rate(2.14, 3.0, DSS_CONSTANTS)
    assert rate == 0.0

def test_penalty_rate_penalty():
    rate = compute_penalty_rate(4.0, 3.0, DSS_CONSTANTS)
    assert round(rate, 4) == 0.1667

def test_penalty_rate_max():
    rate = compute_penalty_rate(100.0, 3.0, DSS_CONSTANTS)
    assert rate == 1.0
