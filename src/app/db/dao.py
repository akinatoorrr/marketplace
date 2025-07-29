from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Category, DeletedPost, Post, User

MAX_PAGE_SIZE = 100


class BaseDAO:
    model = None

    @classmethod
    async def add(
        cls, session: AsyncSession, **values: dict[str, Any]
    ) -> User | Post | Category:
        """Создаёт новый объект"""
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.commit()
        return new_instance


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_or_none(
        cls, session: AsyncSession, **filter_param: dict[str, Any] | int
    ) -> User | None:
        """Возвращает пользователя или None"""
        query = select(User).filter_by(**filter_param)
        result = await session.execute(query)
        return result.scalar_one_or_none()


class BlogDAO(BaseDAO):
    model = None

    @classmethod
    async def get_list(
        cls,
        session: AsyncSession,
        category_id: int | None,
        page_size: int | None,
        page_number: int | None,
    ) -> list[Post] | list[Category]:
        """Возвращает список"""
        page_size = min(page_size or 10, MAX_PAGE_SIZE)
        page_number = page_number or 1
        query = select(cls.model)
        if category_id:
            query = query.where(cls.model.category_id == category_id)
        query = query.limit(page_size).offset((page_number - 1) * page_size)
        result = await session.execute(query)
        return result.scalars().all()


class PostDAO(BlogDAO):
    model = Post
    soft_delete_to = DeletedPost

    @classmethod
    async def edit_post(
        cls, session: AsyncSession, post_id: int, **values: dict[str, Any] | str
    ) -> Post | None:
        """Изменение поста"""
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
    async def soft_delete_post(
        cls, session: AsyncSession, post_id: int
    ) -> dict[str, Any]:
        """Мягкое удаление поста с переносом его
        в отдельную таблицу и удалением из основной
        """
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
        await session.delete(post)
        await session.commit()
        return {"message": f"Пост с id={post.id} успешно удалён"}

    @classmethod
    async def search_posts(
        cls,
        session: AsyncSession,
        search_query: str,
        page_size: int | None,
        page_number: int | None,
    ) -> list[Post]:
        page_size = min(page_size or 10, MAX_PAGE_SIZE)
        page_number = page_number or 1
        # Используем plainto_tsquery для "простой" обработки поисковой строки
        ts_query = func.plainto_tsquery("russian", search_query)
        query = (
            select(cls.model)
            .where(cls.model.tsv.op("@@")(ts_query))
            .limit(page_size)
            .offset((page_number - 1) * page_size)
        )
        result = await session.execute(query)
        return result.scalars().all()


class CategoryDAO(BlogDAO):
    model = Category
