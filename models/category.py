import uuid
from pydantic import BaseModel, Field
from typing import Optional

class Category(BaseModel):
    id: Optional [str] = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(max_length=50)

class CategoryDto(BaseModel):
    name: str = Field(max_length=50)
