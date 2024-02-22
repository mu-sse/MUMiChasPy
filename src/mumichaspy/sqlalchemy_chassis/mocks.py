async def get_mock_db():
    """Get a mock database."""
    print("Getting mock database")
    db = None
    try:
        yield db
    except Exception as exc:
        raise exc
