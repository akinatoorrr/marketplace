from fastapi import FastAPI

from src.app.api.v1.blog.routers import category_router, post_router
from src.app.api.v1.users.routers import router as user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(post_router)
app.include_router(category_router)
