import json
import logging
import requests
import time
import jwt
import uuid
import os
from typing import Dict, Optional, Tuple, Any
from functools import lru_cache
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

WEB3AUTH_VERIFIER_URL = "https://authjs.web3auth.io/api/v4/verify_jwt"
WEB3AUTH_CLIENT_ID = os.environ.get("W3A_CLIENT_ID")
AUTH_TOKEN_TIMEOUT = 5  # seconds
TOKEN_CACHE_SIZE = 128
DEFAULT_ROLE = "patient"

# In-memory user store (should be replaced with a database in production)
USER_STORE = {}


@dataclass
class UserInfo:
    """User information data class"""

    blockchain_id: str
    role: str
    name: str
    email: str
    created_at: int


class AuthError(Exception):
    """Authentication error"""


@lru_cache(maxsize=TOKEN_CACHE_SIZE)
def verify_web3auth_token(token: str) -> Dict[str, Any]:
    """
    Verify a Web3Auth token with the Web3Auth verification service.

    Args:
        token: The JWT token from Web3Auth

    Returns:
        Dict containing the validated token payload with user information

    Raises:
        AuthError: If token verification fails for any reason
    """
    if not WEB3AUTH_CLIENT_ID:
        logger.error("WEB3AUTH_CLIENT_ID environment variable not set")
        raise AuthError("Authentication service misconfigured")

    try:
        payload = jwt.decode(token, options={"verify_signature": False})

        if payload.get("exp") and payload["exp"] < time.time():
            logger.warning("Expired token attempted: %s", payload.get("sub", "unknown"))
            raise AuthError("Token has expired")

        verification_data = {
            "verifier_id": "web3auth-core",
            "id_token": token,
            "client_id": WEB3AUTH_CLIENT_ID,
        }

        response = requests.post(
            WEB3AUTH_VERIFIER_URL,
            json=verification_data,
            timeout=AUTH_TOKEN_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            logger.error(
                "Web3Auth verification failed: [%d] %s",
                response.status_code,
                response.text,
            )
            raise AuthError(
                f"Token verification failed with status {response.status_code}"
            )

        result = response.json()
        if not result.get("valid"):
            logger.warning("Invalid token reported by verification service")
            raise AuthError("Token reported as invalid by verification service")

        return payload

    except jwt.DecodeError as e:
        logger.error("JWT decode error: %s", str(e))
        raise AuthError(f"Invalid token format: {e}") from e
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        raise AuthError("Token has expired") from e
    except requests.RequestException as e:
        logger.error("Web3Auth service error: %s", str(e))
        raise AuthError(f"Verification service unavailable: {e}") from e
    except Exception as e:
        logger.error("Unexpected error during token verification: %s", str(e))
        raise AuthError(f"Authentication failed: {e}") from e


def get_or_create_user(user_data: Dict[str, Any]) -> UserInfo:
    """
    Get an existing user or create a new one based on Web3Auth info.

    Args:
        user_data: User information from Web3Auth

    Returns:
        UserInfo object with user details
    """
    user_id = user_data.get("id") or user_data.get("sub")

    if not user_id:
        user_id = str(uuid.uuid4())
        logger.warning("Creating user with generated ID due to missing ID in user_data")

    if user_id in USER_STORE:
        return USER_STORE[user_id]

    user_info = UserInfo(
        blockchain_id=user_data.get("blockchain_id", user_id),
        role=user_data.get("role", DEFAULT_ROLE),
        name=user_data.get("name", "Anonymous"),
        email=user_data.get("email", ""),
        created_at=user_data.get("created_at", int(time.time())),
    )

    USER_STORE[user_id] = user_info
    logger.info(
        "Created new user: %s with role %s", user_info.blockchain_id, user_info.role
    )

    return user_info


def validate_auth_header(auth_header: Optional[str]) -> Tuple[str, str, UserInfo]:
    """
    Validate API key or JWT token from authorization header.

    Args:
        auth_header: Authorization header from request

    Returns:
        Tuple of (blockchain_id, role, user_info)

    Raises:
        AuthError: If authentication fails
    """
    if not auth_header:
        raise AuthError("Missing authorization header")

    auth_parts = auth_header.split(" ", 1)
    if len(auth_parts) != 2:
        raise AuthError("Malformed authorization header")

    auth_type, auth_value = auth_parts

    if auth_type == "ApiKey":
        if not auth_value or len(auth_value) < 32:
            raise AuthError("Invalid API key format")

        user_data = {
            "id": auth_value,
            "role": "healthcare_provider",
            "name": f"Provider {auth_value[:8]}",
            "email": f"provider_{auth_value[:8]}@example.com",
        }

    elif auth_type == "Bearer":
        try:
            user_data = verify_web3auth_token(auth_value)
        except AuthError as e:
            raise AuthError(f"JWT verification failed: {e}") from e

    else:
        raise AuthError(f"Unsupported authentication type: {auth_type}")

    user_info = get_or_create_user(user_data)
    return user_info.blockchain_id, user_info.role, user_info
