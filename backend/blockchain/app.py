from flask import Flask, jsonify, request, abort
from uuid import uuid4
import json
from functools import wraps
import logging
from typing import Dict, List, Union, Optional, Callable

from blockchain.blockchain import Blockchain, MINING_SENDER, MINING_REWARD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
blockchain = Blockchain()
node_identifier = str(uuid4()).replace("-", "")

# Request validation decorator
def validate_json_request(required_fields: Optional[List[str]] = None) -> Callable:
    """
    Decorator to validate JSON requests and ensure they contain required fields.

    This decorator performs the following validations:
    1. Checks if the request contains JSON data
    2. Verifies the JSON format is valid
    3. Ensures all required fields are present in the JSON payload

    Args:
        required_fields (List[str], optional): List of field names that must be present
            in the request JSON. If None, only format validation is performed.

    Returns:
        Callable: The decorated function if validation passes, otherwise returns
            an appropriate error response with a 400 status code.

    Example:
        @app.route('/endpoint', methods=['POST'])
        @validate_json_request(required_fields=['name', 'email'])
        def my_endpoint():
            # Will only execute if the request contains valid JSON with 'name' and 'email' fields
            data = request.get_json()
            return jsonify({"success": True})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            # Get JSON data
            try:
                request_data = request.get_json()
            except Exception as e:
                logger.error(f"Invalid JSON: {str(e)}")
                return jsonify({"error": "Invalid JSON format"}), 400

            # Check for required fields if specified
            if required_fields:
                missing_fields = [field for field in required_fields if field not in request_data]
                if missing_fields:
                    missing_str = ', '.join(missing_fields)
                    return jsonify({"error": f"Missing required fields: {missing_str}"}), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.

    Returns:
        tuple: A JSON response with error message and 404 status code
    """
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.

    Logs the error details and returns a generic error message to the client.

    Args:
        error: The exception that triggered the error handler

    Returns:
        tuple: A JSON response with error message and 500 status code
    """
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.route("/", methods=["GET"])
def home():
    """
    API home endpoint providing basic information about the blockchain service.

    Returns information about the API status, version, and available endpoints
    to help users understand how to interact with the blockchain service.

    Returns:
        tuple: JSON response with API information and 200 status code

    Example Response:
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
    return jsonify({
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
            "GET /nodes/get": "Get registered nodes"
        }
    }), 200

@app.route("/transactions/new", methods=["POST"])
@validate_json_request(required_fields=["sender", "recipient", "amount", "signature"])
def new_transaction():
    """
    Create a new transaction to be added to the blockchain.

    This endpoint validates transaction details and, if valid, adds the transaction
    to the pending transactions pool to be included in the next mined block.

    Required JSON payload fields:
        - sender (str): Address of the transaction sender
        - recipient (str): Address of the transaction recipient
        - amount (float): Amount to transfer (must be positive)
        - signature (str): Digital signature to verify transaction authenticity
          (Not required for mining reward transactions)

    Returns:
        tuple: JSON response with transaction details and status code
            - 201 Created: Transaction accepted
            - 400 Bad Request: Invalid transaction parameters
            - 406 Not Acceptable: Signature verification failed
            - 500 Server Error: Error processing transaction

    Example Request:
        POST /transactions/new
        Content-Type: application/json

        {
            "sender": "sender_address_hash",
            "recipient": "recipient_address_hash",
            "amount": 5.0,
            "signature": "digital_signature_data"
        }

    Example Success Response:
        {
            "message": "Transaction will be added to Block 5",
            "transaction": {
                "sender": "sender_address_hash",
                "recipient": "recipient_address_hash",
                "amount": 5.0
            }
        }
    """
    values = request.get_json()

    # Validate amount
    try:
        amount = float(values["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a valid number"}), 400

    # Validate sender and recipient addresses
    sender = values["sender"]
    recipient = values["recipient"]

    if len(sender) < 10 or len(recipient) < 10:
        return jsonify({"error": "Invalid sender or recipient address"}), 400

    # Validate signature (basic validation, more should be in blockchain.py)
    signature = values["signature"]
    if not signature and sender != MINING_SENDER:
        return jsonify({"error": "Transaction requires a valid signature"}), 400

    # Submit transaction
    try:
        transaction_result = blockchain.submit_transaction(
            sender, recipient, amount, signature
        )
    except Exception as e:
        logger.error(f"Transaction submission error: {str(e)}")
        return jsonify({"error": f"Transaction processing error: {str(e)}"}), 500

    if transaction_result:
        response = {
            "message": f"Transaction will be added to Block {transaction_result}",
            "transaction": {
                "sender": sender,
                "recipient": recipient,
                "amount": amount
            }
        }
        logger.info(f"New transaction: {sender} -> {recipient}, {amount}")
        return jsonify(response), 201
    else:
        return jsonify({"error": "Invalid transaction - signature verification failed"}), 406

