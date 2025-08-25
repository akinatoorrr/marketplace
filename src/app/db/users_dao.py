from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_dao import BaseDAO
from .models import User


class UsersDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_user_or_none(
        cls, session: AsyncSession, **filter_param: Any
    ) -> User | None:
        query = select(User).filter_by(**filter_param)
        result = await session.execute(query)
        return cast(User | None, result.scalar_one_or_none())
