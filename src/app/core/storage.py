import uuid
from typing import BinaryIO

from src.app.core.config import settings
from src.app.core.minio_client import s3_client


def generate_image_key(prefix: str, filename: str) -> str:
    if "." not in filename:
        raise ValueError("Некорректное имя файла: отсутствует расширение")
    ext = filename.rsplit(".", 1)[-1].lower()
    unique = uuid.uuid4()
    return f"{prefix}/{unique}.{ext}"


def upload_file(file: BinaryIO, key: str, content_type: str) -> None:
    s3_client.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=key,
        Body=file.read(),
        ContentType=content_type,
    )


def get_file_url(key: str) -> str:
    return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{key}"
