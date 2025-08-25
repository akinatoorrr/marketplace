# src/app/services/auth.py
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.db.models import User
from src.app.db.sessions import get_db_session
from src.app.db.users_dao import UsersDAO
from src.app.schemas.users_schemas import UserRegistration

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = cast(
        str,
        jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM),
    )
    return encode_jwt


def get_token(request: Request) -> str:
    token_any: Any = request.cookies.get("users_access_token") or request.headers.get(
        "Authorization"
    )
    if not token_any:
        raise HTTPException(status_code=401, detail="Токен не найден!")
    token = cast(str, token_any)
    if token.startswith("Bearer "):
        token = token[7:]
    return token


async def get_current_user(
    session: AsyncSession = Depends(get_db_session), token: str = Depends(get_token)
) -> User:
    try:
        payload = cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            ),
        )
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не валиден",
        ) from err

    expire = payload.get("exp")
    if not expire:
        raise HTTPException(
            status_code=401, detail="Отсутствует время истечения токена"
        )

    expire_time = datetime.fromtimestamp(cast(float, expire), tz=UTC)
    if expire_time < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Токен истек")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="ID пользователя не найден в токене"
        )

    user = await UsersDAO.get_user_or_none(session, id=int(cast(int, user_id)))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


async def authenticate_user(
    email: EmailStr,
    password: str,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    user = await UsersDAO.get_user_or_none(session, email=email)
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.password)
        is False
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль"
        )
    return user


async def create_user(user_data: UserRegistration, session: AsyncSession) -> None:
    user = await UsersDAO.get_user_or_none(session, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )
    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    await UsersDAO.add(session, **user_dict)
