from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from src.app.core.config import settings
from src.app.db.dao import UsersDAO
from src.app.db.models import User

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


async def get_current_user(token: str = Depends(get_token)) -> User:
    """Декодирует токен и возвращает текущего пользователя"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
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

    expire_time = datetime.fromtimestamp(expire, tz=UTC)
    if expire_time < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Токен истек")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="ID пользователя не найден в токене"
        )

    user = await UsersDAO.get_user_or_none(id=int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return user


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
