from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DB_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    RABBIT_MQ_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_REGION: str
    MINIO_BUCKET: str

    class Config:
        env_file = ".env"


settings = Settings()
