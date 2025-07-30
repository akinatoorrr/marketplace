from src.app.core.storage import generate_image_key, upload_file
from src.app.db.dao import PostDAO


async def create_post_service(session, title, text, category_id, image):
    image_key = None

    if image:
        # 1. Генерация ключа
        image_key = generate_image_key("images/posts", image.filename)

        # 2. Загрузка в MinIO
        await image.seek(0)  # на всякий случай возвращаем курсор в начало
        upload_file(image.file, image_key, image.content_type)

    post_data = {
        "title": title,
        "text": text,
        "category_id": category_id,
        "image_key": image_key,
    }
    return await PostDAO.add(session, **post_data)
