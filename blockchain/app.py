import time
from flask import Flask, Response, jsonify, request
from uuid import uuid4
from functools import wraps
import logging
from typing import Any, Dict, List, Optional, Callable
import os

from blockchain.blockchain import Blockchain, MINING_SENDER, MINING_REWARD, RECORD_TYPES
from blockchain.auth_service import validate_auth_header, AuthError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
blockchain = Blockchain()
node_identifier = str(uuid4()).replace("-", "")

DEV_API_KEY = os.environ.get("DEV_API_KEY", "dev-api-key-for-testing")
DEV_MODE = os.environ.get("FLASK_ENV") == "development"

USER_STORE = {}


def validate_json_request(required_fields: Optional[List[str]] = None) -> Callable:
    """Decorator to validate JSON requests and required fields."""

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
    """Decorator to validate healthcare access authorization."""

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
    logger.error("Resource not found: %s", str(error))
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error) -> Response:
    logger.error("Internal server error: %s", str(error))
    return jsonify({"error": "Internal server error"}), 500


@app.route("/", methods=["GET"])
def home() -> Response:
    """API homepage with endpoint information."""
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
    """Create a new transaction in the blockchain."""
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
    """Get all pending transactions."""
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
    """Get the full blockchain with pagination support."""
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
    """Mine a new block and add it to the blockchain."""
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
    """Register new nodes in the blockchain network."""
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
    """Resolve conflicts between blockchain nodes using consensus algorithm."""
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
    """Get all registered nodes in the network."""
    return (
        jsonify({"nodes": list(blockchain.nodes), "count": len(blockchain.nodes)}),
        200,
    )


@app.route("/block/<int:block_id>", methods=["GET"])
def get_block(block_id: int) -> Response:
    """Get a specific block by ID."""
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
    """Add a new medical record to the blockchain."""
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
            response: Dict[str,] = {
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
    """Get medical records for a specific patient."""
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
    """Manage patient consent for medical record access."""
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
@validate_json_request(required_fields=["name", "role"])
def register_user() -> Response:
    """Register a new user in the system."""
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
    """Validate authentication credentials."""
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
                        "name": user_info.get("name"),
                        "email": user_info.get("email"),
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
