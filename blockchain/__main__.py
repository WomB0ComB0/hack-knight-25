from configparser import ConfigParser
import os
import logging
import secrets

from .app import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Starting application")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.addHandler(logging.StreamHandler())

config = ConfigParser()
config.read("config.ini")


if __name__ == "__main__":
    key_path = "medical_encryption.key"
    if os.path.exists(key_path):
        try:
            with open(file=key_path, mode="w", encoding="utf-8") as f:
                f.write(secrets.token_hex(32))
            logger.info("Overwritten existing encryption key at %s", key_path)
        except (PermissionError, IsADirectoryError) as e:
            logger.error("Failed to overwrite encryption key: %s", str(e))
            raise
    else:
        try:
            if not os.path.exists(os.path.dirname(key_path)):
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(file=key_path, mode="w", encoding="utf-8") as f:
                f.write(secrets.token_hex(32))
            logger.info("Generated new encryption key at %s", key_path)
        except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
            logger.error("Failed to create encryption key: %s", str(e))
            raise

    host = config.get("HOST", "host", fallback="127.0.0.1")
    port = config.getint("HOST", "port", fallback=5000)
    debug = config.getboolean("DEBUG", "debug", fallback=False)

    logger.info("Starting Flask app on %s:%s (debug=%s)", host, port, debug)
    app.run(
        host=host,
        port=port,
        debug=debug,
    )
