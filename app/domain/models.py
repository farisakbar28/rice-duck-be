"""Current A+C domain types and isolated legacy persistence records."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RiceVariety:
    """Lookup label only; variety never modifies the frozen C0 yield."""
    code: str
    label: str
    risk_note: str
    status: str


@dataclass(frozen=True)
class PlantingSystem:
    """Current density recommendation boundaries, not yield coefficients."""
    code: str
    label: str
    recommended_density_min_are: float
    recommended_density_max_are: float
    note: str


@dataclass(frozen=True)
class ParameterMetadata:
    value: Any
    unit: str
    source: str
    status: str
    note: str
    minimum: float | int | None = None
    maximum: float | int | None = None


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class LegacySimulationHistoryRow:
    """Physical v1-v3 storage record; never returned by the current A+C API."""
    id: str
    user_id: str
    schema_version: int
    payload: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
