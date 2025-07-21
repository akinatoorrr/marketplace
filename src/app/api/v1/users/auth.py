from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from src.app.core.config import settings
from src.app.db.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Функция принимает пароль в виде строки
    и возвращает его безопасный хэш.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Функция принимает обычный пароль и его хэш,
    возвращая True, если пароль соответствует хэшу
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Функция создаёт и возвращает JWT-токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encode_jwt


def get_token(request: Request) -> str:
    token = request.cookies.get("users_access_token") or request.headers.get(
        "Authorization"
    )
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден!")
    if token.startswith("Bearer "):
        token = token[7:]
    return token


async def authenticate_user(email: EmailStr, password: str):
    """Функция принимает почту и пароль
    и проверяет, есть ли такой пользователь в базе
    """
    user = await UsersDAO.get_user_or_none(email=email)
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.password)
        is False
    ):
        return None
    return user
