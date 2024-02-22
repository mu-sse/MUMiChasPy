import os
import random
import string
from unittest import TestCase, mock
import tempfile
from mumichaspy.fastapi_jwt_chassis.config import (
    Config,
    get_public_key_from_url,
    get_public_key_from_file,
)
from mumichaspy.fastapi_jwt_chassis.mocks import TESTING_PUBLIC_KEY


@mock.patch("httpx.Client.get")
def test_get_public_key_from_url_ok(mock_get):
    # Arrange
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        public_key_file_name = temp.name

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = TESTING_PUBLIC_KEY

        mock_get.return_value = mock_response

        if os.path.isfile(public_key_file_name):
            os.remove(public_key_file_name)

        # Act
        public_key = get_public_key_from_url("", public_key_file_name)

        # Assert
        assert public_key == TESTING_PUBLIC_KEY
        assert os.path.isfile(public_key_file_name)
        with open(public_key_file_name, "r") as f:
            assert f.read() == TESTING_PUBLIC_KEY


@mock.patch("httpx.Client.get")
def test_get_public_key_from_url_error(mock_get):
    # Arrange
    public_key_file_name = (
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(12)
        )
        + "_public_key.pem"
    )
    mock_response = mock.Mock()
    mock_response.status_code = 404

    mock_get.return_value = mock_response
    if os.path.isfile(public_key_file_name):
        os.remove(public_key_file_name)

    # Act
    public_key = get_public_key_from_url(
        public_key_url="", file_path=public_key_file_name
    )

    # Assert
    assert public_key is None
    assert not os.path.isfile(public_key_file_name)


def test_update_public_key_from_file_ok():
    # Arrange
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        public_key_file_name = temp.name
        temp.write(TESTING_PUBLIC_KEY.encode())
    temp.close()

    # Act
    public_key = get_public_key_from_file(file_path=public_key_file_name)

    # Assert
    assert public_key == TESTING_PUBLIC_KEY
    os.remove(public_key_file_name)


def test_update_public_key_from_file_error():
    # Arrange
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        public_key_file_name = temp.name

    # Act
    public_key = get_public_key_from_file(file_path=public_key_file_name)

    # Assert
    assert public_key is None


class TestConfig(TestCase):
    def setUp(self):
        self.config = Config()

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
    def test_update_public_key_url_ok(self, mock_get_public_key_from_url):
        # Arrange
        mock_get_public_key_from_url.return_value = TESTING_PUBLIC_KEY

        # Act
        self.config.update_public_key()

        # Assert
        assert self.config.public_key == TESTING_PUBLIC_KEY

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
    def test_update_public_key_no_url_file_ok(
        self, mock_get_public_key_from_url, mock_get_public_key_from_file
    ):
        # Arrange
        mock_get_public_key_from_url.return_value = None
        mock_get_public_key_from_file.return_value = TESTING_PUBLIC_KEY

        # Act
        self.config.update_public_key()

        # Assert
        assert self.config.public_key == TESTING_PUBLIC_KEY

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
    def test_update_public_key_no_url_file_error(
        self, mock_get_public_key_from_url, mock_get_public_key_from_file
    ):
        # Arrange
        mock_get_public_key_from_url.return_value = None
        mock_get_public_key_from_file.return_value = None

        # Act
        self.config.update_public_key()

        # Assert
        assert self.config.public_key is None
