from pydantic import BaseModel, Field
from datetime import date


class PlaceBase(BaseModel):
    external_id: int
    notes: str | None = None


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    is_visited: bool | None = None
    notes: str | None = None


class PlaceResponse(PlaceBase):
    id: int
    project_id: int
    is_visited: bool

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    start_date: date | None = None


class ProjectCreate(ProjectBase):
    external_places: list[int] | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: date | None = None


class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool
    places: list[PlaceResponse] = []

    class Config:
        from_attributes = True
