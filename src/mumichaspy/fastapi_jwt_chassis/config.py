import os
import logging


logger = logging.getLogger(__name__)


class Config:
    public_key = None
    public_key_url = os.getenv("PUBLIC_KEY_URL", "https://auth.example.com/pk")
    jwt_issuer = os.getenv("JWT_ISSUER", "mu-sse")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "RS256")

    def __init__(self):
        self.update_public_key()

    def update_public_key(self):
        import httpx

        try:
            with httpx.Client() as client:
                response = client.get(self.public_key_url)
                if response.status_code == 200:
                    self.public_key = response.text
                    with open("public_key.pem", "w") as f:
                        f.write(self.public_key)

        except Exception as e:
            logger.error(
                "Last public key will be loaded from file. Error loading public key: "
                + str(e)
            )

            # load last public key from file
            with open("public_key.pem", "r") as f:
                self.public_key = f.read()


config = Config()
