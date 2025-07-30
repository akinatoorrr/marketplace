import pytest
from sqlalchemy import select

from src.app.db.models import Category
from src.app.db.test_sessions import override_get_session_for_tests

from .utils import unique_blog_title


@pytest.mark.asyncio
async def test_get_category_list(client, auth_headers, category_for_post):
    response = await client.get("/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(category["title"] == category_for_post["title"] for category in data)


@pytest.mark.asyncio
async def test_create_category(client, auth_headers):
    unique_title = unique_blog_title()
    payload = {"title": unique_title}
    response = await client.post("/categories/", json=payload, headers=auth_headers)
    assert response.status_code == 201

    async for session in override_get_session_for_tests():
        result = await session.execute(
            select(Category).where(Category.title == unique_title)
        )
        category = result.scalar_one_or_none()
        assert category is not None
        assert category.title == unique_title
        break  # Нужна только одна сессия
