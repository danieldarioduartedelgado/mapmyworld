import uuid
from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel):
    id: Optional [str] = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(max_length=50)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class LocationDto(BaseModel):
    name: str = Field(max_length=50)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
