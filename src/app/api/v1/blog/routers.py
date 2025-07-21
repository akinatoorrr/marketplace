from fastapi import APIRouter, Depends, HTTPException, status

from src.app.api.v1.users.auth import get_current_user
from src.app.db.dao import CategoryDAO, PostDAO
from src.app.schemas.schemas import (
    CategoryCreate,
    CategoryRead,
    PostCreate,
    PostRead,
    PostUpdate,
)

post_router = APIRouter(
    prefix="/posts", tags=["Posts"], dependencies=[Depends(get_current_user)]
)
category_router = APIRouter(
    prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)]
)


@post_router.get("/", summary="Получение списка статей", response_model=list[PostRead])
async def get_post_list():
    return await PostDAO.get_list()


@post_router.post(
    "/",
    summary="Создание статьи",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post_data: PostCreate):
    return await PostDAO.add(**post_data.model_dump())


@post_router.put("/{post_id}", summary="Редактирование статьи", response_model=PostRead)
async def edit_post(post_id: int, edit_data: PostUpdate):
    try:
        updated_post = await PostDAO.edit_post(
            post_id, **edit_data.model_dump(exclude_none=True)
        )
        return updated_post
    except ValueError as err:
        raise HTTPException(
            status_code=404, detail="Пост с таким id не найден"
        ) from err


@post_router.delete("/{post_id}", summary="Удаление статьи")
async def delete_post(post_id: int):
    try:
        return await PostDAO.soft_delete_post(post_id)
    except ValueError as err:
        raise HTTPException(
            status_code=404, detail="Пост с таким id не найден"
        ) from err


@category_router.get(
    "/", summary="Получение списка категорий", response_model=list[CategoryRead]
)
async def get_category_list():
    return await CategoryDAO.get_list()


@category_router.post(
    "/",
    summary="Создание категории",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category_data: CategoryCreate):
    return await CategoryDAO.add(**category_data.model_dump())
