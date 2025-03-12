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
from cryptography.fernet import InvalidToken

logger = logging.getLogger("blockchain.exceptions")


class BlockchainException(Exception):
    """
    Base exception class for all blockchain-related exceptions.

    This class serves as the parent exception for all specialized blockchain
    exceptions in the system. It provides a common interface for error handling
    and reporting with standardized error codes.

    Attributes:
        message (str): Human-readable description of the error
        error_code (int): Numeric code identifying the error type

    Args:
        message (str): Description of the error. Defaults to "An error occurred in the blockchain"
        error_code (int): Numeric error code. Defaults to 1000

    Example:
        ```python
        # Raising a basic blockchain exception
        raise BlockchainException("Failed to create block", 1050)
        ```
    """

    def __init__(
        self,
        message: str = "An error occurred in the blockchain",
        error_code: int = 1000,
    ):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class EncryptionException(BlockchainException):
    """
    Exception for encryption/decryption errors.

    This exception is raised when encryption or decryption operations fail,
    such as invalid keys, corrupted data, or incompatible encryption formats.

    Attributes:
        message (str): Human-readable description of the encryption error
        error_code (int): Numeric code identifying the encryption error type

    Args:
        message (str): Description of the error. Defaults to "Encryption or decryption operation failed"
        error_code (int): Numeric error code. Defaults to 1001

    Example:
        ```python
        # Raising an encryption exception
        raise EncryptionException("Invalid encryption key format")
        ```
    """

    def __init__(
        self,
        message: str = "Encryption or decryption operation failed",
        error_code: int = 1001,
    ):
        super().__init__(message, error_code)


class SignatureException(BlockchainException):
    """
    Exception for signature verification errors.

    This exception is raised when digital signatures fail verification,
    indicating potential data tampering or invalid signing keys.

    Attributes:
        message (str): Human-readable description of the signature error
        error_code (int): Numeric code identifying the signature error type

    Args:
        message (str): Description of the error. Defaults to "Signature verification failed"
        error_code (int): Numeric error code. Defaults to 1002

    Example:
        ```python
        # Raising a signature exception
        raise SignatureException("Signature does not match transaction data")
        ```
    """

    def __init__(
        self, message: str = "Signature verification failed", error_code: int = 1002
    ):
        super().__init__(message, error_code)


class TransactionException(BlockchainException):
    """
    Exception for transaction-related errors.

    This exception is raised when errors occur during transaction creation,
    validation, submission, or processing within the blockchain.

    Attributes:
        message (str): Human-readable description of the transaction error
        error_code (int): Numeric code identifying the transaction error type

    Args:
        message (str): Description of the error. Defaults to "Transaction operation failed"
        error_code (int): Numeric error code. Defaults to 1003

    Example:
        ```python
        # Raising a transaction exception
        raise TransactionException("Insufficient funds for transaction")
        ```
    """

    def __init__(
        self, message: str = "Transaction operation failed", error_code: int = 1003
    ):
        super().__init__(message, error_code)


class NodeConnectionException(BlockchainException):
    """
    Exception for node network connection errors.

    This exception is raised when the system fails to connect to blockchain nodes,
    indicating network issues, node unavailability, or configuration problems.

    Attributes:
        message (str): Human-readable description of the connection error
        error_code (int): Numeric code identifying the connection error type

    Args:
        message (str): Description of the error. Defaults to "Failed to connect to blockchain node"
        error_code (int): Numeric error code. Defaults to 1004

    Example:
        ```python
        # Raising a node connection exception
        raise NodeConnectionException("Node at 192.168.1.10:8080 is unreachable")
        ```
    """

    def __init__(
        self,
        message: str = "Failed to connect to blockchain node",
        error_code: int = 1004,
    ):
        super().__init__(message, error_code)


class ValidationException(BlockchainException):
    """
    Exception for blockchain validation errors.

    This exception is raised when blockchain data fails validation checks,
    such as invalid block structure, broken chain integrity, or consensus rules violations.

    Attributes:
        message (str): Human-readable description of the validation error
        error_code (int): Numeric code identifying the validation error type

    Args:
        message (str): Description of the error. Defaults to "Blockchain validation failed"
        error_code (int): Numeric error code. Defaults to 1005

    Example:
        ```python
        # Raising a validation exception
        raise ValidationException("Invalid block hash: does not meet difficulty requirement")
        ```
    """

    def __init__(
        self, message: str = "Blockchain validation failed", error_code: int = 1005
    ):
        super().__init__(message, error_code)


