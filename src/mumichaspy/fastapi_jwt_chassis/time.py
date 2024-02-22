import time


def get_current_timestamp_in_seconds():
    """Get the current timestamp in seconds."""
    return int(time.time())


def get_future_timestamp_in_seconds():
    """Get a future timestamp in seconds."""
    return get_current_timestamp_in_seconds() + 300
