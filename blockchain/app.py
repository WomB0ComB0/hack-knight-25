#!/usr/env/bin python
# -*- coding: utf-8 -*-
# pylint: disable=

"""
Healthcare Blockchain API
========================

This module provides a Flask-based RESTful API for a healthcare blockchain system.
It allows for secure management of medical records, patient consent, and transaction
processing on a distributed blockchain network.

Key Features:
- Secure medical record storage and access control
- Patient consent management for healthcare providers
- Blockchain-based transaction processing and validation
- User authentication and authorization
- Node consensus and conflict resolution

Environment Variables:
- DEV_API_KEY: API key for development mode
- FLASK_ENV: Set to 'development' to enable dev features

Dependencies:
- Flask
- flask-cors
- blockchain.blockchain module (local)
- blockchain.auth_service module (local)

Usage:
Run with python app.py [options]
Options:
  -p, --port PORT     Port to listen on (default: 5000)
  -h, --host HOST     Host to listen on (default: 0.0.0.0)
  --debug             Enable debug mode
"""

import time
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from uuid import uuid4
from functools import wraps
import logging
from typing import Any, Dict, List, Optional, Callable
import os

from blockchain import Blockchain, MINING_SENDER, MINING_REWARD, RECORD_TYPES
from auth_service import validate_auth_header, AuthError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
blockchain = Blockchain()
node_identifier = str(uuid4()).replace("-", "")

DEV_API_KEY = os.environ.get("DEV_API_KEY", "dev-api-key-for-testing")
DEV_MODE = os.environ.get("FLASK_ENV") == "development"

USER_STORE = {}


