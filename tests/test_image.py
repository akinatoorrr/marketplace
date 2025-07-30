import io
import re
from unittest.mock import patch

import pytest

from src.app.core.config import settings
from src.app.core.storage import generate_image_key

from .utils import unique_blog_title


@pytest.mark.asyncio
async def test_generate_image_key_preserves_extension():
    """
    Проверяет, что:
    - используется переданный префикс
    - расширение приводится к нижнему регистру
    - UUID валиден
    - структура ключа соответствует {prefix}/{uuid}.{ext}
    """
    prefix = "images/test"
    filename = "picture.PNG"

    key = generate_image_key(prefix, filename)

    # Проверка: путь начинается с правильного префикса
    assert key.startswith(f"{prefix}/"), f"Неверный префикс в ключе: {key}"

    # Отделяем имя файла (uuid.ext) от префикса
    key_suffix = key[len(prefix) + 1 :]  # +1 — слэш между prefix и именем
    uuid_str, ext = key_suffix.rsplit(".", 1)

    # Проверка: расширение приведено к нижнему регистру
    assert ext == "png", f"Расширение должно быть приведено к нижнему регистру: {ext}"

    # Проверка: UUID соответствует формату UUID4
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    assert uuid_pattern.match(uuid_str), f"UUID не соответствует формату: {uuid_str}"


def test_generate_image_key_raises_on_no_extension():
    with pytest.raises(ValueError, match="отсутствует расширение"):
        generate_image_key("images/test", "file_without_dot")


@pytest.mark.asyncio
@patch("src.app.core.storage.s3_client.put_object")
async def test_create_post_upload_image(
    mock_put, client, auth_headers, category_for_post
):
    """
    Проверяем, что при POST /posts:
     - вызывается put_object с правильными параметрами
     - в ответе есть image_key и image_url
    """
    # 1. Подготовка "файла"
    fake_bytes = b"\x89PNG\r\n\x1a\n..."
    file_obj = io.BytesIO(fake_bytes)  # file-like object
    file_obj.name = "test.png"  # именованный файл
    file_obj.seek(0)

    # 2. Выполняем POST-запрос
    data = {
        "title": unique_blog_title(),
        "text": "Test test text",
        "category_id": category_for_post["id"],
    }
    files = {"image": ("test.png", file_obj, "image/png")}

    response = await client.post("/posts/", data=data, files=files)

    # 3. Проверяем HTTP-статус
    assert response.status_code == 201

    payload = response.json()
    # 4. Проверяем, что image_key есть и непустой
    assert "image_key" in payload
    assert payload["image_key"].startswith("images/posts/")

    # 5. Проверяем, что URL корректно собран
    expected_url = (
        f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{payload['image_key']}"
    )
    assert payload["image_url"] == expected_url

    # 6. Удостоверимся, что s3_client.put_object вызван
    mock_put.assert_called_once()
    called_args = mock_put.call_args.kwargs
    assert called_args["Bucket"] == settings.MINIO_BUCKET
    assert called_args["Key"] == payload["image_key"]
    assert called_args["Body"] == fake_bytes
    assert called_args["ContentType"] == "image/png"
