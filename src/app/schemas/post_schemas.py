from datetime import datetime

from pydantic import (
    Field,
    model_serializer,
)

from src.app.core.storage import get_file_url

from .base_schemas import BlogSchema


class PostBase(BlogSchema):
    title: str = Field(..., min_length=5, max_length=70, description="Название статьи")
    text: str = Field(..., description="Текст статьи")
    category_id: int = Field(..., description="Категория статьи")


class PostRead(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    image_key: str | None = None
    image_url: str | None = None

    @model_serializer(mode="wrap")
    def serializer(self, handler):  # type: ignore
        result = handler(self)
        result["image_url"] = get_file_url(self.image_key) if self.image_key else None
        return result


class PostCreate(PostBase):
    pass


class PostUpdate(BlogSchema):
    title: str | None = Field(None, min_length=5, max_length=70)
    text: str | None = Field(None)
    category_id: int | None = Field(None)
