from typing import Any

from sqlalchemy import select

from .models import Category, DeletedPost, Post, User
from .sessions import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def add(cls, **values: dict[str, Any]) -> User | Post | Category:
        """Создаёт новый объект"""
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = cls.model(**values)
                session.add(new_instance)
            return new_instance


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_or_none(
        cls, **filter_param: dict[str, Any] | int
    ) -> User | None:
        """Возвращает пользователя или None"""
        async with async_session_maker() as session:
            query = select(User).filter_by(**filter_param)
            result = await session.execute(query)
            return result.scalar_one_or_none()


class BlogDAO(BaseDAO):
    model = None

    @classmethod
    async def get_list(cls) -> list[Post] | list[Category]:
        """Возвращает список"""
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()


class PostDAO(BlogDAO):
    model = Post
    soft_delete_to = DeletedPost

    @classmethod
    async def edit_post(
        cls, post_id: int, **values: dict[str, Any] | str
    ) -> Post | None:
        """Изменение поста"""
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=post_id)
                result = await session.execute(query)
                post = result.scalar_one_or_none()
                if not post:
                    raise ValueError("Post not found")
                for key, value in values.items():
                    if hasattr(post, key):
                        setattr(post, key, value)
        return post

    @classmethod
    async def soft_delete_post(cls, post_id: int) -> dict[str, Any]:
        """Мягкое удаление поста с переносом его
        в отдельную таблицу и удалением из основной
        """
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=post_id)
                result = await session.execute(query)
                post = result.scalar_one_or_none()
                if not post:
                    raise ValueError("Post not found")
                deleted_post = cls.soft_delete_to(
                    original_id=post.id,
                    title=post.title,
                    text=post.text,
                    category_id=post.category_id,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                )
                session.add(deleted_post)
                session.delete(post)
        return {"message": f"Пост с id={post.id} успешно удалён"}


class CategoryDAO(BlogDAO):
    model = Category
