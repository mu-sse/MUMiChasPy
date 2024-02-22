import os
import uuid
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from mumichaspy.sqlalchemy_chassis.database import Base


logger = logging.getLogger(__name__)


async def reset_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_unique_memory_db():
    """Get unique meomory engine and db (e.g. for testing)."""

    engine_filename = f"file:{uuid.uuid4().hex}"
    engine = create_async_engine(
        # f"sqlite+aiosqlite://:memory:?cache=shared&uuid={uuid.uuid4()}",
        f"sqlite+aiosqlite:///{engine_filename}?mode=memory&cache=shared",
        poolclass=StaticPool,
        echo=False,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        future=True,
    )
    db = TestingSessionLocal()
    await reset_db(engine)
    try:
        yield db
    except Exception as exc:
        raise exc
    finally:
        await db.close()
        logger.info(f"Closed db {db}")
        await engine.dispose()
        logger.info(f"Disposed engine {engine}")
        if os.path.exists(engine_filename):
            os.remove(engine_filename)
            print(f"Removed {engine_filename}")
