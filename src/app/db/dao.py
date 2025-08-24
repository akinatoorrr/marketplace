from typing import Any, Protocol, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Category, DeletedPost, Post, User

MAX_PAGE_SIZE = 100


class ORMModel(Protocol):
    """Минимальный контракт для ORM-моделей, используемый в DAO."""

    id: int


class HasCategory(Protocol):
    """Модели с полем category_id (для BlogDAO)."""

    category_id: int


class CategorizedModel(ORMModel, HasCategory):
    """Комбинация ORMModel + HasCategory."""

    ...


T = TypeVar("T", bound=ORMModel)
TCat = TypeVar("TCat", bound=CategorizedModel)


class BaseDAO[T: ORMModel]:
    model: type[T]

    @classmethod
    async def add(cls, session: AsyncSession, **values: Any) -> T:
        new_instance = cast(T, cls.model(**values))
        session.add(new_instance)
        await session.commit()
        return new_instance


class UsersDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_user_or_none(
        cls, session: AsyncSession, **filter_param: Any
    ) -> User | None:
        query = select(User).filter_by(**filter_param)
        result = await session.execute(query)
        return cast(User | None, result.scalar_one_or_none())


class BlogDAO[TCat: CategorizedModel](BaseDAO[TCat]):
    model: type[TCat]

    @classmethod
    async def get_list(
        cls,
        session: AsyncSession,
        category_id: int | None = None,
        page_size: int | None = 10,
        page_number: int | None = 1,
    ) -> list[TCat]:
        page_size = min(page_size or 10, MAX_PAGE_SIZE)
        page_number = page_number or 1
        query = select(cls.model)
        if category_id is not None:
            query = query.where(cls.model.category_id == category_id)
        query = query.limit(page_size).offset((page_number - 1) * page_size)
        result = await session.execute(query)
        return cast(list[TCat], result.scalars().all())


class PostDAO(BlogDAO[Post]):
    model = Post
    soft_delete_to = DeletedPost

    @classmethod
    async def edit_post(
        cls, session: AsyncSession, post_id: int, **values: Any
    ) -> Post | None:
        query = select(cls.model).filter_by(id=post_id)
        result = await session.execute(query)
        post = cast(Post | None, result.scalar_one_or_none())
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
        query = select(cls.model).filter_by(id=post_id)
        result = await session.execute(query)
        post = cast(Post | None, result.scalar_one_or_none())
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


class CategoryDAO(BlogDAO[Category]):
    model = Category
