from fastapi import HTTPException, status
import pytest
from unittest.mock import MagicMock, patch
from mumichaspy.fastapi_jwt_chassis.config import config
import logging
from mumichaspy.fastapi_jwt_chassis.validation import (
    validate_and_decode_token,
    JWTBearer,
    JWTBearerAdmin,
)
from mumichaspy.fastapi_jwt_chassis.mocks import (
    TESTING_PUBLIC_KEY,
    DECODED_MOCK_JWT,
    DECODED_ADMIN_MOCK_JWT,
    get_encoded_mock_jwt,
)

from mumichaspy.fastapi_jwt_chassis.time import current_timestamp


logger = logging.getLogger(__name__)
config.public_key = TESTING_PUBLIC_KEY


def test_validate_and_decode_token():
    # Arrange
    current_timestamp_sec = current_timestamp()
    encoded_token = get_encoded_mock_jwt(DECODED_MOCK_JWT)

    # Act
    result = validate_and_decode_token(
        encoded_token,
        TESTING_PUBLIC_KEY,
        DECODED_MOCK_JWT["iss"],
        [config.jwt_algorithm],
    )

    # Assert
    assert result["exp"] > current_timestamp_sec
    assert result["iat"] <= current_timestamp_sec
    for key in DECODED_MOCK_JWT.keys():
        assert result[key] == DECODED_MOCK_JWT[key]


def test_validate_and_decode_token_exp_error():
    # Arrange
    current_timestamp_sec = current_timestamp()
    encoded_token = get_encoded_mock_jwt(
        {
            **DECODED_MOCK_JWT,
            "exp": current_timestamp_sec - 1,
            "iat": current_timestamp_sec - 301,
        }
    )

    # Act
    with pytest.raises(HTTPException) as exc:
        validate_and_decode_token(
            encoded_token,
            TESTING_PUBLIC_KEY,
            DECODED_MOCK_JWT["iss"],
            [config.jwt_algorithm],
        )

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Could not decode JWT"


# @Todo: Add more tests for validate_and_decode_token
# @ToDo: Add more tests for JWTBearer and JWTBearerAdmin


@pytest.mark.asyncio
async def test_jwt_bearer_ok():
    """Test JWTBearer with a valid token."""
    # Arrange
    with patch(
        "mumichaspy.fastapi_jwt_chassis.validation.validate_and_decode_token",
        return_value=DECODED_MOCK_JWT,
    ) as mock_validate:
        jwt_bearer = JWTBearer()
        request = MagicMock()
        encoded_token = get_encoded_mock_jwt(DECODED_MOCK_JWT)
        request.headers = {"Authorization": f"Bearer {encoded_token}"}

        # Act
        decoded_jwt = await jwt_bearer(request)

        # Assert
        mock_validate.assert_called_once_with(
            encoded_token=encoded_token,
            public_key=config.public_key,
            issuer=config.jwt_issuer,
            algorithms=[config.jwt_algorithm],
        )
        for key in DECODED_MOCK_JWT.keys():
            assert decoded_jwt[key] == DECODED_MOCK_JWT[key]
        assert decoded_jwt["exp"] > current_timestamp()
        assert decoded_jwt["iat"] <= current_timestamp()


@pytest.mark.asyncio
async def test_jwt_bearer_admin_ok():
    """Test JWTBearerAdmin with a valid token."""
    # Arrange
    with patch(
        "mumichaspy.fastapi_jwt_chassis.validation.validate_and_decode_token",
        return_value=DECODED_ADMIN_MOCK_JWT,
    ) as mock_validate:
        jwt_bearer_admin = JWTBearerAdmin()
        request = MagicMock()
        encoded_token = get_encoded_mock_jwt(DECODED_ADMIN_MOCK_JWT)
        request.headers = {"Authorization": f"Bearer {encoded_token}"}
        decoded_jwt = await jwt_bearer_admin(request)
        mock_validate.assert_called_once_with(
            encoded_token=encoded_token,
            public_key=config.public_key,
            issuer=config.jwt_issuer,
            algorithms=[config.jwt_algorithm],
        )
        for key in DECODED_ADMIN_MOCK_JWT.keys():
            assert decoded_jwt[key] == DECODED_ADMIN_MOCK_JWT[key]
        assert decoded_jwt["exp"] > current_timestamp()
        assert decoded_jwt["iat"] <= current_timestamp()


@pytest.mark.asyncio
async def test_jwt_bearer_admin_error_no_admin_role():
    """Test JWTBearerAdmin with a valid token but no admin role."""
    # Arrange
    with patch(
        "mumichaspy.fastapi_jwt_chassis.validation.validate_and_decode_token",
        return_value=DECODED_MOCK_JWT,
    ) as mock_validate:
        jwt_bearer_admin = JWTBearerAdmin()
        request = MagicMock()
        encoded_token = get_encoded_mock_jwt(DECODED_MOCK_JWT)
        request.headers = {"Authorization": f"Bearer {encoded_token}"}

        # Act
        with pytest.raises(HTTPException) as exc:
            await jwt_bearer_admin(request)
            print(exc)

        # Assert
        assert exc.value.detail == "Only admins can perform this action"
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        mock_validate.assert_called_once_with(
            encoded_token=encoded_token,
            public_key=config.public_key,
            issuer=config.jwt_issuer,
            algorithms=[config.jwt_algorithm],
        )
