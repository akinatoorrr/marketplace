from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    # Добавить SMTP_*, RABBITMQ_*, MINIO_*

    class Config:
        env_file = ".env"


settings = Settings()
