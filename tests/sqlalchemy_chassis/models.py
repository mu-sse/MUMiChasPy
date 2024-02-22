# -*- coding: utf-8 -*-
"""Database models for testing."""

from sqlalchemy import Column, Integer, String


from mumichaspy.sqlalchemy_chassis.database import Base


class EntityForTesting(Base):  # pylint: disable=too-few-public-methods
    """Testing entity for CRUD helpers."""

    __tablename__ = "entity_testing"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    description = Column(String(50), index=True)