def validate_json_request(required_fields: Optional[List[str]] = None) -> Callable:
    """
    Decorator to validate JSON requests and required fields.

    This decorator ensures that:
    1. The request body is valid JSON
    2. All specified required fields are present in the request

    Args:
        required_fields: List of field names that must be present in the JSON request

    Returns:
        Decorated function that validates the request before executing the endpoint handler

    Example:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json_request(['user_id', 'data'])
        def my_endpoint():
            # This will only execute if the request contains valid JSON with 'user_id' and 'data' fields
            ...
    """

    def decorator(f: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Response:
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            try:
                request_data = request.get_json()
            except (
                ValueError,
                TypeError,
                AttributeError,
            ) as e:
                logger.error("Invalid JSON: %s", str(e))
                return jsonify({"error": "Invalid JSON format"}), 400

            if required_fields:
                missing_fields = [
                    field for field in required_fields if field not in request_data
                ]
                if missing_fields:
                    missing_str = ", ".join(missing_fields)
                    return (
                        jsonify({"error": f"Missing required fields: {missing_str}"}),
                        400,
                    )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def authorize_healthcare_access(f: Callable[[Any], Any]) -> Callable:
    """
    Decorator to validate healthcare access authorization.

    This decorator:
    1. Validates the Authorization header
    2. In development mode, allows API key authentication
    3. Sets user context in the request object (user_id, user_role, user_info)

    Args:
        f: The function to decorate

    Returns:
        Decorated function that validates authorization before executing the endpoint handler

    Example:
        @app.route('/medical/records', methods=['GET'])
        @authorize_healthcare_access
        def get_records():
            # This will only execute for authenticated users
            # Access request.user_id, request.user_role, request.user_info
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs) -> Response:
        auth_header = request.headers.get("Authorization")

        if DEV_MODE and auth_header == f"ApiKey {DEV_API_KEY}":
            request.user_id = "dev-doctor-id"
            request.user_role = "healthcare_provider"
            request.user_info = {"name": "Dev Doctor", "email": "dev@example.com"}
            return f(*args, **kwargs)

        try:
            user_id, role, user_info = validate_auth_header(auth_header)

            request.user_id = user_id
            request.user_role = role
            request.user_info = user_info

            return f(*args, **kwargs)

        except AuthError as e:
            logger.error("Authentication error: %s", str(e))
            return jsonify({"error": str(e)}), 401

    return decorated_function


@app.errorhandler(404)
def not_found(error) -> Response:  # pylint: disable=W0613
    """
    Handle 404 Not Found errors.

    Args:
        error: The error object from Flask

    Returns:
        JSON response with 404 status code
    """
    logger.error("Resource not found: %s", str(error))
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error) -> Response:
    """
    Handle 500 Internal Server errors.

    Args:
        error: The error object from Flask

    Returns:
        JSON response with 500 status code
    """
    logger.error("Internal server error: %s", str(error))
    return jsonify({"error": "Internal server error"}), 500


@app.route("/", methods=["GET"])
def home() -> Response:
    """
    API homepage with endpoint information.

    Returns:
        JSON response containing API status and available endpoints

    Example response:
        {
            "message": "Blockchain API is running",
            "status": "success",
            "version": "1.0",
            "endpoints": {
                "GET /": "Home - This information",
                "GET /chain": "Get the full blockchain",
                ...
            }
        }
    """
    return (
        jsonify(
            {
                "message": "Blockchain API is running",
                "status": "success",
                "version": "1.0",
                "endpoints": {
                    "GET /": "Home - This information",
                    "GET /chain": "Get the full blockchain",
                    "GET /mine": "Mine a new block",
                    "POST /transactions/new": "Create a new transaction",
                    "GET /transactions/pending": "Get pending transactions",
                    "POST /nodes/register": "Register new nodes",
                    "GET /nodes/resolve": "Resolve conflicts between nodes",
                    "GET /nodes/get": "Get registered nodes",
                },
            }
        ),
        200,
    )


@app.route("/transactions/new", methods=["POST"])
@validate_json_request(required_fields=["sender", "recipient", "amount", "signature"])
def new_transaction() -> Response:
    """
    Create a new transaction in the blockchain.

    Required JSON fields:
        sender: String - Sender's wallet address
        recipient: String - Recipient's wallet address
        amount: Number - Transaction amount (must be positive)
        signature: String - Digital signature (can be empty for mining rewards)

    Returns:
        JSON response with transaction details and status code 201 if successful

    Error cases:
        - 400: Invalid parameters (non-positive amount, invalid addresses)
        - 406: Signature verification failed
        - 500: Internal processing error

    Example request:
        POST /transactions/new
        {
            "sender": "wallet_address_1",
            "recipient": "wallet_address_2",
            "amount": 10.5,
            "signature": "digital_signature_data"
        }

    Example response:
        {
            "message": "Transaction will be added to Block 5",
            "transaction": {
                "sender": "wallet_address_1",
                "recipient": "wallet_address_2",
                "amount": 10.5
            }
        }
    """
    values = request.get_json()

    try:
        amount = float(values["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    sender = values["sender"]
    recipient = values["recipient"]

    if len(sender) < 10 or len(recipient) < 10:
        return jsonify({"error": "Invalid sender or recipient address"}), 400

    signature = values["signature"]
    if not signature and sender != MINING_SENDER:
        return jsonify({"error": "Transaction requires a valid signature"}), 400

    try:
        transaction_result = blockchain.submit_transaction(
            sender, recipient, amount, signature
        )
    except (
        ValueError,
        TypeError,
        KeyError,
    ) as e:
        logger.error("Transaction submission error: %s", str(e))
        return jsonify({"error": f"Transaction processing error: {str(e)}"}), 500

    if transaction_result:
        response = {
            "message": f"Transaction will be added to Block {transaction_result}",
            "transaction": {"sender": sender, "recipient": recipient, "amount": amount},
        }
        logger.info("New transaction: %s -> %s, %s", sender, recipient, amount)
        return jsonify(response), 201

    return (
        jsonify({"error": "Invalid transaction - signature verification failed"}),
        406,
    )


@app.route("/transactions/pending", methods=["GET"])
def get_pending_transactions() -> Response:
    """
    Get all pending transactions that haven't been included in a block yet.

    Returns:
        JSON response with array of pending transactions and count

    Example response:
        {
            "pending_transactions": [
                {
                    "sender": "wallet_address_1",
                    "recipient": "wallet_address_2",
                    "amount": 10.5,
                    "signature": "digital_signature_data",
                    "timestamp": 1634567890.123
                }
            ],
            "count": 1
        }
    """
    return (
        jsonify(
            {
                "pending_transactions": blockchain.transactions,
                "count": len(blockchain.transactions),
            }
        ),
        200,
    )


@app.route("/chain", methods=["GET"])
def full_chain() -> Response:
    """
    Get the full blockchain with pagination support.

    Query parameters:
        start: Integer - Starting block index (default: 0)
        limit: Integer - Maximum number of blocks to return (default: all blocks)

    Returns:
        JSON response with chain data and metadata

    Example request:
        GET /chain?start=10&limit=5

    Example response:
        {
            "chain": [
                {
                    "index": 10,
                    "timestamp": 1634567890.123,
                    "transactions": [...],
                    "nonce": 12345,
                    "previous_hash": "hash_of_block_9"
                },
                ...
            ],
            "length": 100,
            "start": 10,
            "limit": 5,
            "returned_blocks": 5
        }
    """
    start = request.args.get("start", default=0, type=int)
    limit = request.args.get("limit", default=len(blockchain.chain), type=int)

    start = max(0, start)
    limit = max(1, limit)
    if start >= len(blockchain.chain):
        start = max(0, len(blockchain.chain) - 1)

    chain_slice = blockchain.chain[start : start + limit]

    return (
        jsonify(
            {
                "chain": chain_slice,
                "length": len(blockchain.chain),
                "start": start,
                "limit": limit,
                "returned_blocks": len(chain_slice),
            }
        ),
        200,
    )


@app.route("/mine", methods=["GET"])
def mine() -> Response:
    """
    Mine a new block and add it to the blockchain.

    This will:
    1. Create a mining reward transaction for the current node
    2. Execute proof-of-work algorithm to find a valid nonce
    3. Create a new block with all pending transactions

    Returns:
        JSON response with details of the newly mined block

    Example response:
        {
            "message": "New Block Forged",
            "block_number": 5,
            "transactions": [
                {
                    "sender": "MINING",
                    "recipient": "node_identifier",
                    "amount": 1.0,
                    "signature": "",
                    "timestamp": 1634567890.123
                },
                ...
            ],
            "nonce": 12345,
            "previous_hash": "hash_of_previous_block",
            "timestamp": 1634567890.123
        }

    Error cases:
        - 500: Error during mining process
    """
    blockchain.submit_transaction(
        MINING_SENDER, node_identifier, MINING_REWARD, signature=""
    )

    try:
        nonce = blockchain.proof_of_work()

        last_block = blockchain.last_block
        previous_hash = blockchain.hash(last_block)

        block = blockchain.new_block(nonce, previous_hash)

        response: Dict[str, Any] = {
            "message": "New Block Forged",
            "block_number": block["index"],
            "transactions": block["transactions"],
            "nonce": block["nonce"],
            "previous_hash": block["previous_hash"],
            "timestamp": block["timestamp"],
        }
        logger.info("New block mined: #%s", block["index"])
        return jsonify(response), 200
    except (ValueError, KeyError) as e:
        logger.error("Mining error: %s", str(e))
        return jsonify({"error": f"Error mining new block: {str(e)}"}), 500


@app.route("/nodes/register", methods=["POST"])
@validate_json_request(required_fields=["nodes"])
def register_nodes() -> Response:
    """
    Register new nodes in the blockchain network.

    Required JSON fields:
        nodes: Array of strings - URLs of nodes to register (e.g., ["http://node1:5000", "http://node2:5000"])

    Returns:
        JSON response with registration results and status code 201 if at least one node was registered

    Error cases:
        - 400: Invalid nodes format or empty nodes list
        - 500: Internal error during node registration

    Example request:
        POST /nodes/register
        {
            "nodes": ["http://node1.example.com:5000", "http://node2.example.com:5000"]
        }

    Example response:
        {
            "message": "Nodes registration completed: 2 succeeded, 0 failed",
            "total_nodes": ["http://node1.example.com:5000", "http://node2.example.com:5000"],
            "successful_nodes": ["http://node1.example.com:5000", "http://node2.example.com:5000"]
        }
    """
    values = request.get_json()
    nodes = values.get("nodes")

    if not isinstance(nodes, list):
        return jsonify({"error": "Nodes must be provided as a list"}), 400

    if not nodes:
        return jsonify({"error": "Empty nodes list"}), 400

    successful_nodes = []
    failed_nodes = []

    for node in nodes:
        try:
            blockchain.register_node(node)
            successful_nodes.append(node)
        except ValueError as e:
            failed_nodes.append({"node": node, "error": str(e)})

    response: Dict[str, Any] = {
        "message": f"Nodes registration completed: {len(successful_nodes)} succeeded, {len(failed_nodes)} failed",
        "total_nodes": list(blockchain.nodes),
        "successful_nodes": successful_nodes,
    }

    if failed_nodes:
        response["failed_nodes"] = failed_nodes

    logger.info(
        "Registered %s new nodes, %s failed", len(successful_nodes), len(failed_nodes)
    )
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus() -> Response:
    """
    Resolve conflicts between blockchain nodes using consensus algorithm.

    This endpoint:
    1. Contacts all registered nodes to find the longest valid chain
    2. Replaces our chain if a longer valid chain is found

    Returns:
        JSON response indicating if our chain was replaced or maintained

    Example response (when chain is replaced):
        {
            "message": "Our chain was replaced",
            "new_chain_length": 25
        }

    Example response (when our chain is authoritative):
        {
            "message": "Our chain is authoritative",
            "chain_length": 20
        }

    Error cases:
        - 500: Error during consensus process
    """
    if not blockchain.nodes:
        return jsonify({"message": "No nodes registered. Nothing to resolve."}), 200

    try:
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response: Dict[str, str | int] = {
                "message": "Our chain was replaced",
                "new_chain_length": len(blockchain.chain),
            }
            logger.info("Chain replaced during consensus")
        else:
            response: Dict[str, str | int] = {
                "message": "Our chain is authoritative",
                "chain_length": len(blockchain.chain),
            }
            logger.info("Chain maintained during consensus")

        return jsonify(response), 200
    except (
        ValueError,
        KeyError,
    ) as e:
        logger.error("Consensus error: %s", str(e))
        return jsonify({"error": f"Error during consensus resolution: {str(e)}"}), 500


@app.route("/nodes/get", methods=["GET"])
def get_nodes() -> Response:
    """
    Get all registered nodes in the network.

    Returns:
        JSON response with list of all node URLs and count

    Example response:
        {
            "nodes": [
                "http://node1.example.com:5000",
                "http://node2.example.com:5000"
            ],
            "count": 2
        }
    """
    return (
        jsonify({"nodes": list(blockchain.nodes), "count": len(blockchain.nodes)}),
        200,
    )


@app.route("/block/<int:block_id>", methods=["GET"])
def get_block(block_id: int) -> Response:
    """
    Get a specific block by ID.

    Path parameters:
        block_id: Integer - Index of the block to retrieve

    Returns:
        JSON response with block data and its hash

    Error cases:
        - 404: Block not found (invalid block_id)

    Example request:
        GET /block/5

    Example response:
        {
            "block": {
                "index": 5,
                "timestamp": 1634567890.123,
                "transactions": [...],
                "nonce": 12345,
                "previous_hash": "hash_of_block_4"
            },
            "hash": "hash_of_block_5"
        }
    """
    if block_id < 0 or block_id >= len(blockchain.chain):
        return jsonify({"error": f"Block #{block_id} not found"}), 404

    return (
        jsonify(
            {
                "block": blockchain.chain[block_id],
                "hash": blockchain.hash(blockchain.chain[block_id]),
            }
        ),
        200,
    )


@app.route("/medical/record", methods=["POST"])
@validate_json_request(
    required_fields=["patient_id", "record_type", "medical_data", "signature"]
)
@authorize_healthcare_access
def add_medical_record() -> Response:
    """
    Add a new medical record to the blockchain.

    This endpoint requires authentication as a healthcare provider.

    Required JSON fields:
        patient_id: String - Unique identifier for the patient
        record_type: String - Type of medical record (must be one of the valid RECORD_TYPES)
        medical_data: Object - Medical record data in JSON format
        signature: String - Digital signature verifying record authenticity

    Optional JSON fields:
        access_list: Array of strings - IDs of users who can access this record
                    (defaults to [patient_id, provider_id])

    Returns:
        JSON response with record confirmation and status code 201 if successful

    Error cases:
        - 400: Invalid record type
        - 403: Unauthorized (not a healthcare provider)
        - 406: Signature verification failed
        - 500: Internal processing error

    Example request:
        POST /medical/record
        {
            "patient_id": "patient123",
            "record_type": "VISIT",
            "medical_data": {
                "diagnosis": "Common cold",
                "treatment": "Rest and fluids",
                "notes": "Patient should recover in 3-5 days"
            },
            "signature": "digital_signature_data",
            "access_list": ["patient123", "doctor456", "specialist789"]
        }

    Example response:
        {
            "message": "Medical record will be added to Block 5",
            "record_type": "VISIT",
            "patient_id": "patient123",
            "provider_id": "doctor456",
            "timestamp": 1634567890.123
        }
    """
    values = request.get_json()

    patient_id = values.get("patient_id")
    record_type = values.get("record_type")
    medical_data = values.get("medical_data")
    signature = values.get("signature")
    access_list = values.get("access_list", [patient_id, request.user_id])

    if record_type not in RECORD_TYPES.values():
        valid_types = ", ".join(RECORD_TYPES.values())
        return (
            jsonify({"error": f"Invalid record type. Must be one of: {valid_types}"}),
            400,
        )

    if request.user_role != "healthcare_provider":
        return (
            jsonify({"error": "Only healthcare providers can add medical records"}),
            403,
        )

    try:
        block_index: int | bool = blockchain.new_medical_record(
            patient_id,
            request.user_id,
            record_type,
            medical_data,
            access_list,
            signature,
        )

        if block_index:
            response: Dict[str, Any] = {
                "message": f"Medical record will be added to Block {block_index}",
                "record_type": record_type,
                "patient_id": patient_id,
                "provider_id": request.user_id,
                "timestamp": values.get("timestamp", time.time()),
            }
            logger.info(
                "New medical record: %s for patient %s", record_type, patient_id
            )
            return jsonify(response), 201

        return (
            jsonify(
                {"error": "Invalid medical record - signature verification failed"}
            ),
            406,
        )

    except (
        KeyError,
        ValueError,
    ) as e:
        logger.error("Error adding medical record: %s", str(e))
        return jsonify({"error": f"Error processing medical record: {str(e)}"}), 500


@app.route("/medical/records/:str<patient_id>", methods=["GET"])
@authorize_healthcare_access
def get_medical_records(
    patient_id: str,
) -> Response:
    """
    Get medical records for a specific patient.

    This endpoint requires authentication, and the user must either:
    1. Be the patient requesting their own records, or
    2. Be a healthcare provider with access to the patient's records

    Path parameters:
        patient_id: String - Unique identifier for the patient

    Query parameters:
        record_type: String (optional) - Filter records by type

    Returns:
        JSON response with patient records and count

    Error cases:
        - 403: Unauthorized access to patient records
        - 500: Error retrieving records

    Example request:
        GET /medical/records/patient123?record_type=VISIT

    Example response:
        {
            "patient_id": "patient123",
            "records": [
                {
                    "index": 5,
                    "record_type": "VISIT",
                    "medical_data": {
                        "diagnosis": "Common cold",
                        "treatment": "Rest and fluids"
                    },
                    "provider_id": "doctor456",
                    "timestamp": 1634567890.123
                },
                ...
            ],
            "count": 3
        }
    """
    record_type = request.args.get("record_type")

    is_self_access = request.user_id == patient_id
    is_provider = request.user_role == "healthcare_provider"

    if not (is_self_access or is_provider):
        return jsonify({"error": "Unauthorized access to patient records"}), 403

    try:
        records: List[Dict[str, Any]] = blockchain.get_patient_records(
            patient_id, request.user_id, record_type
        )

        return (
            jsonify(
                {"patient_id": patient_id, "records": records, "count": len(records)}
            ),
            200,
        )

    except (ValueError, KeyError) as e:
        logger.error("Error retrieving medical records: %s", str(e))
        return jsonify({"error": f"Error retrieving medical records: {str(e)}"}), 500


@app.route("/medical/consent", methods=["POST"])
@validate_json_request(
    required_fields=["patient_id", "provider_id", "access_type", "signature"]
)
@authorize_healthcare_access
def manage_consent() -> Response:
    """
    Manage patient consent for medical record access.

    This endpoint allows patients to grant or revoke access to their medical records.
    Only the patient can manage their own consent.

    Required JSON fields:
        patient_id: String - Patient's unique identifier
        provider_id: String - Healthcare provider's unique identifier
        access_type: String - Either "grant" or "revoke"
        signature: String - Digital signature verifying consent authenticity

    Optional JSON fields:
        record_types: Array of strings - Specific record types to grant/revoke access to
                     (defaults to all record types)
        expiration: Number - Unix timestamp when the consent expires (optional)

    Returns:
        JSON response with consent confirmation and status code 201 if successful

    Error cases:
        - 400: Invalid access_type
        - 403: Unauthorized (not the patient)
        - 406: Signature verification failed
        - 500: Internal processing error

    Example request:
        POST /medical/consent
        {
            "patient_id": "patient123",
            "provider_id": "doctor456",
            "access_type": "grant",
            "record_types": ["VISIT", "MEDICATION"],
            "signature": "digital_signature_data",
            "expiration": 1640995200
        }

    Example response:
        {
            "message": "Consent record will be added to Block 5",
            "patient_id": "patient123",
            "provider_id": "doctor456",
            "access_type": "grant",
            "record_types": ["VISIT", "MEDICATION"]
        }
    """
    values = request.get_json()

    patient_id = values.get("patient_id")
    provider_id = values.get("provider_id")
    access_type = values.get("access_type")
    signature = values.get("signature")
    record_types = values.get("record_types", list(RECORD_TYPES.values()))

    if request.user_id != patient_id:
        return (
            jsonify(
                {"error": "Only patients can manage consent for their own records"}
            ),
            403,
        )

    if access_type not in ["grant", "revoke"]:
        return jsonify({"error": "access_type must be either 'grant' or 'revoke'"}), 400

    try:
        consent_data: Dict[str, Any] = {
            "action": access_type,
            "provider_id": provider_id,
            "record_types": record_types,
            "timestamp": time.time(),
            "expiration": values.get("expiration"),
        }

        block_index: int | bool = blockchain.new_medical_record(
            patient_id,
            patient_id,
            RECORD_TYPES["CONSENT"],
            consent_data,
            [patient_id, provider_id],
            signature,
        )

        if block_index:
            response: Dict[str, Any] = {
                "message": f"Consent record will be added to Block {block_index}",
                "patient_id": patient_id,
                "provider_id": provider_id,
                "access_type": access_type,
                "record_types": record_types,
            }
            logger.info(
                "New consent record: %s access for provider %s",
                access_type,
                provider_id,
            )
            return jsonify(response), 201

        return (
            jsonify(
                {"error": "Invalid consent record - signature verification failed"}
            ),
            406,
        )

    except (
        ValueError,
        KeyError,
    ) as e:
        logger.error("Error managing consent: %s", str(e))
        return jsonify({"error": f"Error processing consent: {str(e)}"}), 500


@app.route("/auth/register", methods=["POST"])
@validate_json_request(required_fields=["name", "role", "email"])
def register_user() -> Response:
    """
    Register a new user in the system.

    This endpoint creates a new user with a specified role.

    Required JSON fields:
        name: String - User's full name
        role: String - User's role (must be either "patient" or "healthcare_provider")

    Optional JSON fields:
        email: String - User's email address

    Returns:
        JSON response with user credentials and status code 201 if successful

    Error cases:
        - 400: Invalid role
        - 500: Error during user registration

    Example request:
        POST /auth/register
        {
            "name": "John Doe",
            "role": "patient",
            "email": "john.doe@example.com"
        }

    Example response:
        {
            "message": "User registered successfully",
            "user_id": "user_uuid",
            "blockchain_id": "blockchain_uuid",
            "role": "patient",
            "api_key": "api_key_uuid"
        }

    Security notes:
        - In production, api_key should be stored securely and not returned in plaintext
        - Consider implementing a proper token issuance system for production use
    """
    values = request.get_json()
    name = values.get("name")
    requested_role = values.get("role")
    email = values.get("email", "")

    try:
        valid_roles = ["patient", "healthcare_provider"]
        if requested_role not in valid_roles:
            return (
                jsonify(
                    {
                        "error": f"Invalid role - must be one of: {', '.join(valid_roles)}"
                    }
                ),
                400,
            )

        user_id = str(uuid4())
        blockchain_id = str(uuid4()).replace("-", "")

        USER_STORE[user_id] = {
            "role": requested_role,
            "blockchain_id": blockchain_id,
            "name": name,
            "email": email,
            "created_at": time.time(),
        }

        api_key = str(uuid4()).replace("-", "")

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user_id": user_id,
                    "blockchain_id": blockchain_id,
                    "role": requested_role,
                    "api_key": api_key,
                }
            ),
            201,
        )

    except (
        ValueError,
        KeyError,
    ) as e:
        logger.error("User registration error: %s", str(e))
        return jsonify({"error": f"Error during user registration: {str(e)}"}), 500


@app.route("/auth/validate", methods=["GET"])
def validate_auth() -> Response:
    """
    Validate authentication credentials.

    This endpoint verifies the provided authentication credentials and returns
    user information if valid. It can be used to check if a user's authentication
    token is valid without performing any other operations.

    Authentication:
        Requires a valid Authorization header (typically "Bearer <token>" or "ApiKey <key>")

    Returns:
        JSON response with validation results

    Response fields:
        valid: Boolean - True if credentials are valid, False otherwise
        user_id: String - Unique identifier for the authenticated user (if valid)
        role: String - User's role in the system (if valid)
        user_info: Object - Additional user information (if valid)
            name: String - User's full name
            email: String - User's email address

    Status codes:
        200: Authentication is valid
        401: Authentication is invalid

    Error cases:
        - 401: Invalid, expired, or missing authentication credentials

    Security notes:
        - This endpoint should be rate-limited in production to prevent brute force attacks
        - Consider implementing token expiration checks

    Example request:
        GET /auth/validate
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example success response:
        {
            "valid": true,
            "user_id": "user123",
            "role": "healthcare_provider",
            "user_info": {
                "name": "Dr. Jane Smith",
                "email": "jane.smith@hospital.org"
            }
        }

    Example error response:
        {
            "valid": false,
            "error": "Invalid authentication token"
        }
    """
    auth_header = request.headers.get("Authorization")

    try:
        (user_id, role, user_info) = validate_auth_header(auth_header)

        return (
            jsonify(
                {
                    "valid": True,
                    "user_id": user_id,
                    "role": role,
                    "user_info": {
                        "name": (
                            user_info.get("name")
                            if isinstance(user_info, dict)
                            else None
                        ),
                        "email": (
                            user_info.get("email")
                            if isinstance(user_info, dict)
                            else None
                        ),
                    },
                }
            ),
            200,
        )

    except AuthError as e:
        return jsonify({"valid": False, "error": str(e)}), 401


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--port", default=5000, type=int, help="port to listen on"
    )
    parser.add_argument("-h", "--host", default="0.0.0.0", help="host to listen on")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    args = parser.parse_args()

    port = args.port
    host = args.host
    debug = args.debug

    logger.info("Starting blockchain node on %s:%s", host, port)
    app.run(host=host, port=port, debug=debug)
