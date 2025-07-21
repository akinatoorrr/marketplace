import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegistration(BaseModel):
    """Схема для регистрации пользователей"""

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
    """Схема для авторизации пользователей"""

    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )


class BlogSchema(BaseModel):
    """Базовая схема для работы с БД"""

    model_config = ConfigDict(from_attributes=True)


class PostBase(BlogSchema):
    """Базовая схема для чтения постов"""

    title: str = Field(..., min_length=5, max_length=70, description="Название статьи")
    text: str = Field(..., description="Текст статьи")
    category_id: int = Field(..., description="Категория статьи")


class CategoryBase(BlogSchema):
    """Базовая схема для чтения категорий"""

    title: str = Field(..., max_length=70, description="Название категории")


class PostRead(PostBase):
    """Схема для ответа на get постов"""

    id: int
    created_at: datetime
    updated_at: datetime


class PostCreate(PostBase):
    """Схема для создания постов"""

    pass


class PostUpdate(BlogSchema):
    """Схема для обновления постов"""

    title: str | None = Field(None, min_length=5, max_length=70)
    text: str | None = Field(None)
    category_id: int | None = Field(None)


class CategoryRead(CategoryBase):
    """Схема для ответа на get категорийй"""

    id: int
    created_at: datetime
    updated_at: datetime


class CategoryCreate(CategoryBase):
    """Схема для создания категорий"""

    pass
