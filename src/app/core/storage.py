import uuid
from typing import BinaryIO

from src.app.core.config import settings
from src.app.core.minio_client import s3_client


def generate_image_key(prefix: str, filename: str) -> str:
    """
    Генерирует уникальный ключ для объекта в бакете.
    prefix: "images/posts"
    filename: оригинальное имя файла для получения расширения.
    """
    if "." not in filename:
        raise ValueError("Некорректное имя файла: отсутствует расширение")
    ext = filename.rsplit(".", 1)[
        -1
    ].lower()  # получаем расширение после последней точки
    unique = uuid.uuid4()  # генерируем UUID4
    return f"{prefix}/{unique}.{ext}"


def upload_file(file: BinaryIO, key: str, content_type: str) -> None:
    """
    Загружает байты файла в S3/MinIO.
    file: объект, из которого .read() возвращает байты
    key: куда сохранить внутри бакета
    content_type: MIME-тип (например, "image/png")
    """
    s3_client.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=key,
        Body=file.read(),  # читаем содержимое
        ContentType=content_type,
    )


def get_file_url(key: str) -> str:
    """
    Формирует публичный URL до объекта.
    Если нужно signed URL, здесь можно добавить логику boto3.generate_presigned_url.
    """
    return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{key}"
