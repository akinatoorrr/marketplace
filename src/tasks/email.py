import smtplib
from email.message import EmailMessage

from celery import shared_task

from src.app.core.config import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, email_to: str):  # type: ignore
    msg = EmailMessage()
    msg["Subject"] = "Добро пожаловать!"
    msg["From"] = "noreply@example.com"
    msg["To"] = email_to
    msg.set_content("Спасибо за регистрацию!")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.send_message(msg)
    except Exception as exc:
        raise self.retry(exc=exc)  # noqa: B904
