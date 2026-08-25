"""Phase 2: age support classifier -- metadata only, boundaries 20/21/30/31."""

import pytest

from app.domain.models import AgeSupportFlag
from app.engines.r2.config import load_default_config
from app.engines.r2.support import classify_age


@pytest.fixture(scope="module")
def config():
    return load_default_config()


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (1, AgeSupportFlag.CAUTION),
        (20, AgeSupportFlag.CAUTION),
        (21, AgeSupportFlag.SUPPORTED),
        (25, AgeSupportFlag.SUPPORTED),
        (30, AgeSupportFlag.SUPPORTED),
        (31, AgeSupportFlag.OUTSIDE_LOCAL_RANGE),
        (45, AgeSupportFlag.OUTSIDE_LOCAL_RANGE),
    ],
)
def test_age_boundaries(config, age: int, expected: AgeSupportFlag) -> None:
    assert classify_age(age, config) is expected


def test_classifier_is_metadata_only(config) -> None:
    """The result is a bare enum flag -- no numeric payload of any kind."""
    result = classify_age(30, config)
    assert isinstance(result, AgeSupportFlag)
