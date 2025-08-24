from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.sessions import get_db_session
from src.app.db.users_dao import UsersDAO
from src.app.schemas.users_schemas import UserAuth, UserRegistration
from src.app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from src.celery_app import celery_app

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration, session: AsyncSession = Depends(get_db_session)
) -> dict:
    user = await UsersDAO.get_user_or_none(session, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )
    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    await UsersDAO.add(session, **user_dict)
    await run_in_threadpool(
        lambda: celery_app.send_task(
            "src.tasks.email.send_email_task", args=[user_data.email]
        )
    )
    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(
    response: Response,
    user_data: UserAuth,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    check = await authenticate_user(
        session=session, email=user_data.email, password=user_data.password
    )
    if check is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль"
        )
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": None}


@router.post("/logout/")
async def logout_user(response: Response) -> dict:
    response.delete_cookie(key="users_access_token")
    return {"message": "Пользователь успешно вышел из системы"}
