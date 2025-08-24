from datetime import datetime

from pydantic import (
    Field,
)

from .base_schemas import BlogSchema


class CategoryBase(BlogSchema):
    title: str = Field(..., max_length=70, description="Название категории")


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime


class CategoryCreate(CategoryBase):
    pass
