import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.app.db.sessions import Base


class User(Base):
    username = Column(String(50), unique=True, nullable=False)
    email =Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)


class Post(Base):
    title = Column(String(70), unique=True, nullable=False)
    text = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    category = relationship("Category", back_populates="posts")
    # image = Column()
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.datetime.now())

class Category(Base):
    title = Column(String(25), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    posts = relationship("Post", back_populates="category")

class DeletedPost(Base):
    original_id = Column(Integer, nullable=False)
    title = Column(String(70), nullable=False)
    text = Column(Text, nullable=False)
    category_id = Column(Integer, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, default=datetime.datetime.now)