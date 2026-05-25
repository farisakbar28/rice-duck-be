from pydantic import BaseModel


class RiceVarietyResponse(BaseModel):
    id: str
    name: str
    hst_entry: int
    hst_heading: int
    plant_height_category: str
    notes: str


class PlantingSystemResponse(BaseModel):
    id: str
    name: str
    k_max_per_are: float
    f_yield: float
    notes: str


class RiceVarietyListResponse(BaseModel):
    data: list[RiceVarietyResponse]


class PlantingSystemListResponse(BaseModel):
    data: list[PlantingSystemResponse]
