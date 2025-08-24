from celery import Celery

from src.app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.RABBIT_MQ_URL,
)

celery_app.autodiscover_tasks(["src.tasks"])

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
