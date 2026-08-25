"""Seed-backed lookup access for R2 domain structures.

Pattern unchanged from the pre-R2 repository (normalization + module-level
singleton); the data behind it is now the R2 seed registry
(``app.data.seed``). Legacy ``get_constants`` / ``get_parameter_metadata``
accessors are gone: R2 code consumes the versioned parameter registry via
``get_parameter_registry`` / ``get_parameter``.
"""

from app.data.seed import PARAMETER_REGISTRY, PLANTING_SYSTEMS, RICE_VARIETIES
from app.domain.models import ParameterMetadata, PlantingSystem, RiceVariety


class LookupRepository:
    def list_rice_varieties(self) -> list[RiceVariety]:
        return list(RICE_VARIETIES)

    def get_rice_variety(self, code: str) -> RiceVariety | None:
        normalized = code.strip().lower()
        return next((item for item in RICE_VARIETIES if item.code == normalized), None)

    def list_planting_systems(self) -> list[PlantingSystem]:
        return list(PLANTING_SYSTEMS)

    def get_planting_system(self, code: str) -> PlantingSystem | None:
        normalized = code.strip().lower()
        return next((item for item in PLANTING_SYSTEMS if item.code == normalized), None)

    def get_parameter_registry(self) -> dict[str, ParameterMetadata]:
        return dict(PARAMETER_REGISTRY)

    def get_parameter(self, key: str) -> ParameterMetadata | None:
        return PARAMETER_REGISTRY.get(key)


lookup_repository = LookupRepository()
