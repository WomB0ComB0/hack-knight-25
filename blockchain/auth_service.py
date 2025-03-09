import json
import logging
import requests
import time
import jwt
from typing import Dict, Optional, Tuple, Any
from os import environ
import uuid
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Web3Auth configuration
WEB3AUTH_VERIFIER_URL = "https://authjs.web3auth.io/api/v4/verify_jwt"
WEB3AUTH_CLIENT_ID = environ.get("W3A_CLIENT_ID")

# In-memory user store - in production, this would be a database
USER_STORE = {}


class AuthError(Exception):
    """Authentication error"""
    pass


@lru_cache(maxsize=128)
def verify_web3auth_token(token: str) -> Dict[str, Any]:
    """
    Verify a Web3Auth token with the Web3Auth verification service.

    Args:
        token (str): The JWT token from Web3Auth

    Returns:
        Dict: The token payload with user information

    Raises:
        AuthError: If token verification fails
    """
    try:
        # Verify token structure and expiration locally first
        payload = jwt.decode(token, options={"verify_signature": False})

        # Check token expiration
        if payload.get("exp") and payload["exp"] < time.time():
            raise AuthError("Token has expired")

        # Verify with Web3Auth service
        verification_data = {
            "verifier_id": "web3auth-core",
            "id_token": token,
            "client_id": WEB3AUTH_CLIENT_ID,
        }

        response = requests.post(
            WEB3AUTH_VERIFIER_URL,
            json=verification_data,
            timeout=5,
        )

        if response.status_code != 200:
            logger.error(f"Web3Auth verification failed: {response.text}")
            raise AuthError("Token verification failed")

        result = response.json()
        if not result.get("valid"):
            raise AuthError("Invalid token")

        return payload

    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise AuthError(f"Invalid token format: {str(e)}")
    except requests.RequestException as e:
        logger.error(f"Web3Auth service error: {str(e)}")
        raise AuthError(f"Verification service error: {str(e)}")


def get_or_create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get an existing user or create a new one based on Web3Auth info.

    Args:
        user_data: User information from Web3Auth

    Returns:
        Dict with user role and blockchain ID
    """
    # Ensure we have a user ID
    user_id = user_data.get("id", str(uuid.uuid4()))

    # Return existing user if found
    if user_id in USER_STORE:
        return USER_STORE[user_id]

    # Create new user
    user_info = {
        "role": user_data.get("role", "patient"),
        "blockchain_id": user_data.get("blockchain_id", user_id),
        "name": user_data.get("name", "Anonymous"),
        "email": user_data.get("email", ""),
        "created_at": user_data.get("created_at", int(time.time())),
    }

    # Store and log new user
    USER_STORE[user_id] = user_info
    logger.info(f"Created new user: {user_info['blockchain_id']} with role {user_info['role']}")

    return user_info


def validate_auth_header(auth_header: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Validate API key authorization header.

    Args:
        auth_header: Authorization header from request

    Returns:
        Tuple of (blockchain_id, role, user_info)

    Raises:
        AuthError: If authentication fails
    """
    if not auth_header or not auth_header.startswith("ApiKey "):
        raise AuthError("Invalid authorization header")

    api_key = auth_header.split(" ", 1)[1]

    # Create user based on API key
    user_data = {
        "id": api_key,
        "role": "healthcare_provider",
        "name": f"User {api_key[:8]}",
        "email": f"user_{api_key[:8]}@example.com",
    }

    user_info = get_or_create_user(user_data)

    return user_info["blockchain_id"], user_info["role"], user_info
