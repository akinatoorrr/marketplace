import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_serializer,
)

from src.app.core.storage import get_file_url


class UserRegistration(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )
    phone_number: str = Field(
        ..., description="Номер телефона в международном формате, начинающийся с '+'"
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r"^\+\d{5,15}$", value):
            raise ValueError(
                'Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр'
            )
        return value


class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )


class BlogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PostBase(BlogSchema):
    title: str = Field(..., min_length=5, max_length=70, description="Название статьи")
    text: str = Field(..., description="Текст статьи")
    category_id: int = Field(..., description="Категория статьи")


class CategoryBase(BlogSchema):
    title: str = Field(..., max_length=70, description="Название категории")


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


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime


class CategoryCreate(CategoryBase):
    pass
