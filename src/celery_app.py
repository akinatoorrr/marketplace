from celery import Celery

from src.app.core.config import settings

celery_app = Celery(
    "worker",  # имя проекта
    broker=settings.RABBIT_MQ_URL,  # RabbitMQ URL
    #  backend=settings.CELERY_RESULT_BACKEND  - Хранение результатов (опционально)
)

# Роутинг задач по очередям
celery_app.autodiscover_tasks(["src.tasks"])

# Общие прод-опции
celery_app.conf.update(
    task_serializer="json",  # сериализация
    result_serializer="json",  # результат
    accept_content=["json"],  # разрешённые форматы
    task_acks_late=True,  # подтверждение только после выполнения
    task_reject_on_worker_lost=True,  # откат если воркер умер
)
