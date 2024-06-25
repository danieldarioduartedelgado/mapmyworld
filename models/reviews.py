import uuid
from pydantic import BaseModel, Field
from typing import Optional

class Review(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    id_location: str
    location_name: str
    id_category: str
    category_name: str
    register_date: str
    update_date: str
    comments: str = Field(max_length=50)

class ReviewDto(BaseModel):
    id_location: str
    id_category: str
    comments: str = Field(max_length=50)
    
