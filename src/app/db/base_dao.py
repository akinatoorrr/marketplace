from typing import Any, Protocol, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
