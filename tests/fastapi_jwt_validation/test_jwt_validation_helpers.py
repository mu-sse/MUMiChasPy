import time
from fastapi import HTTPException, status
import jwt
import pytest
from mumichaspy.fastapi_jwt_validation.config import config

from mumichaspy.fastapi_jwt_validation.validation import (
    validate_and_decode_token,
)
from tests.fastapi_jwt_validation.helpers import TESTING_PUBLIC_KEY, TESTING_PRIVATE_KEY

config.public_key = TESTING_PUBLIC_KEY


def test_validate_and_decode_token():
    # Arrange
    expected_decoded_token = {
        "user_id": "123",
        "iss": config.jwt_issuer,
        "exp": int(time.time()) + 60,
    }
    encoded_token = jwt.encode(
        expected_decoded_token, TESTING_PRIVATE_KEY, algorithm=config.jwt_algorithm
    )

    # Act
    result = validate_and_decode_token(
        encoded_token,
        TESTING_PUBLIC_KEY,
        expected_decoded_token["iss"],
        [config.jwt_algorithm],
    )

    # Assert
    assert result == expected_decoded_token


def test_validate_and_decode_token_exp_error():
    # Arrange
    expected_decoded_token = {
        "user_id": "123",
        "iss": config.jwt_issuer,
        "exp": int(time.time()) - 60,
    }
    encoded_token = jwt.encode(
        expected_decoded_token, TESTING_PRIVATE_KEY, algorithm=config.jwt_algorithm
    )

    # Act
    with pytest.raises(HTTPException, match="403: Could not decode JWT") as exc:
        validate_and_decode_token(
            encoded_token,
            TESTING_PUBLIC_KEY,
            expected_decoded_token["iss"],
            [config.jwt_algorithm],
        )

        assert exc.status_code == status.HTTP_403_FORBIDDEN


# @Todo: Add more tests for validate_and_decode_token
# @ToDo: Add more tests for JWTBearer and JWTBearerAdmin
