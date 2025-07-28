import uuid

from src.app.core.config import settings
from src.app.core.minio_client import s3_client
from src.app.db.dao import PostDAO


async def create_post_service(session, title, text, category_id, image):
    image_key = None
    if image:
        ext = image.filename.split(".")[-1]
        image_key = f"images/posts/{uuid.uuid4()}.{ext}"
        contents = await image.read()
        s3_client.put_object(
            Bucket=settings.MINIO_BUCKET,
            Key=image_key,
            Body=contents,
            ContentType=image.content_type,
        )
    post_data = {
        "title": title,
        "text": text,
        "category_id": category_id,
        "image_key": image_key,
    }
    return await PostDAO.add(session, **post_data)
