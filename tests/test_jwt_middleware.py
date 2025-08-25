import pytest


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client):
    response = await client.get("/posts/")
    assert response.status_code == 401
