import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.sessions import Base


class User(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Post(Base):
    title: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("category.id"))
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="posts"
    )
    image_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tsv: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )


class Category(Base):
    title: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")


class DeletedPost(Base):
    original_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(70), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
