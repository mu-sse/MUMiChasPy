import os
import uuid
from unittest import TestCase, mock
import tempfile
from mumichaspy.fastapi_jwt_chassis.config import (
    Config,
    get_public_key_from_url,
    get_public_key_from_file,
    write_public_key_to_file,
    get_public_key,
)
from mumichaspy.fastapi_jwt_chassis.mocks import TESTING_PUBLIC_KEY


# get_public_key_from_url #########################################################################
@mock.patch("httpx.Client.get")
def test_get_public_key_from_url_ok(mock_get):
    # Arrange
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.text = TESTING_PUBLIC_KEY
    mock_get.return_value = mock_response
    url = "https://example.com/public_key"

    # Act
    public_key = get_public_key_from_url(url)

    # Assert
    mock_get.assert_called_once_with(url)
    assert public_key == TESTING_PUBLIC_KEY


@mock.patch("httpx.Client.get")
def test_get_public_key_from_url_error(mock_get):
    # Arrange
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    url = "https://example.com/public_key"

    # Act
    public_key = get_public_key_from_url(url)

    # Assert
    mock_get.assert_called_once_with(url)
    assert public_key is None


@mock.patch("httpx.Client.get")
def test_get_public_key_from_url_no_url(mock_get):
    # Arrange
    url = ""

    # Act
    public_key = get_public_key_from_url(public_key_url=url)

    # Assert
    mock_get.assert_not_called()
    assert public_key is None


# get_public_key_from_file ########################################################################
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


@mock.patch("mumichaspy.fastapi_jwt_chassis.config.logger.warning")
def test_update_public_key_from_file_no_file(logger_warning_mock):
    # Arrange
    filename = f"{uuid.uuid4().hex}.pem"

    # Act
    public_key = get_public_key_from_file(file_path=filename)

    # Assert
    logger_warning_mock.assert_called_once_with(
        "Could not load public key from file: Public key file not found"
    )
    assert public_key is None


# write_public_key_to_file ########################################################################
def test_write_public_key_to_file_ok():
    # Arrange
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        public_key_file_name = temp.name

    # Act
    write_public_key_to_file(
        public_key=TESTING_PUBLIC_KEY, file_path=public_key_file_name
    )

    # Assert
    with open(public_key_file_name, "r") as f:
        public_key = f.read()
    assert public_key == TESTING_PUBLIC_KEY
    os.remove(public_key_file_name)


# get_public_key ##################################################################################
@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_file")
@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
def test_get_public_key_ok_public_key(mock_from_url, mock_from_file):
    # Arrange
    public_key = TESTING_PUBLIC_KEY
    public_key_url = "https://example.com/public_key"
    public_key_file_path = f"{uuid.uuid4().hex}.pem"

    # Act
    result = get_public_key(
        public_key=public_key,
        public_key_url=public_key_url,
        public_key_file_path=public_key_file_path,
    )

    # Assert
    mock_from_url.assert_not_called()
    mock_from_file.assert_not_called()
    assert result == TESTING_PUBLIC_KEY


@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_file")
@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
def test_get_public_key_ok_url(mock_from_url, mock_from_file):
    # Arrange
    public_key = ""
    public_key_url = "https://example.com/public_key"
    public_key_file_path = f"{uuid.uuid4().hex}.pem"
    mock_from_url.return_value = TESTING_PUBLIC_KEY

    # Act
    result = get_public_key(
        public_key=public_key,
        public_key_url=public_key_url,
        public_key_file_path=public_key_file_path,
    )

    # Assert
    mock_from_url.assert_called_once_with(public_key_url)
    mock_from_file.assert_not_called()
    assert result == TESTING_PUBLIC_KEY


@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_file")
@mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key_from_url")
def test_get_public_key_ok_public_file(mock_from_url, mock_from_file):
    # Arrange
    public_key = ""
    public_key_url = "https://example.com/public_key"
    public_key_file_path = f"{uuid.uuid4().hex}.pem"
    mock_from_url.return_value = None
    mock_from_file.return_value = TESTING_PUBLIC_KEY

    # Act
    result = get_public_key(
        public_key=public_key,
        public_key_url=public_key_url,
        public_key_file_path=public_key_file_path,
    )

    # Assert
    mock_from_url.assert_called_once_with(public_key_url)
    mock_from_file.assert_called_once_with(public_key_file_path)
    assert result == TESTING_PUBLIC_KEY


