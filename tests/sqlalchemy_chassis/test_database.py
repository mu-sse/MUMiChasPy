import os
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mumichaspy.sqlalchemy_chassis.database import get_db


@pytest.mark.asyncio
async def test_get_db():
    """Test get_db."""

    # Arrange
    # remove database file if it exists
    db_file = "./microservice.db"
    if os.path.isfile(db_file):
        os.remove(db_file)

    # Act
    async for db in get_db():
        assert db is not None
        assert isinstance(db, AsyncSession)
        await db.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY);"))

    # Assert
    # check that db is closed
    assert not db.in_transaction()

    # Check if the database file exists
    assert os.path.isfile(db_file)

    # check that table has been created
    async for db in get_db():
        result = await db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = [row[0] for row in result]
        assert "test" in tables

    # Remove the database file
    os.remove(db_file)
