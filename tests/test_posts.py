import pytest
from sqlalchemy import select

from src.app.db.models import Post
from src.app.db.test_sessions import override_get_session_for_tests

from .utils import unique_blog_title


@pytest.mark.asyncio
async def test_get_post_list(client, auth_headers, single_post):
    response = await client.get("/posts/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(post["title"] == single_post["title"] for post in data)


@pytest.mark.asyncio
async def test_create_post(client, auth_headers, category_for_post):
    unique_title = unique_blog_title()
    payload = {
        "title": unique_title,
        "text": "Test test text",
        "category_id": category_for_post["id"],
    }
    response = await client.post("/posts/", data=payload, headers=auth_headers)
    assert response.status_code == 201

    async for session in override_get_session_for_tests():
        result = await session.execute(select(Post).where(Post.title == unique_title))
        post = result.scalar_one_or_none()
        assert post is not None
        assert post.title == unique_title
        break  # Нужна только одна сессия


@pytest.mark.asyncio
async def test_edit_post(client, auth_headers, single_post):
    payload = {"title": "Update Test post"}
    response = await client.put(
        f"/posts/{single_post['id']}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Update Test post"
