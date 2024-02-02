# -*- coding: utf-8 -*-
"""Helper functions for testing."""

from contextlib import asynccontextmanager
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from .models import EntityForTesting

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


N_OF_ENTITIES = 20

entities = [
    {
        "id": None,
        "name": f"Test name {i}",
        "description": f"{N_OF_ENTITIES - i:03d} description",
    }
    for i in range(N_OF_ENTITIES)
]


@asynccontextmanager
async def get_db(empty: bool = True):
    """Get an alternative session for testing."""
    print("Getting empty database")
    db = await init_empty_db()

    try:
        if not empty:
            await insert_entities(db)
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        await db.close()


async def init_tables():
    """Create tables if needed."""
    async with engine.begin() as conn:
        has_table = await conn.run_sync(
            lambda conn: inspect(conn).has_table(EntityForTesting.__tablename__)
        )
        if not has_table:
            print("Creating tables")
            await conn.run_sync(EntityForTesting.metadata.create_all)


async def init_empty_db():
    """Get an empty but formed database."""
    await init_tables()
    db = async_session()
    await truncate_table(db)
    return db


async def insert_entities(db):
    """Insert entities from dict array into database."""
    for entity in entities:
        new_entity = EntityForTesting(**entity)
        db.add(new_entity)
        await db.commit()
        await db.refresh(new_entity)
        entity["id"] = new_entity.id


async def truncate_table(db, table_names=None):
    """Truncate given tables."""
    if table_names is None:
        table_names = [EntityForTesting.__tablename__]
    for table_name in table_names:
        await db.execute(text("DELETE FROM " + table_name))
    for entity in entities:
        entity["id"] = None


def get_ids():
    """Get a list of ids from entity dict array."""
    return [entity["id"] for entity in entities]


def get_entity_by_id(entity_id):
    """Get an entity by id from entity dict array."""
    return next(entity for entity in entities if entity["id"] == entity_id)
