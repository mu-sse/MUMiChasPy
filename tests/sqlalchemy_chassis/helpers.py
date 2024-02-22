# -*- coding: utf-8 -*-
"""Helper functions for testing."""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mumichaspy.sqlalchemy_chassis.testing_helpers import get_unique_memory_db

from .models import EntityForTesting

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


N_OF_ENTITIES = 20

entities = [
    {
        "id": i,
        "name": f"Test name {i}",
        "description": f"{N_OF_ENTITIES - i:03d} description",
    }
    for i in range(1, N_OF_ENTITIES + 1)
]


@asynccontextmanager
async def get_testing_db(empty: bool = True):
    """Get an alternative session for testing."""
    async with get_unique_memory_db() as db:
        try:
            if not empty:
                await insert_entities(db)
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e


async def insert_entities(db):
    """Insert entities from dict array into database."""
    for entity in entities:
        new_entity = EntityForTesting(
            name=entity["name"], description=entity["description"]
        )
        db.add(new_entity)
        await db.commit()
        await db.refresh(new_entity)
        assert entity["id"] == new_entity.id


def get_entity_ids():
    """Get a list of ids from entity dict array."""
    return [entity["id"] for entity in entities]


def get_entity_by_id(entity_id):
    """Get an entity by id from entity dict array."""
    return next(entity for entity in entities if entity["id"] == entity_id)