@app.route("/transactions/pending", methods=["GET"])
def get_pending_transactions():
    """
    Retrieve all pending transactions waiting to be mined into a block.

    Provides visibility into the current transaction pool that will be included
    in the next block when mining occurs.

    Returns:
        tuple: JSON response with pending transactions and 200 status code

    Example Response:
        {
            "pending_transactions": [
                {
                    "sender": "sender_address_hash",
                    "recipient": "recipient_address_hash",
                    "amount": 5.0,
                    "signature": "digital_signature_data",
                    "timestamp": 1623825026.744143
                }
            ],
            "count": 1
        }
    """
    return jsonify({
        "pending_transactions": blockchain.transactions,
        "count": len(blockchain.transactions)
    }), 200

@app.route("/chain", methods=["GET"])
def full_chain():
    """
    Retrieve the full blockchain or a paginated subset of blocks.

    Returns the blockchain data with optional pagination support to handle
    potentially large chains efficiently.

    Query Parameters:
        - start (int, optional): Starting block index (default: 0)
        - limit (int, optional): Maximum number of blocks to return (default: entire chain)

    Returns:
        tuple: JSON response with blockchain data and 200 status code

    Example Request:
        GET /chain?start=10&limit=5

    Example Response:
        {
            "chain": [
                {
                    "index": 10,
                    "timestamp": 1623825026.744143,
                    "transactions": [...],
                    "nonce": 42,
                    "previous_hash": "hash_of_block_9"
                },
                ... (up to 5 blocks total)
            ],
            "length": 100,
            "start": 10,
            "limit": 5,
            "returned_blocks": 5
        }
    """
    # Optional query parameter for pagination
    start = request.args.get('start', default=0, type=int)
    limit = request.args.get('limit', default=len(blockchain.chain), type=int)

    # Validate pagination parameters
    if start < 0:
        start = 0
    if limit < 1:
        limit = 1
    if start >= len(blockchain.chain):
        start = max(0, len(blockchain.chain) - 1)

    chain_slice = blockchain.chain[start:start + limit]

    response = {
        "chain": chain_slice,
        "length": len(blockchain.chain),
        "start": start,
        "limit": limit,
        "returned_blocks": len(chain_slice)
    }
    return jsonify(response), 200

@app.route("/mine", methods=["GET"])
def mine():
    """
    Mine a new block and add it to the blockchain.

    This endpoint performs the proof of work algorithm to find a valid nonce,
    creates a new block with all pending transactions, and adds it to the chain.
    A mining reward transaction is automatically included in the block.

    Returns:
        tuple: JSON response with block details and 200 status code
              or error message with appropriate status code

    Example Response:
        {
            "message": "New Block Forged",
            "block_number": 5,
            "transactions": [
                {
                    "sender": "MINING",
                    "recipient": "node_identifier_hash",
                    "amount": 1.0,
                    "signature": "",
                    "timestamp": 1623825026.744143
                },
                ... (other transactions)
            ],
            "nonce": 12345,
            "previous_hash": "hash_of_previous_block",
            "timestamp": 1623825026.744143
        }

    Note:
        Mining is computationally intensive and may take time depending on the 
        difficulty level set in the blockchain implementation.
    """
    # Ensure there's at least one transaction (the mining reward) to include
    blockchain.submit_transaction(
        MINING_SENDER, node_identifier, MINING_REWARD, signature=""
    )

    try:
        # Find the proof of work
        nonce = blockchain.proof_of_work()

        # Get the hash of the last block
        last_block = blockchain.last_block
        previous_hash = blockchain.hash(last_block)

        # Create the new block
        block = blockchain.new_block(nonce, previous_hash)

        response = {
            "message": "New Block Forged",
            "block_number": block["index"],
            "transactions": block["transactions"],
            "nonce": block["nonce"],
            "previous_hash": block["previous_hash"],
            "timestamp": block["timestamp"]
        }
        logger.info(f"New block mined: #{block['index']}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Mining error: {str(e)}")
        return jsonify({"error": f"Error mining new block: {str(e)}"}), 500

