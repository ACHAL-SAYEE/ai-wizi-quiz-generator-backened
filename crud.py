# app/crud.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models import QuizEntry
from schemas import QuizResponse
from sqlalchemy.ext.asyncio import AsyncSession

async def get_all_entries(db: AsyncSession):
    q = await db.execute(select(QuizEntry).order_by(QuizEntry.created_at.desc()))
    return q.scalars().all()

async def get_entry_by_id(db: AsyncSession, entry_id: int):
    q = await db.execute(select(QuizEntry).where(QuizEntry.id == entry_id))
    return q.scalar_one_or_none()

async def get_entry_by_url(db: AsyncSession, url: str):
    q = await db.execute(select(QuizEntry).where(QuizEntry.url == url))
    return q.scalar_one_or_none()

async def create_or_update_entry(db: AsyncSession, payload: dict):
    # payload should match model keys
    existing = await get_entry_by_url(db, payload["url"])
    if existing:
        # update
        for k, v in payload.items():
            setattr(existing, k, v)
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        new = QuizEntry(**payload)
        db.add(new)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            found = await get_entry_by_url(db, payload["url"])
            return found
        await db.refresh(new)
        return new
