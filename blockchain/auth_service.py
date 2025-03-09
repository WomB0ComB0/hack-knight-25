import json
import logging
import requests
import time
import jwt
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv
from os import environ
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Web3Auth configuration
WEB3AUTH_VERIFIER_URL = "https://authjs.web3auth.io/api/v4/verify_jwt"
WEB3AUTH_CLIENT_ID = environ.get("W3A_CLIENT_ID")

# User role mapping store - in production, this would be a database
# Format: {web3auth_user_id: {"role": "patient|healthcare_provider", "blockchain_id": "hash"}}
USER_STORE = {}


class AuthError(Exception):
    """Authentication error"""

    pass


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
        # First verify token structure and expiration locally
        # We'll still send it to Web3Auth for full verification
        payload = jwt.decode(token, options={"verify_signature": False})

        # Check if token is expired
        if payload.get("exp") and payload["exp"] < time.time():
            raise AuthError("Token has expired")

        # Verify with Web3Auth service
        response = requests.post(
            WEB3AUTH_VERIFIER_URL,
            json={
                "verifier_id": "web3auth-core",  # Default verifier for Web3Auth
                "id_token": token,
                "client_id": WEB3AUTH_CLIENT_ID,
            },
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


def get_or_create_user(user_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Get an existing user or create a new one based on Web3Auth info.

    Args:
        user_data: User information from Web3Auth

    Returns:
        Dict with user role and blockchain ID
    """
    user_id = user_data.get("id")
    if not user_id:
        user_id = str(uuid.uuid4())

    # If user exists, return their info
    if user_id in USER_STORE:
        return USER_STORE[user_id]

    # New user with provided information
    role = user_data.get("role", "patient")
    blockchain_id = user_data.get("blockchain_id", user_id)

    # Store user information
    USER_STORE[user_id] = {
        "role": role,
        "blockchain_id": blockchain_id,
        "name": user_data.get("name", "Anonymous"),
        "email": user_data.get("email", ""),
        "created_at": user_data.get("created_at", 0),
    }

    logger.info(f"Created new user: {blockchain_id} with role {role}")
    return USER_STORE[user_id]


def validate_auth_header(auth_header: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Validate API key authorization header.

    Args:
        auth_header: Authorization header from request

    Returns:
        Tuple of (user_id, role, user_info)

    Raises:
        AuthError: If authentication fails
    """
    if not auth_header or not auth_header.startswith("ApiKey "):
        raise AuthError("Invalid authorization header")

    api_key = auth_header.split(" ", 1)[1]

    # In a real application, you'd validate the API key against a database
    # For simplicity, we'll create a user based on the API key
    user_data = {
        "id": api_key,
        "role": "healthcare_provider",
        "name": f"User {api_key[:8]}",
        "email": f"user_{api_key[:8]}@example.com",
    }

    user_info = get_or_create_user(user_data)

    return user_info["blockchain_id"], user_info["role"], user_info
