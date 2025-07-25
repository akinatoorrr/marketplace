from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from src.app.api.v1.users.auth import get_current_user
from src.app.db.dao import CategoryDAO, PostDAO
from src.app.schemas.schemas import (
    CategoryCreate,
    CategoryRead,
    PostRead,
    PostUpdate,
)
from src.app.services.posts import create_post_service

post_router = APIRouter(
    prefix="/posts", tags=["Posts"], dependencies=[Depends(get_current_user)]
)
category_router = APIRouter(
    prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)]
)


@post_router.get("/", summary="Получение списка статей", response_model=list[PostRead])
async def list_posts(
    search: str | None = Query(None, description="Поисковый запрос"),
    category_id: int | None = Query(None, description="ID категории"),
    page_size: int = Query(
        10, ge=1, le=100, description="Размер страницы (по умолчанию 10, максимум 100)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы (по умолчанию 1)"),
):
    if search:
        posts = await PostDAO.search_posts(search, page_size, page_number)
    else:
        posts = await PostDAO.get_list(category_id, page_size, page_number)
    return posts


@post_router.post(
    "/",
    summary="Создание статьи",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    title: str = Form(...),
    text: str = Form(...),
    category_id: int = Form(...),
    image: UploadFile | None = File(None),
):
    # 1. Если есть файл — загружаем его в MinIO
    try:
        new_post = await create_post_service(title, text, category_id, image)
        return new_post
    except Exception as err:
        raise HTTPException(
            status_code=500, detail="Ошибка загрузки изображения"
        ) from err


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
async def get_category_list(
    page_size: int = Query(
        10, ge=1, le=100, description="Размер страницы (по умолчанию 10, максимум 100)"
    ),
    page_number: int = Query(1, ge=1, description="Номер страницы (по умолчанию 1)"),
):
    return await CategoryDAO.get_list(None, page_size, page_number)


@category_router.post(
    "/",
    summary="Создание категории",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category_data: CategoryCreate):
    return await CategoryDAO.add(**category_data.model_dump())
