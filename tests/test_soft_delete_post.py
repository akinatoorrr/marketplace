import pytest
from sqlalchemy import select

from src.app.db.models import DeletedPost, Post
from src.app.db.test_sessions import override_get_session_for_tests


@pytest.mark.asyncio
async def test_soft_delete_post(client, auth_headers, single_post):
    async for session in override_get_session_for_tests():
        result = await session.execute(
            select(Post).where(Post.title == single_post["title"])
        )
        post = result.scalar_one_or_none()
        assert post is not None
        assert post.title == single_post["title"]
        break

    response = await client.delete(f"posts/{single_post['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == f"Пост с id={single_post['id']} успешно удалён"

    async for session in override_get_session_for_tests():
        result = await session.execute(
            select(Post).where(Post.title == single_post["title"])
        )
        post = result.scalar_one_or_none()
        assert post is None
        soft_result = await session.execute(
            select(DeletedPost).where(DeletedPost.title == single_post["title"])
        )
        soft_result = soft_result.scalar_one_or_none()
        assert soft_result is not None
        assert soft_result.title == single_post["title"]
        break
