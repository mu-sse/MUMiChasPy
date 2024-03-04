import os
import logging


logger = logging.getLogger(__name__)


def get_public_key_from_url(public_key_url: str):
    """Upload public key from URL."""

    import httpx

    public_key = None

    if public_key_url is None or public_key_url == "":
        logger.warning("No public key URL provided")
        return None

    try:
        with httpx.Client() as client:
            response = client.get(public_key_url)

            if response.status_code != 200:
                raise Exception(f"Status code: {response.status_code}")

            public_key = response.text

    except Exception as e:
        logger.warning("Could not load public key from URL: " + str(e))

    return public_key


def get_public_key_from_file(file_path: str):
    """Get public key from pem file."""
    public_key = None
    try:
        if not os.path.isfile(file_path):
            raise Exception("Public key file not found")

        with open(file_path, "r") as f:
            public_key = f.read()

    except Exception as e:
        logger.warning("Could not load public key from file: " + str(e))

    return public_key


def write_public_key_to_file(public_key: str, file_path: str):
    """Write public key to file."""
    try:
        with open(file_path, "w") as f:
            f.write(public_key)
    except Exception as e:
        logger.warning("Could not write public key to file: " + str(e))


def get_public_key(
    public_key: str = None,
    public_key_url: str = None,
    public_key_file_path: str = None,
):
    """Get public key."""

    if public_key is None or public_key == "":
        public_key = get_public_key_from_url(public_key_url)

    if public_key is None or public_key == "":
        public_key = get_public_key_from_file(public_key_file_path)

    return public_key


class Config:
    public_key = None
    public_key_url = os.getenv("PUBLIC_KEY_URL", "")
    jwt_issuer = os.getenv("JWT_ISSUER", "mu-sse")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "RS256")
    public_key_file_path = os.getenv("PUBLIC_KEY_FILE_PATH", "public_key.pem")

    def __init__(self):
        self.update_public_key()

    def update_public_key(self, public_key=None, public_key_file_path=None):
        """Update public key."""
        if public_key_file_path is not None:
            self.public_key_file_path = public_key_file_path

        public_key = get_public_key(
            public_key, self.public_key_url, self.public_key_file_path
        )

        if public_key is not None and public_key != "":
            self.public_key = public_key
            write_public_key_to_file(self.public_key, self.public_key_file_path)

        else:
            logger.error("No public key available")


config = Config()
