from fastapi import APIRouter, FastAPI

from src.app.api.v1.blog.category_routers import category_router
from src.app.api.v1.blog.post_routers import post_router
from src.app.api.v1.users.routers import router as user_router

app = FastAPI()

healthcheck_router = APIRouter(prefix="/health")


@healthcheck_router.get("/", summary="Эндпоинт для healthcheck")
async def healthcheck() -> dict:
    return {"status": "ok"}


app.include_router(user_router)
app.include_router(post_router)
app.include_router(category_router)
app.include_router(healthcheck_router)
