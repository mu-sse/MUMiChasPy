# -*- coding: utf-8 -*-
"""Tests for crud helper functions."""

import pytest

from sqlalchemy.future import select

from mumichaspy.sqlalchemy_crud.crud_helpers import (
    get_element_by_id,
    get_first_statement_result,
    get_list,
    delete_element_by_id,
)
from .helpers import get_db, get_ids, N_OF_ENTITIES
from .models import EntityForTesting


@pytest.mark.asyncio
async def test_get_element_by_id_error_not_found():
    """Test that get_element_by_id returns None when element is not found."""
    async with get_db() as db:
        element = await get_element_by_id(db, EntityForTesting, 1)
        assert element is None


@pytest.mark.asyncio
async def test_get_element_by_id_ok():
    """Test that get_element_by_id returns the correct element."""
    async with get_db(empty=False) as db:
        ids = get_ids()
        for entity_id in ids:
            element = await get_element_by_id(db, EntityForTesting, entity_id)
            assert element is not None
            assert element.id == entity_id


@pytest.mark.asyncio
async def test_get_list_empty_ok():
    """Test that get_list returns an empty array when there are no elements."""
    async with get_db() as db:
        elements = await get_list(db, EntityForTesting)
        assert elements is not None
        assert len(elements) == 0


@pytest.mark.asyncio
async def test_get_list_ok():
    """Test that get_list returns all elements."""
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting)
        assert elements is not None
        assert len(elements) == N_OF_ENTITIES
        for element in elements:
            assert element is not None
            assert element.id is not None
            assert element.name is not None
            assert element.description is not None


@pytest.mark.asyncio
async def test_get_list_order_by_ok():
    """Test that default order by (asc) works."""
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, order_by="description")
        assert elements is not None
        assert len(elements) == N_OF_ENTITIES
        for i in range(1, N_OF_ENTITIES):
            assert elements[i - 1].description < elements[i].description


@pytest.mark.asyncio
async def test_get_list_order_by_desc_ok():
    """Test that order by desc works."""
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, order_by="-description")
        assert elements is not None
        assert len(elements) == N_OF_ENTITIES
        for i in range(1, N_OF_ENTITIES):
            assert elements[i - 1].description > elements[i].description


@pytest.mark.asyncio
async def test_get_list_offset_ok():
    """Test that offset option works."""
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, offset=5)
        assert elements is not None
        assert len(elements) == N_OF_ENTITIES - 5
        for i in range(N_OF_ENTITIES - 5):
            assert elements[i].id == i + 6


@pytest.mark.asyncio
async def test_get_list_limit_ok():
    """Test that limit option works."""
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, limit=5)
        assert elements is not None
        assert len(elements) == 5
        for i in range(5):
            assert elements[i].id == i + 1


@pytest.mark.asyncio
async def test_get_list_order_limit_offset_ok():
    """Test that all options work together."""
    offset = 10
    limit = 4
    order_by = "-id"
    async with get_db(empty=False) as db:
        elements = await get_list(
            db, EntityForTesting, order_by=order_by, limit=limit, offset=offset
        )
        assert elements is not None
        assert len(elements) == limit
        for i in range(limit):
            expected_id = N_OF_ENTITIES - offset - i
            assert elements[i].id == expected_id


@pytest.mark.asyncio
async def test_larger_offset_than_elements_ok():
    """
    If offset is larger than the number of elements, no error is expected,
    but an empty array is returned.
    """
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, offset=N_OF_ENTITIES)
        assert elements is not None
        assert len(elements) == 0


@pytest.mark.asyncio
async def test_larger_offset_limit_than_elements_ok():
    """
    If offset + limit is larger than the number of elements, no error is expected,
    but a smaller array is returned.
    """
    expected_length = 2
    offset = N_OF_ENTITIES - expected_length
    limit = 4
    async with get_db(empty=False) as db:
        elements = await get_list(db, EntityForTesting, offset=offset, limit=limit)
        assert elements is not None
        assert len(elements) == expected_length


@pytest.mark.asyncio
async def test_delete_element_by_id_error_not_found():
    """Test that delete_element_by_id returns None when element is not found."""
    async with get_db() as db:
        element = await delete_element_by_id(db, EntityForTesting, 1)
        assert element is None


@pytest.mark.asyncio
async def test_delete_element_by_id_ok():
    """
    Test that delete_element_by_id returns the correct element and that is actualy deleted
    from database.
    """
    async with get_db(empty=False) as db:
        delete_id = get_ids()[0]
        element = await delete_element_by_id(db, EntityForTesting, delete_id)
        assert element is not None
        assert element.id == delete_id

        elements = await get_list(db, EntityForTesting)
        assert elements is not None
        assert len(elements) == N_OF_ENTITIES - 1

        element = await get_element_by_id(db, EntityForTesting, delete_id)
        assert element is None


@pytest.mark.asyncio
async def test_get_first_statement_result_ok():
    """Test that get_first_statement_result returns the first element."""
    async with get_db(empty=False) as db:
        expected_id = get_ids()[0]
        stmt = select(EntityForTesting)
        element = await get_first_statement_result(db, stmt)
        assert element is not None
        assert element.id == expected_id
        assert element.name == f"Test name {expected_id - 1}"
        assert (
            element.description
            == f"{N_OF_ENTITIES - (expected_id - 1):03d} description"
        )