class MedicalRecordException(BlockchainException):
    """
    Exception for medical record operations.

    This exception is raised when operations on medical records stored in the blockchain
    fail, such as during creation, retrieval, updating, or permission management.

    Attributes:
        message (str): Human-readable description of the medical record error
        error_code (int): Numeric code identifying the medical record error type

    Args:
        message (str): Description of the error. Defaults to "Medical record operation failed"
        error_code (int): Numeric error code. Defaults to 1006

    Example:
        ```python
        # Raising a medical record exception
        raise MedicalRecordException("Patient ID not found in the system")
        ```
    """

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
    Decorator for handling exceptions with custom mapping and fallback handlers.

    This decorator wraps a function to provide structured exception handling with
    customizable exception type-to-handler mappings. It allows for specific handling
    of different exception types and provides a fallback mechanism for uncaught exceptions.

    Args:
        *exception_map: Variable number of dictionaries mapping exception types to handler functions.
            Each handler function should accept the exception as an argument and return a value
            that will be used as the return value of the decorated function when that exception occurs.
        fallback_handler: Optional function to handle any uncaught exceptions.
            If not provided and an exception isn't explicitly handled, a BlockchainException is raised.
        log_traceback: Whether to log the full traceback (True) or just the exception message (False).
            Defaults to True.

    Returns:
        Callable: The decorated function with exception handling.

    Raises:
        BlockchainException: If an uncaught exception occurs and no fallback_handler is provided.

    Example:
        ```python
        # Define exception handlers
        db_handlers = {
            DatabaseConnectionError: lambda e: {"success": False, "error": "Database unavailable"},
            IntegrityError: lambda e: {"success": False, "error": "Data integrity violation"}
        }

        validation_handlers = {
            ValueError: lambda e: {"success": False, "error": f"Invalid value: {str(e)}"},
            TypeError: lambda e: {"success": False, "error": f"Type error: {str(e)}"}
        }

        # Apply the decorator with multiple handler mappings
        @handle_exceptions(db_handlers, validation_handlers,
                          fallback_handler=default_fallback_handler,
                          log_traceback=True)
        def create_user(user_data):
            # Function implementation that might raise exceptions
            pass
        ```
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
                        "Unhandled exception in %s:\n%s", 
                        func.__name__, 
                        traceback.format_exc()
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
    """
    Default fallback handler that converts exceptions to a standardized response dictionary.

    This handler creates a consistent error response format when exceptions occur,
    which is particularly useful for APIs and service interfaces.

    Args:
        exception (Exception): The exception that was caught

    Returns:
        Dict[str, Any]: A dictionary containing standardized error information with keys:
            - success: Always False, indicating failure
            - error: Generic error message
            - error_code: Standard error code (9999) for unhandled exceptions
            - error_type: The name of the exception class

    Example:
        ```python
        # Using the default fallback handler
        try:
            # Some operation that might fail
            result = perform_risky_operation()
        except Exception as e:
            response = default_fallback_handler(e)
            return response  # Returns a standardized error dictionary
        ```
    """
    return {
        "success": False,
        "error": "An unexpected error occurred",
        "error_code": 9999,
        "error_type": type(exception).__name__,
        "traceback": traceback.format_exc()
    }


def encrypt_with_exception_handling(blockchain, data: Any) -> Optional[str]:
    """
    Encrypt data with comprehensive exception handling.

    This function demonstrates how to use the exception handling decorator
    to safely encrypt data with proper error handling for various exception types
    that might occur during encryption.

    Args:
        blockchain: The blockchain object containing the encryption_key
        data (Any): The data to encrypt. Can be any JSON-serializable object.
            If None or empty, the function returns None without attempting encryption.

    Returns:
        Optional[str]: Base64-encoded encrypted string if successful, None if encryption fails
                      or if input data is empty/None.

    Raises:
        No exceptions are raised directly from this function due to exception handling,
        but the underlying encryption might encounter:
        - TypeError: If data cannot be properly serialized
        - JSONDecodeError: If there are issues converting data to JSON
        - InvalidToken: If there are Fernet token issues

    Example:
        ```python
        # Encrypt user data
        user_data = {"id": 12345, "name": "John Doe", "access_level": 3}
        encrypted_data = encrypt_with_exception_handling(blockchain_instance, user_data)

        if encrypted_data:
            # Store or transmit the encrypted data
            store_in_database(encrypted_data)
        else:
            # Handle encryption failure
            notify_admin("Failed to encrypt user data")
        ```
    """

    # Define exception handlers for encryption-specific issues
    encryption_handlers = {
        TypeError: lambda e: logger.error(
            "Type error during encryption: %s\n%s", str(e), traceback.format_exc()
        ) or None,
        json.JSONDecodeError: lambda e: logger.error(
            "JSON error during encryption: %s\n%s", str(e), traceback.format_exc()
        ) or None,
        InvalidToken: lambda e: logger.error(
            "Invalid Fernet token: %s\n%s", str(e), traceback.format_exc()
        ) or None,
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