class TestConfig(TestCase):
    url = "https://test.com/public_key"
    issuer = "test-issuer"
    algorithm = "RS256"
    file_path = f"{uuid.uuid4().hex}.pem"

    # @mock.patch("os.getenv")
    def setUp(self):
        # mock_getenv.side_effect = lambda x, default=None: {
        #     "PUBLIC_KEY_URL": self.url,
        #     "JWT_ISSUER": self.issuer,
        #     "JWT_ALGORITHM": self.algorithm,
        #     "PUBLIC_KEY_FILE_PATH": self.file_path,
        # }.get(x, default)

        self.config = Config()

        # assert self.config.public_key is None
        # assert self.config.public_key_url == url
        # assert self.config.jwt_issuer == self.issuer
        # assert self.config.jwt_algorithm == self.algorithm
        # assert self.config.public_key_file_path == self.file_path

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.write_public_key_to_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key")
    def test_update_public_key_ok(self, mock_get_public_key, mock_write_public_key):
        # Arrange
        self.config.public_key = None
        self.config.public_key_url = self.url
        self.config.public_key_file_path = self.file_path
        mock_get_public_key.return_value = TESTING_PUBLIC_KEY

        # Act
        self.config.update_public_key()

        # Assert
        mock_get_public_key.assert_called_once_with(None, self.url, self.file_path)
        mock_write_public_key.assert_called_once_with(
            TESTING_PUBLIC_KEY, self.file_path
        )
        assert self.config.public_key == TESTING_PUBLIC_KEY

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.write_public_key_to_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key")
    def test_update_public_key_ok_with_public_key(
        self, mock_get_public_key, mock_write_public_key
    ):
        # Arrange
        self.config.public_key_url = self.url
        self.config.public_key_file_path = self.file_path
        mock_get_public_key.return_value = TESTING_PUBLIC_KEY

        # Act
        self.config.update_public_key(public_key=TESTING_PUBLIC_KEY)

        # Assert
        mock_get_public_key.assert_called_once_with(
            TESTING_PUBLIC_KEY, self.url, self.file_path
        )
        mock_write_public_key.assert_called_once_with(
            TESTING_PUBLIC_KEY, self.file_path
        )
        assert self.config.public_key == TESTING_PUBLIC_KEY

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.write_public_key_to_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key")
    def test_update_public_key_ok_with_file_path(
        self, mock_get_public_key, mock_write_public_key
    ):
        # Arrange
        self.config.public_key_url = self.url
        self.config.public_key_file_path = "test.pem"
        mock_get_public_key.return_value = TESTING_PUBLIC_KEY

        # Act
        self.config.update_public_key(
            public_key=TESTING_PUBLIC_KEY, public_key_file_path=self.file_path
        )

        # Assert
        mock_get_public_key.assert_called_once_with(
            TESTING_PUBLIC_KEY, self.url, self.file_path
        )
        mock_write_public_key.assert_called_once_with(
            TESTING_PUBLIC_KEY, self.file_path
        )
        assert self.config.public_key == TESTING_PUBLIC_KEY
        assert self.config.public_key_file_path == self.file_path

    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.write_public_key_to_file")
    @mock.patch("mumichaspy.fastapi_jwt_chassis.config.get_public_key")
    def test_update_public_key_error(self, mock_get_public_key, mock_write_public_key):
        # Arrange
        self.config.public_key = None
        self.config.public_key_url = self.url
        self.config.public_key_file_path = self.file_path
        mock_get_public_key.return_value = None

        # Act
        self.config.update_public_key()

        # Assert
        mock_get_public_key.assert_called_once_with(None, self.url, self.file_path)
        mock_write_public_key.assert_not_called()
        assert self.config.public_key is None
