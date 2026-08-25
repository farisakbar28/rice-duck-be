"""Shared numerical helpers for the R2 pure-engine package.

Precision policy (docs/01 SSOT, task section 4):
  * All scientific/monetary math uses ``decimal.Decimal``.
  * External floats enter via ``Decimal(str(value))`` -- never binary-float
    conversion.
  * High precision (prec=50) applies to division/square-root contexts;
    there is no mid-calculation rounding. Serialization rounding belongs
    to later orchestration layers, never to these pure engines.

Import-boundary rule (docs/07 section 6): modules in ``app.engines.r2``
must never import the invalidated legacy engine implementations
(``formula_engine`` / ``impact_engine``); the static test suite enforces it.
"""

from __future__ import annotations

from contextlib import contextmanager
from decimal import Decimal, localcontext
from typing import Iterator

DEFAULT_PRECISION = 50


def to_decimal(value: int | float | str | Decimal) -> Decimal:
    """Convert an external numeric value to Decimal via its string form."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@contextmanager
def high_precision(prec: int = DEFAULT_PRECISION) -> Iterator[None]:
    """Deterministic high-precision context for division / sqrt steps."""

    with localcontext() as ctx:
        ctx.prec = prec
        yield
