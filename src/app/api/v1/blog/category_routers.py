from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.category_dao import CategoryDAO
from src.app.db.models import Category
from src.app.db.sessions import get_db_session
from src.app.schemas.category_schemas import CategoryCreate, CategoryRead
from src.app.services.auth import get_current_user

category_router = APIRouter(
    prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)]
)


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
