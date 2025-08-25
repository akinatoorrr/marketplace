from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base_dao import MAX_PAGE_SIZE, BlogDAO
from .models import DeletedPost, Post


class PostDAO(BlogDAO[Post]):
    model = Post
    soft_delete_to = DeletedPost

    @classmethod
    async def edit_post(
        cls, session: AsyncSession, post_id: int, **values: Any
    ) -> Post:
        query = select(cls.model).filter_by(id=post_id)
        result = await session.execute(query)
        post = cast(Post | None, result.scalar_one_or_none())
        if not post:
            raise ValueError("Post not found")
        for key, value in values.items():
            if hasattr(post, key):
                setattr(post, key, value)
        return post

    @classmethod
    async def soft_delete_post(
        cls, session: AsyncSession, post_id: int
    ) -> dict[str, Any]:
        query = select(cls.model).filter_by(id=post_id)
        result = await session.execute(query)
        post = cast(Post | None, result.scalar_one_or_none())
        if not post:
            raise ValueError("Post not found")
        deleted_post = cls.soft_delete_to(
            original_id=post.id,
            title=post.title,
            text=post.text,
            category_id=post.category_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        session.add(deleted_post)
        await session.delete(post)
        await session.commit()
        return {"message": f"Пост с id={post.id} успешно удалён"}

    @classmethod
    async def search_posts(
        cls,
        session: AsyncSession,
        search_query: str,
        page_size: int | None,
        page_number: int | None,
    ) -> list[Post]:
        page_size = min(page_size or 10, MAX_PAGE_SIZE)
        page_number = page_number or 1
        ts_query = func.websearch_to_tsquery("russian", search_query)
        rank = func.ts_rank_cd(cls.model.tsv, ts_query)
        query = (
            select(cls.model)
            .where(cls.model.tsv.op("@@")(ts_query))
            .order_by(rank.desc())
            .limit(page_size)
            .offset((page_number - 1) * page_size)
        )
        result = await session.execute(query)
        return list(result.scalars().all())
