import boto3

from .config import settings

s3_client = boto3.client(
    "s3",  # Мы используем сервис S3
    endpoint_url=settings.MINIO_ENDPOINT,  # Подключаемся к MinIO вместо AWS
    aws_access_key_id=settings.MINIO_ACCESS_KEY,  # Ключ доступа
    aws_secret_access_key=settings.MINIO_SECRET_KEY,  # Секретный ключ
    region_name=settings.MINIO_REGION,  # Регион (не обязателен для MinIO)
    # В MinIO обычно не используется SSL,
    # если используешь http — стоит явно указать verify=False
    # verify=False  # (по умолчанию True, для https)
)
