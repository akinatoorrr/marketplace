import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from src.app.db.sessions import get_db_session
from src.app.db.test_sessions import (
    init_test_db,
    override_get_session_for_tests,
)
from src.app.main import app

from .utils import unique_blog_title, unique_username_email


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
def patch_celery_send_task():
    with patch("src.celery_app.celery_app.send_task") as mock_send_task:
        yield mock_send_task


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    await init_test_db()


@pytest_asyncio.fixture
async def auth_headers(client):
    unique_username, unique_email = unique_username_email()
    payload = {
        "email": unique_email,
        "password": "secret123",
        "username": unique_username,
        "phone_number": "+79990000000",
    }
    reg_resp = await client.post("/auth/register/", json=payload)
    assert reg_resp.status_code == 201, (
        f"User register failed: {reg_resp.status_code} {reg_resp.json()}"
    )
    login_resp = await client.post(
        "/auth/login/",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_resp.status_code == 200, (
        f"User login failed: {login_resp.status_code} {login_resp.json()}"
    )
    token = login_resp.cookies.get("users_access_token")
    headers = {"Authorization": f"Bearer {token}"}
    yield headers

    # Teardown
    async for session in override_get_session_for_tests():
        await session.execute(
            text('DELETE FROM "user" WHERE email = :email'), {"email": payload["email"]}
        )
        await session.commit()
        break


@pytest_asyncio.fixture(scope="function")
async def client():
    def get_test_db_session():
        async def _get_session():
            async for session in override_get_session_for_tests():
                yield session

        return _get_session

    app.dependency_overrides[get_db_session] = get_test_db_session()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def category_for_post(client, auth_headers):
    unique_title = unique_blog_title()
    payload = {"title": unique_title}
    response = await client.post("/categories/", json=payload, headers=auth_headers)
    assert response.status_code == 201, (
        f"Category creation failed: {response.status_code} {response.json()}"
    )
    category = response.json()
    yield category

    # Teardown
    async for session in override_get_session_for_tests():
        await session.execute(
            text("DELETE FROM post WHERE category_id = :category_id"),
            {"category_id": category["id"]},
        )
        await session.execute(
            text("DELETE FROM category WHERE title = :title"),
            {"title": payload["title"]},
        )
        await session.commit()
        break


@pytest_asyncio.fixture
async def single_post(client, auth_headers, category_for_post):
    unique_title = unique_blog_title()
    payload = {
        "title": unique_title,
        "text": "Test test text",
        "category_id": category_for_post.get("id"),
    }
    response = await client.post("/posts/", data=payload, headers=auth_headers)
    assert response.status_code == 201, (
        f"Post creation failed: {response.status_code} {response.json()}"
    )
    post = response.json()
    yield post

    # Teardown
    async for session in override_get_session_for_tests():
        await session.execute(
            text("DELETE FROM post WHERE title = :title"), {"title": payload["title"]}
        )
        await session.commit()
        break
