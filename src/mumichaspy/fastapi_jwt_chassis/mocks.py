import jwt
from mumichaspy.fastapi_jwt_chassis.config import config
from mumichaspy.fastapi_jwt_chassis.time import (
    current_timestamp,
    current_timestamp_with_timedelta,
    DEFAULT_TIMEDELTA,
)

TESTING_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCUQJHeEDVKZAVKpYwXPxIGA4Uf
sV1Y15JlnoK3nr6bFUCdI3oKc/nEco5XY6Do4Ek+ECk2rnpxDExLAUJbA1ea41tt
jhGp7pJYwqU+eA66mu9lIkBjQFXagmvAAG+PfN4NE80DM17eLMcBXS2jkz2O36Iz
xtfFHeD8pDuYRtx3KwIDAQAB
-----END PUBLIC KEY-----
"""

TESTING_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCUQJHeEDVKZAVKpYwXPxIGA4UfsV1Y15JlnoK3nr6bFUCdI3oK
c/nEco5XY6Do4Ek+ECk2rnpxDExLAUJbA1ea41ttjhGp7pJYwqU+eA66mu9lIkBj
QFXagmvAAG+PfN4NE80DM17eLMcBXS2jkz2O36IzxtfFHeD8pDuYRtx3KwIDAQAB
AoGAHOz4SP6alzgqvCTOz55Tsu6u478kengdLUyfLpp/kBy2bbKFVlLIkebUFQLw
W1+fisd2cx/Z7gK7RAsr2jwttFIZ2qaq3z+hMQ+ihqvMv5kQPMTiyymDCvNdrp3I
LTDz0yF4nygXvU3DR+vG1WQnzNWP4H5A7daBi3INoew+CVECQQDwypjbNKYhgMlY
r3yZw0nXrEJZM7x9i7+NUfmZsKn5olUmImm67rvMw7bbrCvxwgRFcCDo/G2iGo1N
MUpvrKsDAkEAnZ2wWfFMEHz+2b3k+jwTsSWrV3FaTBCWb0Wo8TDAsVHb+qUAUhTG
B/3kUimdXoz/1YqpnfvF2M1NiKEJokD2uQJACj1jYLcNdZFHfrj/wH44jq5pp+d2
VZRy0eyxg6Kqp84KdvOxsVxjqiKMjSz2NXK9wcIx9BaABwvABI9bDgK2xwJAO6dG
64Or6kGkovyAAUVjnpRHOR0ps8hDZ3HR8xcklvgIbeCtMmOyX6v0EjS13uc2nLeS
Yry7sMZjJebtIn+74QJBAOXUcGRQG6rJgWcI43mr40L1JanOPTuZvRHd2XfT9zkd
9ma0n1LI2LExC0U9Ho+3bMiHVK5lf7NhHgdqps3lMos=
-----END RSA PRIVATE KEY-----
"""

DECODED_MOCK_JWT = {
    "sub": 1,
    "username": "jdoe",
    "iss": config.jwt_issuer,
    "is_active": True,
    "email": "jdoe@example.com",
    "roles": ["USER"],
}

DECODED_ADMIN_MOCK_JWT = {
    "sub": 1,
    "username": "admin",
    "iss": config.jwt_issuer,
    "is_active": True,
    "email": "admin@example.com",
    "roles": ["ADMIN"],
}


def get_encoded_mock_jwt(jwt_payload):
    """Get an encoded JWT."""
    if "iat" not in jwt_payload:
        jwt_payload["iat"] = current_timestamp()
    if "exp" not in jwt_payload:
        jwt_payload["exp"] = current_timestamp_with_timedelta(seconds=DEFAULT_TIMEDELTA)
    return jwt.encode(jwt_payload, TESTING_PRIVATE_KEY, algorithm="RS256")


def mock_jwt_decode_error(encoded_token, public_key, issuer, algorithms):
    """Mock JWT decode error."""

    raise jwt.exceptions.DecodeError("error mocked")


def mock_jwt_decode_ok(encoded_token, public_key, issuer, algorithms):
    """Mock validate and decode token and return a JWT."""
    global DECODED_MOCK_JWT
    return {**DECODED_MOCK_JWT}


def mock_jwt_decode_admin_ok(encoded_token, public_key, issuer, algorithms):
    """Mock validate and decode token and return a JWT."""
    global DECODED_ADMIN_MOCK_JWT
    return {**DECODED_ADMIN_MOCK_JWT}


def mock_jwt_headers(headers: dict = {}):
    """Get a mock JWT header."""
    global DECODED_MOCK_JWT
    return {
        **headers,
        "Authorization": f"Bearer {get_encoded_mock_jwt(DECODED_MOCK_JWT)}",
    }


def mock_jwt_headers_admin(headers: dict = {}):
    """Get a mock JWT header."""
    global DECODED_ADMIN_MOCK_JWT
    return {
        **headers,
        "Authorization": f"Bearer {get_encoded_mock_jwt(DECODED_ADMIN_MOCK_JWT)}",
    }


def assert_token_validation_called(mock_validate_and_decode_token, encoded_token):
    """Assert mock validate and decode token was called."""
    mock_validate_and_decode_token.assert_called_once_with(
        encoded_token=encoded_token,
        public_key=config.public_key,
        issuer=config.jwt_issuer,
        algorithms=[config.jwt_algorithm],
    )