@app.route("/nodes/register", methods=["POST"])
@validate_json_request(required_fields=["nodes"])
def register_nodes():
    """
    Register new nodes in the blockchain network.

    This endpoint allows this node to become aware of other nodes in the network,
    enabling distributed consensus and blockchain synchronization.

    Required JSON payload:
        - nodes (List[str]): List of node URLs to register (e.g., ["http://192.168.0.5:5000"])

    Returns:
        tuple: JSON response with registration results and 201 status code
               or error message with 400 status code

    Example Request:
        POST /nodes/register
        Content-Type: application/json

        {
            "nodes": [
                "http://192.168.0.5:5000",
                "http://192.168.0.6:5000"
            ]
        }

    Example Success Response:
        {
            "message": "Nodes registration completed: 2 succeeded, 0 failed",
            "total_nodes": [
                "192.168.0.5:5000",
                "192.168.0.6:5000"
            ],
            "successful_nodes": [
                "http://192.168.0.5:5000",
                "http://192.168.0.6:5000"
            ]
        }

    Example Partial Success Response:
        {
            "message": "Nodes registration completed: 1 succeeded, 1 failed",
            "total_nodes": ["192.168.0.5:5000"],
            "successful_nodes": ["http://192.168.0.5:5000"],
            "failed_nodes": [
                {
                    "node": "http://invalid-url",
                    "error": "Invalid URL format"
                }
            ]
        }
    """
    values = request.get_json()
    nodes = values.get("nodes")

    if not isinstance(nodes, list):
        return jsonify({"error": "Nodes must be provided as a list"}), 400

    if len(nodes) == 0:
        return jsonify({"error": "Empty nodes list"}), 400

    # Register each node
    successful_nodes = []
    failed_nodes = []

    for node in nodes:
        try:
            blockchain.register_node(node)
            successful_nodes.append(node)
        except ValueError as e:
            failed_nodes.append({"node": node, "error": str(e)})

    response = {
        "message": f"Nodes registration completed: {len(successful_nodes)} succeeded, {len(failed_nodes)} failed",
        "total_nodes": list(blockchain.nodes),
        "successful_nodes": successful_nodes
    }

    if failed_nodes:
        response["failed_nodes"] = failed_nodes

    logger.info(f"Registered {len(successful_nodes)} new nodes, {len(failed_nodes)} failed")
    return jsonify(response), 201

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    """
    Resolve conflicts between nodes using the consensus algorithm.

    This endpoint contacts all registered nodes, compares their chains with this node's chain,
    and replaces this node's chain if a longer valid chain is found on another node.

    The consensus algorithm follows the rule that the longest valid chain in the network
    is considered authoritative. This ensures all nodes in the network eventually 
    converge to the same blockchain state.

    Returns:
        tuple: JSON response with consensus results and 200 status code
               or error message with 500 status code

    Example Response (Chain Replaced):
        {
            "message": "Our chain was replaced",
            "new_chain_length": 15
        }

    Example Response (Chain Maintained):
        {
            "message": "Our chain is authoritative",
            "chain_length": 20
        }

    Note:
        This endpoint requires network communication with other nodes and may take
        time depending on network conditions and the number of registered nodes.
    """
    if not blockchain.nodes:
        return jsonify({"message": "No nodes registered. Nothing to resolve."}), 200

    try:
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                "message": "Our chain was replaced",
                "new_chain_length": len(blockchain.chain)
            }
            logger.info("Chain replaced during consensus")
        else:
            response = {
                "message": "Our chain is authoritative",
                "chain_length": len(blockchain.chain)
            }
            logger.info("Chain maintained during consensus")

        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Consensus error: {str(e)}")
        return jsonify({"error": f"Error during consensus resolution: {str(e)}"}), 500

@app.route("/nodes/get", methods=["GET"])
def get_nodes():
    """
    Retrieve all nodes currently registered in the blockchain network.

    Returns:
        tuple: JSON response with registered nodes and 200 status code

    Example Response:
        {
            "nodes": [
                "192.168.0.5:5000",
                "192.168.0.6:5000"
            ],
            "count": 2
        }
    """
    response = {
        "nodes": list(blockchain.nodes),
        "count": len(blockchain.nodes)
    }
    return jsonify(response), 200

@app.route("/block/<int:block_id>", methods=["GET"])
def get_block(block_id):
    """
    Retrieve a specific block from the blockchain by its index.

    Args:
        block_id (int): The index of the block to retrieve

    Returns:
        tuple: JSON response with block data and hash, and 200 status code
               or error message with 404 status code if block not found

    Example Request:
        GET /block/5

    Example Response:
        {
            "block": {
                "index": 5,
                "timestamp": 1623825026.744143,
                "transactions": [
                    {
                        "sender": "sender_address_hash",
                        "recipient": "recipient_address_hash",
                        "amount": 5.0,
                        "signature": "digital_signature_data",
                        "timestamp": 1623825026.744143
                    }
                ],
                "nonce": 12345,
                "previous_hash": "hash_of_block_4"
            },
            "hash": "hash_of_block_5"
        }
    """
    if block_id < 0 or block_id >= len(blockchain.chain):
        return jsonify({"error": f"Block #{block_id} not found"}), 404

    return jsonify({
        "block": blockchain.chain[block_id],
        "hash": blockchain.hash(blockchain.chain[block_id])
    }), 200

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-h', '--host', default='0.0.0.0', help='host to listen on')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    args = parser.parse_args()

    port = args.port
    host = args.host
    debug = args.debug

    logger.info(f"Starting blockchain node on {host}:{port}")
    app.run(host=host, port=port, debug=debug)