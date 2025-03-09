import json
import logging
import requests
import time
import jwt
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv
from os import environ

load_dotenv(find_dotenv())

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


def get_or_create_user(user_info: Dict[str, Any]) -> Dict[str, str]:
    user_id = user_info.get("sub")
    if not user_id:
        raise AuthError("Missing user ID in token")

    # If user exists, return their info
    if user_id in USER_STORE:
        return USER_STORE[user_id]

    # New user - determine role
    # In a production system, you might have a registration process
    # Here we're assigning based on email domain as an example
    email = user_info.get("email", "")
    if (
        email.endswith("hospital.org")
        or email.endswith("clinic.com")
        or email.endswith("doctor.com")
    ):
        role = "healthcare_provider"
    else:
        role = "patient"

    # Generate a blockchain ID from the user's Web3Auth public key
    # In a real system, this would be their actual blockchain address
    blockchain_id = user_info.get("wallets", {}).get("public_key", user_id)

    # Store user information
    USER_STORE[user_id] = {
        "role": role,
        "blockchain_id": blockchain_id,
        "name": user_info.get("name", "Anonymous"),
        "email": email,
        "created_at": time.time(),
    }

    logger.info(f"Created new user: {blockchain_id} with role {role}")
    return USER_STORE[user_id]


def validate_auth_header(auth_header: str) -> Tuple[str, str, Dict[str, Any]]:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthError("Invalid authorization header")

    token = auth_header.split(" ", 1)[1]
    user_info = verify_web3auth_token(token)
    user_data = get_or_create_user(user_info)

    return user_data["blockchain_id"], user_data["role"], user_data
