from unittest.mock import patch

import pytest
from sqlalchemy import select

from src.app.db.models import User
from src.app.db.test_sessions import override_get_session_for_tests
from src.app.services.auth import create_access_token

from .utils import unique_username_email


@pytest.mark.asyncio
@patch("src.celery_app.celery_app.send_task")
async def test_user_registration(mock_send_task, client):
    unique_username, unique_email = unique_username_email()
    payload = {
        "email": unique_email,
        "password": "secret123",
        "username": unique_username,
        "phone_number": "+79990000000",
    }

    response = await client.post("/auth/register/", json=payload)
    mock_send_task.assert_called_once()

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Вы успешно зарегистрированы!"

    async for session in override_get_session_for_tests():
        result = await session.execute(select(User).where(User.email == unique_email))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == unique_email
        break


def test_jwt_creation():
    token = create_access_token({"sub": "user_id_123"})
    assert token.startswith("eyJ")
