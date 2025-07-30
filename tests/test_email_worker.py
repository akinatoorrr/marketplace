from unittest.mock import patch

import pytest


@pytest.mark.asyncio
@patch("src.celery_app.celery_app.send_task")
async def test_registration_email_sent(mock_send_email, client):
    payload = {
        "email": "user@example.com",
        "password": "secret123",
        "username": "testuser",
        "phone_number": "+79990000000",
    }

    response = await client.post("/auth/register/", json=payload)

    assert response.status_code == 201
    mock_send_email.assert_called_once()
