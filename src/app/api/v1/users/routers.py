from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.sessions import get_db_session
from src.app.schemas.users_schemas import (
    Token,
    UserAuth,
    UserRegisterResponse,
    UserRegistration,
)
from src.app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
)
from src.tasks.email import send_email_task

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration, session: AsyncSession = Depends(get_db_session)
) -> UserRegisterResponse:
    await create_user(user_data, session)
    send_email_task.delay(user_data.email)
    return UserRegisterResponse(message="Вы успешно зарегистрированы!")


@router.post("/login/", response_model=Token)
async def auth_user(
    response: Response,
    user_data: UserAuth,
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    check = await authenticate_user(
        session=session, email=user_data.email, password=user_data.password
    )
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return Token(access_token=access_token, refresh_token=None)


@router.post("/logout/")
async def logout_user(response: Response) -> None:
    response.delete_cookie(key="users_access_token")
