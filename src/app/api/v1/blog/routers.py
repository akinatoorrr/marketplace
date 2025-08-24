from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.category_dao import CategoryDAO
from src.app.db.models import Category, Post
from src.app.db.post_dao import PostDAO
from src.app.db.sessions import get_db_session
from src.app.schemas.category_schemas import CategoryCreate, CategoryRead
from src.app.schemas.post_schemas import PostRead, PostUpdate
from src.app.services.auth import get_current_user
from src.app.services.posts import create_post_service

post_router = APIRouter(
    prefix="/posts", tags=["Posts"], dependencies=[Depends(get_current_user)]
)
category_router = APIRouter(
    prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)]
)


@post_router.get("/", summary="Получение списка статей", response_model=list[PostRead])
async def list_posts(
    session: AsyncSession = Depends(get_db_session),
    search: str | None = Query(None, description="Поисковый запрос"),
    category_id: int | None = Query(None, description="ID категории"),
    page_size: int = Query(
        10, ge=1, le=100, description="Размер страницы (по умолчанию 10, максимум 100)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы (по умолчанию 1)"),
) -> list[Post]:
    if search:
        posts = await PostDAO.search_posts(session, search, page_size, page_number)
    else:
        posts = await PostDAO.get_list(session, category_id, page_size, page_number)
    return posts


@post_router.post(
    "/",
    summary="Создание статьи",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    session: AsyncSession = Depends(get_db_session),
    title: str = Form(...),
    text: str = Form(...),
    category_id: int = Form(...),
    image: UploadFile | None = File(None),
) -> PostRead:
    new_post = await create_post_service(session, title, text, category_id, image)
    return new_post


@post_router.put("/{post_id}", summary="Редактирование статьи", response_model=PostRead)
async def edit_post(
    post_id: int, edit_data: PostUpdate, session: AsyncSession = Depends(get_db_session)
) -> PostRead:
    updated_post = await PostDAO.edit_post(
        session, post_id, **edit_data.model_dump(exclude_none=True)
    )
    return PostRead.model_validate(updated_post)


@post_router.delete("/{post_id}", summary="Удаление статьи")
async def delete_post(
    post_id: int, session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await PostDAO.soft_delete_post(session, post_id)


@category_router.get(
    "/", summary="Получение списка категорий", response_model=list[CategoryRead]
)
async def get_category_list(
    session: AsyncSession = Depends(get_db_session),
    page_size: int = Query(
        10, ge=1, le=100, description="Размер страницы (по умолчанию 10, максимум 100)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы (по умолчанию 1)"),
) -> list[Category]:
    return await CategoryDAO.get_list(session, None, page_size, page_number)


@category_router.post(
    "/",
    summary="Создание категории",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: CategoryCreate, session: AsyncSession = Depends(get_db_session)
) -> CategoryRead:
    return await CategoryDAO.add(session, **category_data.model_dump())
