from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.storage import generate_image_key, upload_file
from src.app.db.models import Post
from src.app.db.post_dao import PostDAO


async def create_post_service(
    session: AsyncSession,
    title: str,
    text: str,
    category_id: int,
    image: UploadFile | None,
) -> Post:
    image_key: str | None = None

    if image and image.filename and image.content_type:
        image_key = generate_image_key("images/posts", image.filename)
        await image.seek(0)
        upload_file(image.file, image_key, image.content_type)

    post_data: dict[str, Any] = {
        "title": title,
        "text": text,
        "category_id": category_id,
        "image_key": image_key,
    }
    return await PostDAO.add(session, **post_data)
