"""Lookup access for active Model C reference metadata."""

from app.data.seed import PARAMETER_METADATA, PLANTING_SYSTEMS, RICE_VARIETIES
from app.domain.models import ParameterMetadata, PlantingSystem, RiceVariety


class LookupRepository:
    def list_rice_varieties(self) -> list[RiceVariety]:
        return list(RICE_VARIETIES)

    def list_planting_systems(self) -> list[PlantingSystem]:
        return list(PLANTING_SYSTEMS)

    def get_rice_variety(self, code: str) -> RiceVariety | None:
        return next((item for item in RICE_VARIETIES if item.code == code), None)

    def get_planting_system(self, code: str) -> PlantingSystem | None:
        return next((item for item in PLANTING_SYSTEMS if item.code == code), None)

    def get_parameter_metadata(self) -> dict[str, ParameterMetadata]:
        return dict(PARAMETER_METADATA)


lookup_repository = LookupRepository()
