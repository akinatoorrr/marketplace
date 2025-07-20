from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .models import User
from .sessions import async_session_maker


class UsersDAO:
    @classmethod
    async def create_user(cls, **values):
        async with async_session_maker() as session:
            async with session.begin():
                new_instance = User(**values)
                session.add(new_instance)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return new_instance

    @classmethod
    async def get_user_or_none(cls, **filter_param):
        async with async_session_maker() as session:
            query = select(User).filter_by(**filter_param)
            result = await session.execute(query)
            return result.scalar_one_or_none()
