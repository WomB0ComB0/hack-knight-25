#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0611,W0718

import base64
import json
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from cryptography.fernet import Fernet

logger = logging.getLogger("blockchain.exceptions")


class BlockchainException(Exception):
    """Base exception class for all blockchain-related exceptions."""

    def __init__(
        self,
        message: str = "An error occurred in the blockchain",
        error_code: int = 1000,
    ):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class EncryptionException(BlockchainException):
    """Exception for encryption/decryption errors."""

    def __init__(
        self,
        message: str = "Encryption or decryption operation failed",
        error_code: int = 1001,
    ):
        super().__init__(message, error_code)


class SignatureException(BlockchainException):
    """Exception for signature verification errors."""

    def __init__(
        self, message: str = "Signature verification failed", error_code: int = 1002
    ):
        super().__init__(message, error_code)


class TransactionException(BlockchainException):
    """Exception for transaction-related errors."""

    def __init__(
        self, message: str = "Transaction operation failed", error_code: int = 1003
    ):
        super().__init__(message, error_code)


class NodeConnectionException(BlockchainException):
    """Exception for node network connection errors."""

    def __init__(
        self,
        message: str = "Failed to connect to blockchain node",
        error_code: int = 1004,
    ):
        super().__init__(message, error_code)


class ValidationException(BlockchainException):
    """Exception for blockchain validation errors."""

    def __init__(
        self, message: str = "Blockchain validation failed", error_code: int = 1005
    ):
        super().__init__(message, error_code)


class MedicalRecordException(BlockchainException):
    """Exception for medical record operations."""

    def __init__(
        self, message: str = "Medical record operation failed", error_code: int = 1006
    ):
        super().__init__(message, error_code)


def handle_exceptions(
    *exception_map: Dict[Type[Exception], Callable[[Exception], Any]],
    fallback_handler: Optional[Callable[[Exception], Any]] = None,
    log_traceback: bool = True,
) -> Callable:
    """
    Decorator for handling exceptions with custom mapping and fallback.

    Args:
        *exception_map: A dictionary mapping exception types to handler functions
        fallback_handler: Handler for any uncaught exceptions
        log_traceback: Whether to log the full traceback

    Returns:
        The decorated function
    """
    exception_handlers = {}
    for mapping in exception_map:
        exception_handlers.update(mapping)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exception_type = type(e)

                for exc_type, handler in exception_handlers.items():
                    if isinstance(e, exc_type):
                        logger.debug(
                            "Handling %s with specific handler", exception_type.__name__
                        )
                        return handler(e)

                if log_traceback:
                    logger.error(
                        "Unhandled exception in %s:", func.__name__, exc_info=True
                    )
                else:
                    logger.error("Unhandled exception in %s: %s", func.__name__, str(e))

                if fallback_handler:
                    return fallback_handler(e)
                else:
                    raise BlockchainException(f"Unexpected error: {str(e)}") from e

        return wrapper

    return decorator


def default_fallback_handler(exception: Exception) -> Dict[str, Any]:
    """Default fallback handler that converts exceptions to a standardized response dict."""
    return {
        "success": False,
        "error": "An unexpected error occurred",
        "error_code": 9999,
        "error_type": type(exception).__name__,
    }


def encrypt_with_exception_handling(blockchain, data: Any) -> Optional[str]:
    """Example of using the exception handler with your encryption method."""

    encryption_handlers = {
        TypeError: lambda e: logger.error("Type error during encryption: %s", str(e))
        or None,
        json.JSONDecodeError: lambda e: logger.error(
            "JSON error during encryption: %s", str(e)
        )
        or None,
        Fernet.InvalidToken: lambda e: logger.error("Invalid Fernet token: %s", str(e))
        or None,
    }

    @handle_exceptions(encryption_handlers, fallback_handler=default_fallback_handler)
    def _encrypt():
        if not data:
            return None

        f = Fernet(blockchain.encryption_key)
        json_data = json.dumps(data)
        encrypted_data = f.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()

    return _encrypt()
