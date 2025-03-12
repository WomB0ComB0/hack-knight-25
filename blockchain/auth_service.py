#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0611,W0718

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

"""
# Authentication Module for Web3Auth Integration

This module provides authentication capabilities for applications using Web3Auth 
and optional API key authentication. It handles JWT token verification, user management,
and authentication header validation.

## Key Features

- Web3Auth JWT token verification with caching
- Basic user management (in-memory, should be replaced in production)
- Support for both JWT token and API key authentication
- Role-based access management
- Comprehensive error handling and logging

## Configuration

The module requires the following environment variables:
- `W3A_CLIENT_ID`: Web3Auth Client ID for token verification

## Constants
- `WEB3AUTH_VERIFIER_URL`: URL for the Web3Auth token verification service
- `AUTH_TOKEN_TIMEOUT`: Timeout for Web3Auth verification requests (seconds)
- `TOKEN_CACHE_SIZE`: Maximum size of the token verification cache
- `DEFAULT_ROLE`: Default role assigned to new users

## Usage Example

```python
# Validating an authentication header from a request
try:
    auth_header = request.headers.get("Authorization")
    blockchain_id, role, user_info = validate_auth_header(auth_header)

    # Use the authenticated user information
    if role == "healthcare_provider":
        # Allow healthcare provider specific actions
        pass
    elif role == "patient":
        # Allow patient specific actions
        pass

except AuthError as e:
    # Handle authentication failure
    return {"error": str(e)}, 401
```

## Security Considerations

- In production, replace the in-memory `USER_STORE` with a proper database
- Consider adding rate limiting for authentication attempts
- Review and adjust the default role assignment policy
- API keys should be properly generated with sufficient entropy
"""

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
    """
    User information data class

    Attributes:
        blockchain_id (str): Unique identifier for the user, often from blockchain
        role (str): User's role in the system (e.g., "patient", "healthcare_provider")
        name (str): User's display name
        email (str): User's email address
        created_at (int): Unix timestamp when the user was created
    """

    blockchain_id: str
    role: str
    name: str
    email: str
    created_at: int


class AuthError(Exception):
    """
    Authentication error

    This exception is raised for any authentication-related failures,
    including invalid tokens, expired tokens, service unavailability,
    or malformed authentication headers.
    """


@lru_cache(maxsize=TOKEN_CACHE_SIZE)
def verify_web3auth_token(token: str) -> Dict[str, Any]:
    """
    Verify a Web3Auth token with the Web3Auth verification service.

    This function validates the authenticity of a JWT token issued by Web3Auth.
    It first performs a local check for token expiration, then verifies the token
    with the Web3Auth verification service. Results are cached to improve performance
    for repeated verification requests with the same token.

    Args:
        token (str): The JWT token from Web3Auth

    Returns:
        Dict[str, Any]: Dictionary containing the validated token payload with user information

    Raises:
        AuthError: If token verification fails for any reason, including:
            - Missing WEB3AUTH_CLIENT_ID environment variable
            - Token format errors
            - Expired tokens
            - Failed verification from Web3Auth service
            - Network errors when contacting the verification service

    Example:
        ```python
        try:
            user_data = verify_web3auth_token(token)
            user_id = user_data.get("sub")
            # Process authenticated user
        except AuthError as e:
            # Handle authentication failure
            print(f"Authentication failed: {e}")
        ```
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
    except jwt.ExpiredSignatureError as e:
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
    Get an existing user or create a new one based on authentication data.

    This function checks if a user exists in the user store and returns that user
    if found. Otherwise, it creates a new user with the provided information.

    Args:
        user_data (Dict[str, Any]): User information from authentication source
            This dictionary may contain:
            - id or sub: Unique identifier for the user
            - blockchain_id: Optional blockchain identifier
            - role: Optional user role (defaults to DEFAULT_ROLE)
            - name: Optional user name (defaults to "Anonymous")
            - email: Optional user email (defaults to empty string)
            - created_at: Optional timestamp of user creation (defaults to current time)

    Returns:
        UserInfo: User information object containing user details

    Note:
        In a production environment, this function should be modified to use
        a persistent database instead of the in-memory USER_STORE.

    Example:
        ```python
        user_data = {
            "id": "user123",
            "name": "Alice Smith",
            "email": "alice@example.com",
            "role": "healthcare_provider"
        }
        user = get_or_create_user(user_data)
        ```
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

    This function parses and validates the Authorization header from a request,
    supporting two authentication methods:
    1. API Key: Format "ApiKey {key}"
    2. JWT Token: Format "Bearer {token}"

    The function returns user identification information after successful
    authentication, retrieving or creating a user record as needed.

    Args:
        auth_header (Optional[str]): Authorization header from HTTP request
            Expected format is either:
            - "ApiKey {api_key}" for API key authentication
            - "Bearer {jwt_token}" for Web3Auth JWT authentication

    Returns:
        Tuple[str, str, UserInfo]: A tuple containing:
            - blockchain_id (str): User's blockchain identifier
            - role (str): User's role in the system
            - user_info (UserInfo): Complete user information object

    Raises:
        AuthError: If authentication fails for any reason, including:
            - Missing authorization header
            - Malformed header format
            - Invalid API key format
            - Failed JWT verification
            - Unsupported authentication type

    Example:
        ```python
        # In a web framework route handler
        try:
            auth_header = request.headers.get("Authorization")
            blockchain_id, role, user_info = validate_auth_header(auth_header)

            if role == "admin":
                # Allow admin actions
                pass
            else:
                # Regular user actions
                pass

        except AuthError as e:
            return {"error": str(e)}, 401
        ```
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
