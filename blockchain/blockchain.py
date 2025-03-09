import binascii
import hashlib
import json
from collections import OrderedDict
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import os
from cryptography.fernet import Fernet
import base64
import logging
import requests
from typing import Any, Dict, List, Optional, Set, Union
# Use pycryptodome package instead of Crypto for better compatibility
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Configure logging once at module level
logger = logging.getLogger("blockchain")
logger.setLevel(logging.INFO)

# Only add handler if not already added (prevents duplicate log entries)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Global constants for blockchain operation
MINING_SENDER = "THE BLOCKCHAIN"  # Special identifier for mining rewards
MINING_REWARD = 1  # Amount of cryptocurrency awarded for mining a block
MINING_DIFFICULTY = 2  # Difficulty of the proof of work (number of leading zeros required)

RECORD_TYPES = {
    "DIAGNOSTIC": "diagnostic_report",
    "PRESCRIPTION": "prescription",
    "LAB_RESULT": "lab_result",
    "VITAL_SIGNS": "vital_signs",
    "CONSULTATION": "consultation_notes",
    "SURGERY": "surgery_record",
    "IMAGING": "imaging_report",
    "VACCINATION": "vaccination",
    "ALLERGY": "allergy_record",
    "CONSENT": "patient_consent",
}

class Blockchain:
    def __init__(self) -> None:
        """Initialize a new blockchain."""
        self.chain: List[Dict[str, Any]] = []  # The blockchain - a list of blocks
        self.transactions: List[Dict[str, Any]] = []  # Pending transactions for the next block
        self.nodes: Set[str] = set()  # Set of nodes in the network for consensus
        self.node_id: str = str(uuid4()).replace("-", "")  # Unique identifier for this node

        # Create the genesis block (first block in the chain)
        self.new_block(0, "00")

        # Generate or load encryption key
        self.encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self) -> bytes:
        """Generate or load a key for encrypting sensitive medical data."""
        key_file = "medical_encryption.key"
        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    return f.read()
            else:
                # Generate a new key
                key = Fernet.generate_key()
                # Ensure directory exists
                os.makedirs(os.path.dirname(key_file) or '.', exist_ok=True)
                # Use secure file permissions for the key
                with open(key_file, "wb") as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Read/write for owner only
                return key
        except (IOError, OSError) as e:
            logger.error(f"Error accessing encryption key file: {e}")
            # Generate a temporary key in memory
            logger.warning("Using temporary in-memory encryption key")
            return Fernet.generate_key()

    def encrypt_medical_data(self, data: Any) -> Optional[str]:
        """Encrypt sensitive medical data.

        Args:
            data: The data to encrypt

        Returns:
            Base64-encoded encrypted data or None if input is empty
        """
        if not data:
            return None

        try:
            f = Fernet(self.encryption_key)
            json_data = json.dumps(data)
            encrypted_data = f.encrypt(json_data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt_medical_data(self, encrypted_data: Optional[str], authorized: bool = False) -> Optional[Any]:
        """Decrypt medical data if authorized.

        Args:
            encrypted_data: The encrypted data to decrypt
            authorized: Whether the requester is authorized to access this data

        Returns:
            Decrypted data or None if unauthorized or decryption failed
        """
        if not encrypted_data or not authorized:
            return None

        try:
            f = Fernet(self.encryption_key)
            decoded = base64.b64decode(encrypted_data)
            decrypted_data = f.decrypt(decoded).decode()
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None

    def new_block(self, nonce: int, previous_hash: Optional[str] = None) -> Dict[str, Any]:
        """Create a new block in the blockchain.

        Args:
            nonce: The proof of work value
            previous_hash: Hash of previous block (optional for genesis block)

        Returns:
            The newly created block
        """
        # Handle genesis block case
        prev_hash = previous_hash if previous_hash is not None else self.hash(self.chain[-1])

        block = {
            "index": len(self.chain) + 1,  # Block number in sequence
            "timestamp": time(),  # Current timestamp
            "transactions": self.transactions.copy(),  # Copy of list of transactions
            "nonce": nonce,  # Proof of work value
            "previous_hash": prev_hash,  # Link to previous block
        }

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """Add a new transaction to the list of pending transactions.

        Args:
            sender: Sender's address
            recipient: Recipient's address
            amount: Transaction amount

        Returns:
            The index of the block that will hold this transaction
        """
        self.transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )

        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """Create a SHA-256 hash of a block.

        Args:
            block: Block to hash

        Returns:
            Hash string
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        """Get the last block in the chain.

        Returns:
            The most recent block
        """
        return self.chain[-1]

    def proof_of_work(self) -> int:
        """Proof of Work algorithm.

        Find a number (nonce) that produces a hash with leading zeros.

        Returns:
            The nonce that satisfies the proof of work
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while not self.valid_proof(self.transactions, last_hash, nonce):
            nonce += 1

        return nonce

    @staticmethod
    def valid_proof(transactions: List[Dict[str, Any]], last_hash: str, nonce: int, 
                    difficulty: int = MINING_DIFFICULTY) -> bool:
        """Validate the proof of work.

        Args:
            transactions: List of transactions
            last_hash: Hash of the previous block
            nonce: The proof of work value
            difficulty: The number of leading zeros required

        Returns:
            True if valid, False otherwise
        """
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def register_node(self, address: str) -> None:
        """Add a new node to the list of nodes.

        Args:
            address: Address of the node. e.g. 'http://192.168.0.5:5000'

        Raises:
            ValueError: If the URL is invalid
        """
        try:
            parsed_url = urlparse(address)
            if parsed_url.netloc:
                self.nodes.add(parsed_url.netloc)
            elif parsed_url.path:
                # Accepts an URL without scheme like '192.168.0.5:5000'.
                self.nodes.add(parsed_url.path)
            else:
                raise ValueError("Invalid URL")
        except ValueError as e:
            raise ValueError(f"Invalid URL: {str(e)}") from e

    def verify_transaction_signature(self, sender_address: str, signature: str, 
                                    transaction: Dict[str, Any]) -> bool:
        """Verify the signature of a transaction.

        Args:
            sender_address: Sender's address (hex encoded public key)
            signature: Signature to verify
            transaction: Transaction data

        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Import the public key
            public_key = RSA.importKey(binascii.unhexlify(sender_address))
            verifier = pkcs1_15.new(public_key)

            # Create a SHA hash of the transaction
            h = SHA.new(str(transaction).encode("utf8"))

            # Verify the signature using the public key
            verifier.verify(h, binascii.unhexlify(signature))
            return True
        except (ValueError, TypeError, binascii.Error) as e:
            logger.error(f"Signature verification error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during signature verification: {e}")
            return False

    def submit_transaction(self, sender_address: str, recipient_address: str, 
                          value: int, signature: str) -> Union[int, bool]:
        """Add a transaction to pending transactions.

        Args:
            sender_address: Sender's address
            recipient_address: Recipient's address
            value: Transaction amount
            signature: Transaction signature

        Returns:
            Block index or False if signature verification fails
        """
        transaction = OrderedDict(
            {
                "sender_address": sender_address,
                "recipient_address": recipient_address,
                "value": value,
            }
        )

        # Mining reward transaction requires no signature verification
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1

        # Normal transaction requires signature verification
        if self.verify_transaction_signature(sender_address, signature, transaction):
            self.transactions.append(transaction)
            return len(self.chain) + 1

        return False

    def new_medical_record(
        self,
        patient_id: str,
        doctor_id: str,
        record_type: str,
        medical_data: Any,
        access_list: Optional[List[str]] = None,
        signature: Optional[str] = None,
    ) -> Union[int, bool]:
        """Creates a new medical record transaction to go into the next mined Block.

        Args:
            patient_id: Patient identifier (hash of patient's public key)
            doctor_id: Doctor identifier (hash of doctor's public key)
            record_type: Type of medical record (from RECORD_TYPES)
            medical_data: The medical data to be stored (will be encrypted)
            access_list: List of entities allowed to access this record
            signature: Doctor's signature to validate the record

        Returns:
            The index of the Block that will hold this record or False if validation fails
        """
        if record_type not in RECORD_TYPES.values():
            raise ValueError(
                f"Invalid record type. Must be one of: {', '.join(RECORD_TYPES.values())}"
            )

        # Encrypt the medical data
        encrypted_data = self.encrypt_medical_data(medical_data)
        if encrypted_data is None and medical_data is not None:
            logger.error("Failed to encrypt medical data")
            return False

        # Create the medical record transaction
        record = OrderedDict(
            {
                "type": "MEDICAL_RECORD",
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "record_type": record_type,
                "data": encrypted_data,
                "timestamp": time(),
                "access_list": access_list or [patient_id, doctor_id],
            }
        )

        # Verify doctor's signature
        if doctor_id != MINING_SENDER:  # Skip verification for system-generated records
            if not self.verify_record_signature(doctor_id, signature, record):
                logger.warning(f"Record signature verification failed for doctor_id: {doctor_id}")
                return False

        self.transactions.append(record)
        return self.last_block["index"] + 1

    def verify_record_signature(self, provider_id: str, signature: Optional[str], 
                              record: Dict[str, Any]) -> bool:
        """Verify that a medical record was signed by the healthcare provider.

        Args:
            provider_id: Provider's ID
            signature: Signature to verify
            record: Record data

        Returns:
            True if the signature is valid, False otherwise
        """
        # Special case for debug mode signature
        if signature == "DEBUG_SKIP_VERIFICATION":
            logger.warning("Skipping signature verification in DEBUG mode")
            return True

        # For doctors/providers adding records, we need signature verification
        if not signature:
            logger.error("Missing signature for record verification")
            return False

        try:
            # Create a copy of the record without the data field for signature verification
            record_for_verification = record.copy()
            # Don't include the encrypted data in signature verification
            if "data" in record_for_verification:
                record_for_verification["data"] = "SIGNATURE_PLACEHOLDER"

            # Verify signature similar to transaction verification
            public_key = RSA.importKey(binascii.unhexlify(provider_id))
            verifier = pkcs1_15.new(public_key)

            # Create a hash of the record
            record_hash = SHA.new(
                json.dumps(record_for_verification, sort_keys=True).encode("utf8")
            )

            verifier.verify(record_hash, binascii.unhexlify(signature))
            return True
        except (ValueError, TypeError, binascii.Error) as e:
            logger.error(f"Record signature verification error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying record signature: {str(e)}")
            return False

    def get_patient_records(self, patient_id: str, requester_id: str, 
                           record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all medical records for a specific patient.

        Args:
            patient_id: ID of the patient
            requester_id: ID of the person requesting access (for authorization)
            record_type: Optional filter for specific record types

        Returns:
            List of medical records the requester is authorized to access
        """
        records = []

        # Search through all blocks in the chain
        for block in self.chain:
            for transaction in block["transactions"]:
                # Check if it's a medical record and belongs to the patient
                if (
                    transaction.get("type") == "MEDICAL_RECORD"
                    and transaction.get("patient_id") == patient_id
                ):
                    # Check if record type matches filter (if provided)
                    if record_type and transaction.get("record_type") != record_type:
                        continue

                    # Check if requester is authorized to access this record
                    access_list = transaction.get("access_list", [])
                    if requester_id in access_list:
                        # Create a copy to avoid modifying the blockchain
                        record = transaction.copy()

                        # Decrypt the data if the requester is authorized
                        if "data" in record and record["data"]:
                            decrypted_data = self.decrypt_medical_data(
                                record["data"], authorized=True
                            )
                            if decrypted_data:
                                record["data"] = decrypted_data
                            else:
                                record["data"] = "ENCRYPTED"

                        records.append(record)

        return records

    def valid_chain(self, chain: List[Dict[str, Any]]) -> bool:
        """Validate the entire blockchain.

        Verifies that each block in the chain has a valid hash link to the previous
        block and that each block's proof of work is valid.

        Args:
            chain: A blockchain to validate

        Returns:
            True if the entire chain is valid, False otherwise
        """
        if not chain or len(chain) == 0:
            return False

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the previous block is correct
            if block.get("previous_hash") != self.hash(last_block):
                logger.warning(f"Invalid hash link at block {current_index}")
                return False

            # Create a simplified representation of transactions for proof validation
            transactions_for_validation = []
            tx_list = block.get("transactions", [])

            for tx in tx_list:
                # Handle regular transactions
                if all(k in tx for k in ("sender", "recipient", "amount")):
                    transactions_for_validation.append(
                        {
                            "sender": tx["sender"],
                            "recipient": tx["recipient"],
                            "amount": tx["amount"],
                        }
                    )
                # Handle medical records
                elif tx.get("type") == "MEDICAL_RECORD":
                    transactions_for_validation.append(
                        {
                            "type": "MEDICAL_RECORD",
                            "patient_id": tx.get("patient_id"),
                            "doctor_id": tx.get("doctor_id"),
                            "record_type": tx.get("record_type"),
                        }
                    )

            # Verify the nonce is valid for this block
            if not self.valid_proof(
                transactions_for_validation,
                block.get("previous_hash", ""),
                block.get("nonce", 0),
                MINING_DIFFICULTY,
            ):
                logger.warning(f"Invalid proof of work at block {current_index}")
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """Resolve conflicts between blockchain nodes by implementing consensus.

        This is the consensus algorithm that resolves conflicts by replacing
        our chain with the longest valid chain in the network.

        Returns:
            True if our chain was replaced with a longer valid chain,
            False if our chain is already the longest valid one
        """
        if not self.nodes:
            return False

        new_chain = None
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in self.nodes:
            try:
                response = requests.get(f"http://{node}/chain", timeout=3)

                if response.status_code == 200:
                    data = response.json()
                    length = data.get("length", 0)
                    chain = data.get("chain", [])

                    # Check if the length is longer and the chain is valid
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except (requests.RequestException, ValueError, KeyError) as e:
                logger.error(f"Error connecting to node {node}: {e}")
                continue

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            logger.info(f"Chain replaced with longer chain of length {max_length}")
            return True

        return False
