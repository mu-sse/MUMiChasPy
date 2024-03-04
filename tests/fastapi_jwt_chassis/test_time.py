from mumichaspy.fastapi_jwt_chassis.time import (
    current_timestamp,
    current_timestamp_with_timedelta,
    current_datetime,
    current_datetime_with_timedelta,
)


def test_current_datetime_wtih_timedelta():
    # Arrange
    seconds = 300
    current_datetime_1 = current_datetime()

    # Act
    result = current_datetime_with_timedelta(
        seconds=seconds,
    )

    # Assert
    diff = result - current_datetime_1
    assert diff.total_seconds() >= 300


def test_current_timestamp_with_timedelta():
    # Arrange
    current_timestamp_1 = current_timestamp()
    seconds = 300

    # Act
    result = current_timestamp_with_timedelta(
        seconds=seconds,
    )

    # Assert
    assert result >= current_timestamp_1 + 300
