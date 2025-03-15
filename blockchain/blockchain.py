#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0611

import binascii
import hashlib
import json
import logging
import os
import requests
from collections import OrderedDict
from time import time
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse
from uuid import uuid4

import base64
from cryptography.fernet import Fernet, InvalidToken
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from blockchain_exceptions import (
    EncryptionException,
    handle_exceptions,
    default_fallback_handler,
)

logger = logging.getLogger("blockchain")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

# Constants used throughout the blockchain implementation
MINING_SENDER = "THE BLOCKCHAIN"  # Special identifier for mining rewards
MINING_REWARD = 1  # Amount of cryptocurrency rewarded for mining a block
MINING_DIFFICULTY = 2  # Number of leading zeros required for proof-of-work
KEY_FILE = "medical_encryption.key"  # File to store encryption keys

# Dictionary of valid medical record types supported by the blockchain
RECORD_TYPES: Dict[str, str] = {
    "DIAGNOSTIC": "diagnostic_report",  # Medical diagnostic information
    "PRESCRIPTION": "prescription",  # Medication prescriptions
    "LAB_RESULT": "lab_result",  # Laboratory test results
    "VITAL_SIGNS": "vital_signs",  # Patient vital measurements
    "CONSULTATION": "consultation_notes",  # Notes from doctor consultations
    "SURGERY": "surgery_record",  # Surgical procedure records
    "IMAGING": "imaging_report",  # X-rays, MRIs, CT scans, etc.
    "VACCINATION": "vaccination",  # Vaccination/immunization records
    "ALLERGY": "allergy_record",  # Patient allergy information
    "CONSENT": "patient_consent",  # Patient consent forms
}


class Blockchain:
    """
    Blockchain implementation for medical records and transactions.

    This class provides a comprehensive implementation of a blockchain specifically
    designed for storing and managing medical records. It includes features for:

    - Creating and validating blocks in the chain
    - Processing medical record transactions with proper encryption
    - Verifying digital signatures for records and transactions
    - Managing access control for sensitive medical data
    - Implementing consensus mechanisms for distributed deployment

    The implementation prioritizes security, data privacy, and the special requirements
    of medical record management while maintaining blockchain fundamentals.
    """

    def __init__(self) -> None:
        """
        Initialize a new blockchain.

        Creates a new blockchain with an empty transaction pool, initializes the
        genesis block, and sets up encryption keys for secure medical data storage.

        Attributes:
            chain (List[Dict]): The blockchain itself, a list of block dictionaries
            transactions (List[Dict]): Current pending transactions
            nodes (Set[str]): Set of registered nodes in the network
            node_id (str): Unique identifier for this blockchain node
            encryption_key (bytes): Key used for encrypting/decrypting medical data
        """
        self.chain: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        self.nodes: Set[str] = set()
        self.node_id: str = str(uuid4()).replace("-", "")

        # Create the genesis block
        self.new_block(0, "00")

        # Generate or load encryption key
        self.encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self) -> bytes:
        """
        Generate or load a key for encrypting sensitive medical data.

        Attempts to load an existing encryption key from the KEY_FILE.
        If the file doesn't exist, generates a new Fernet key and saves it.
        Sets proper file permissions to protect the key.

        Returns:
            bytes: The encryption key for securing medical data

        Note:
            If there's an error accessing the key file, falls back to an
            in-memory temporary key (which won't persist between restarts).
        """
        try:
            if os.path.exists(KEY_FILE):
                with open(KEY_FILE, "rb") as f:
                    return f.read()

            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(KEY_FILE) or ".", exist_ok=True)

            with open(KEY_FILE, "wb") as f:
                f.write(key)
            os.chmod(KEY_FILE, 0o600)  # Read/write for owner only
            return key

        except (IOError, OSError) as e:
            logger.error("Error accessing encryption key file: %s", e)
            logger.warning("Using temporary in-memory encryption key")
            return Fernet.generate_key()

    def encrypt_medical_data(self, data: Any) -> Optional[str]:
        """
        Encrypt sensitive medical data.

        Converts data to JSON, encrypts it using Fernet symmetric encryption,
        and encodes the result in base64 for storage in the blockchain.

        Args:
            data (Any): The medical data to encrypt (must be JSON serializable)

        Returns:
            Optional[str]: Base64-encoded encrypted data, or None if encryption failed

        Note:
            Uses exception handlers to gracefully manage encryption errors
        """
        encryption_handlers = {
            TypeError: lambda e: logger.error(
                "Type error during encryption: %s", str(e)
            )
            or None,
            json.JSONDecodeError: lambda e: logger.error(
                "JSON error during encryption: %s", str(e)
            )
            or None,
            InvalidToken: lambda e: logger.error("Invalid Fernet token: %s", str(e))
            or None,
        }

        @handle_exceptions(
            encryption_handlers, fallback_handler=default_fallback_handler
        )
        def _encrypt():
            if not data:
                return None

            f = Fernet(self.encryption_key)
            json_data = json.dumps(data)
            encrypted_data = f.encrypt(json_data.encode())
            return base64.b64encode(encrypted_data).decode()

        return _encrypt()

    def decrypt_medical_data(
        self, encrypted_data: Optional[str], authorized: bool = False
    ) -> Optional[Any]:
        """
        Decrypt medical data if authorized.

        Decrypts previously encrypted medical data, but only if the requester
        is authorized to access it.

        Args:
            encrypted_data (Optional[str]): Base64-encoded encrypted data
            authorized (bool): Whether the requester is authorized to access this data

        Returns:
            Optional[Any]: The decrypted data as a Python object, or None if:
                - encrypted_data is None
                - authorized is False
                - decryption fails for any reason

        Note:
            Uses exception handlers to gracefully manage decryption errors
        """
        if not encrypted_data or not authorized:
            return None

        decryption_handlers = {
            TypeError: lambda e: logger.error(
                "Type error during decryption: %s", str(e)
            )
            or None,
            json.JSONDecodeError: lambda e: logger.error(
                "JSON error during decryption: %s", str(e)
            )
            or None,
            InvalidToken: lambda e: logger.error("Invalid Fernet token: %s", str(e))
            or None,
            binascii.Error: lambda e: logger.error("Base64 decoding error: %s", str(e))
            or None,
        }

        @handle_exceptions(
            decryption_handlers, fallback_handler=default_fallback_handler
        )
        def _decrypt():
            f = Fernet(self.encryption_key)
            decoded = base64.b64decode(encrypted_data)
            decrypted_data = f.decrypt(decoded).decode()
            return json.loads(decrypted_data)

        return _decrypt()

    def new_block(
        self, nonce: int, previous_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new block in the blockchain.

        Creates a new block with the current pending transactions and
        appends it to the chain.

        Args:
            nonce (int): The proof-of-work nonce that validates this block
            previous_hash (Optional[str]): Hash of the previous block
                If None, calculates it from the previous block

        Returns:
            Dict[str, Any]: The newly created block

        Note:
            After creating a block, the pending transaction list is cleared
        """
        prev_hash = (
            previous_hash if previous_hash is not None else self.hash(self.chain[-1])
        )

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.transactions.copy(),
            "nonce": nonce,
            "previous_hash": prev_hash,
        }

        self.transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        Add a new transaction to pending transactions.

        Creates a basic financial transaction to be included in the next block.

        Args:
            sender (str): Address of the transaction sender
            recipient (str): Address of the transaction recipient
            amount (int): Amount to transfer

        Returns:
            int: Index of the block that will contain this transaction
        """
        self.transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        Create a SHA-256 hash of a block.

        Generates a unique hash representing the block contents.
        This is critical for maintaining the immutability and
        integrity of the blockchain.

        Args:
            block (Dict[str, Any]): Block to hash

        Returns:
            str: Hexadecimal string representation of the block hash
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        """
        Get the last block in the chain.

        Returns:
            Dict[str, Any]: The most recently added block
        """
        return self.chain[-1]

    def proof_of_work(self) -> int:
        """
        Find a nonce that produces a hash with leading zeros.

        Implements the Proof of Work consensus algorithm, which requires
        finding a number (nonce) that when combined with the previous block's hash
        produces a hash with a certain number of leading zeros.

        Returns:
            int: The nonce that satisfies the difficulty requirement

        Note:
            The difficulty is controlled by MINING_DIFFICULTY constant
        """
        last_block = self.last_block
        last_hash = self.hash(last_block)

        nonce = 0
        while not self.valid_proof(self.transactions, last_hash, nonce):
            nonce += 1

        return nonce

    @staticmethod
    def valid_proof(
        transactions: List[Dict[str, Any]],
        last_hash: str,
        nonce: int,
        difficulty: int = MINING_DIFFICULTY,
    ) -> bool:
        """
        Validate the proof of work.

        Checks if a given nonce creates a hash with the required number
        of leading zeros when combined with the transactions and previous hash.

        Args:
            transactions (List[Dict]): List of transactions to include in the proof
            last_hash (str): Hash of the previous block
            nonce (int): The proof-of-work nonce to validate
            difficulty (int): Number of leading zeros required (default: MINING_DIFFICULTY)

        Returns:
            bool: True if the proof is valid, False otherwise
        """
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def register_node(self, address: str) -> None:
        """
        Add a new node to the network.

        Registers another blockchain node to maintain a distributed network.

        Args:
            address (str): Address of node to add (URL/IP)

        Raises:
            ValueError: If the address is invalid

        Note:
            Accepts addresses with or without schemes (http://)
        """
        try:
            parsed_url = urlparse(address)
            if parsed_url.netloc:
                self.nodes.add(parsed_url.netloc)
            elif parsed_url.path:
                # Accept URLs without scheme like '192.168.0.5:5000'
                self.nodes.add(parsed_url.path)
            else:
                raise ValueError("Invalid URL")
        except ValueError as e:
            raise ValueError(f"Invalid URL: {e}") from e

    def verify_transaction_signature(
        self, sender_address: str, signature: str, transaction: Dict[str, Any]
    ) -> bool:
        """
        Verify the signature of a transaction.

        Confirms that a transaction was signed by the owner of the sender address
        using RSA digital signatures (PKCS#1 v1.5).

        Args:
            sender_address (str): Hex-encoded public key of the sender
            signature (str): Hex-encoded signature to verify
            transaction (Dict[str, Any]): The transaction data that was signed

        Returns:
            bool: True if signature is valid, False otherwise or if verification fails

        Note:
            Uses exception handlers to gracefully manage verification errors
        """
        signature_handlers = {
            ValueError: lambda e: logger.error(
                "Value error during signature verification: %s", str(e)
            )
            or False,
            TypeError: lambda e: logger.error(
                "Type error during signature verification: %s", str(e)
            )
            or False,
            binascii.Error: lambda e: logger.error(
                "Binascii error during signature verification: %s", str(e)
            )
            or False,
        }

        @handle_exceptions(signature_handlers, fallback_handler=lambda e: False)
        def _verify():
            public_key = RSA.importKey(binascii.unhexlify(sender_address))
            verifier = pkcs1_15.new(public_key)
            h = SHA.new(str(transaction).encode("utf8"))
            verifier.verify(h, binascii.unhexlify(signature))
            return True

        return _verify()

    def submit_transaction(
        self, sender_address: str, recipient_address: str, value: float, signature: str
    ) -> Union[int, bool]:
        """
        Add a transaction after verifying signature.

        Creates and adds a new financial transaction to the pending transactions
        pool after verifying the sender's signature, except for mining rewards
        which don't require signatures.

        Args:
            sender_address (str): Address of the sender
            recipient_address (str): Address of the recipient
            value (float): Amount to transfer
            signature (str): Digital signature proving authorization

        Returns:
            Union[int, bool]: Block index that will include this transaction,
                              or False if the signature is invalid

        Note:
            Mining rewards (from MINING_SENDER) don't require signature verification
        """
        transaction = OrderedDict(
            {
                "sender_address": sender_address,
                "recipient_address": recipient_address,
                "value": value,
            }
        )

        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1

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
        """
        Create a new medical record transaction.

        Adds a new medical record to the blockchain with proper encryption
        and access control. Verifies that the healthcare provider has
        properly authorized this record addition through their signature.

        Args:
            patient_id (str): Identifier for the patient
            doctor_id (str): Identifier for the healthcare provider
            record_type (str): Type of medical record (must be in RECORD_TYPES.values())
            medical_data (Any): The medical data to encrypt and store
            access_list (Optional[List[str]]): List of IDs authorized to access this record
                                              Defaults to [patient_id, doctor_id]
            signature (Optional[str]): Digital signature from the healthcare provider

        Returns:
            Union[int, bool]: Block index that will include this record,
                              or False if validation fails

        Note:
            - Record types are validated against the RECORD_TYPES dictionary
            - Medical data is encrypted before storage
            - An access_list controls who can decrypt the data later
        """
        record_handlers = {
            ValueError: lambda e: logger.error("Invalid record type: %s", str(e))
            or False,
            EncryptionException: lambda e: logger.error("Encryption error: %s", str(e))
            or False,
        }

        @handle_exceptions(record_handlers, fallback_handler=lambda e: False)
        def _create_record():
            if record_type not in RECORD_TYPES.values():
                raise ValueError(
                    f"Invalid record type. Must be one of: {', '.join(RECORD_TYPES.values())}"
                )

            encrypted_data = self.encrypt_medical_data(medical_data)
            if encrypted_data is None and medical_data is not None:
                logger.error("Failed to encrypt medical data")
                return False

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

            if doctor_id != MINING_SENDER and not self.verify_record_signature(
                doctor_id, signature, record
            ):
                logger.warning(
                    "Record signature verification failed for doctor_id: %s", doctor_id
                )
                return False

            self.transactions.append(record)
            return self.last_block["index"] + 1

        return _create_record()

    def verify_record_signature(
        self, provider_id: str, signature: Optional[str], record: Dict[str, Any]
    ) -> bool:
        """
        Verify that a medical record was properly signed.

        Confirms that a medical record was signed by the healthcare provider
        who created it, ensuring authenticity and integrity.

        Args:
            provider_id (str): Identifier (public key) of the healthcare provider
            signature (Optional[str]): Digital signature to verify
            record (Dict[str, Any]): The medical record that was signed

        Returns:
            bool: True if signature is valid, False otherwise

        Note:
            - Special "DEBUG_SKIP_VERIFICATION" signature bypasses verification for testing
            - During verification, the encrypted data is replaced with a placeholder
              to ensure consistent verification regardless of encryption
        """
        if signature == "DEBUG_SKIP_VERIFICATION":
            logger.warning("Skipping signature verification in DEBUG mode")
            return True

        if not signature:
            logger.error("Missing signature for record verification")
            return False

        signature_handlers = {
            ValueError: lambda e: logger.error(
                "Value error during record signature verification: %s", str(e)
            )
            or False,
            TypeError: lambda e: logger.error(
                "Type error during record signature verification: %s", str(e)
            )
            or False,
            binascii.Error: lambda e: logger.error(
                "Binascii error during record signature verification: %s", str(e)
            )
            or False,
        }

        @handle_exceptions(signature_handlers, fallback_handler=lambda e: False)
        def _verify():
            record_for_verification = record.copy()
            if "data" in record_for_verification:
                record_for_verification["data"] = "SIGNATURE_PLACEHOLDER"

            public_key = RSA.importKey(binascii.unhexlify(provider_id))
            verifier = pkcs1_15.new(public_key)

            record_hash = SHA.new(
                json.dumps(record_for_verification, sort_keys=True).encode("utf8")
            )

            verifier.verify(record_hash, binascii.unhexlify(signature))
            return True

        return _verify()

    def get_patient_records(
        self, patient_id: str, requester_id: str, record_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve authorized medical records for a patient.

        Searches the entire blockchain for medical records belonging to a
        specific patient. Only returns records that the requester is authorized
        to access, and optionally filters by record type.

        Args:
            patient_id (str): ID of the patient whose records to retrieve
            requester_id (str): ID of the entity requesting access
            record_type (Optional[str]): If provided, only returns records of this type

        Returns:
            List[Dict[str, Any]]: List of authorized medical records with decrypted data
                                 if the requester has access rights

        Note:
            - Records are only returned if requester_id is in the record's access_list
            - Data is automatically decrypted if the requester is authorized
            - If decryption fails, the data field shows "ENCRYPTED"
        """
        records = []

        for block in self.chain:
            for transaction in block["transactions"]:
                if (
                    transaction.get("type") == "MEDICAL_RECORD"
                    and transaction.get("patient_id") == patient_id
                ):

                    if record_type and transaction.get("record_type") != record_type:
                        continue

                    access_list = transaction.get("access_list", [])
                    if requester_id in access_list:
                        record = transaction.copy()

                        if "data" in record and record["data"]:
                            decrypted_data = self.decrypt_medical_data(
                                record["data"], authorized=True
                            )
                            record["data"] = (
                                decrypted_data if decrypted_data else "ENCRYPTED"
                            )

                        records.append(record)

        return records

    def valid_chain(self, chain: List[Dict[str, Any]]) -> bool:
        """
        Validate the entire blockchain.

        Ensures the integrity of a blockchain by verifying that:
        1. Each block's previous_hash matches the hash of the actual previous block
        2. The proof-of-work for each block is valid

        Args:
            chain (List[Dict[str, Any]]): Blockchain to validate

        Returns:
            bool: True if the entire chain is valid, False if any validation fails

        Note:
            This is critical for the consensus mechanism and resolving conflicts
            between nodes in the distributed network.
        """
        validation_handlers = {
            Exception: lambda e: logger.error("Chain validation error: %s", str(e))
            or False,
        }

        @handle_exceptions(validation_handlers, fallback_handler=lambda e: False)
        def _validate():
            if not chain:
                return False

            last_block = chain[0]
            current_index = 1

            while current_index < len(chain):
                block = chain[current_index]

                if block.get("previous_hash") != self.hash(last_block):
                    logger.warning("Invalid hash link at block %s", current_index)
                    return False

                transactions_for_validation = []
                for tx in block.get("transactions", []):
                    if all(k in tx for k in ("sender", "recipient", "amount")):
                        transactions_for_validation.append(
                            {
                                "sender": tx["sender"],
                                "recipient": tx["recipient"],
                                "amount": tx["amount"],
                            }
                        )
                    elif tx.get("type") == "MEDICAL_RECORD":
                        transactions_for_validation.append(
                            {
                                "type": "MEDICAL_RECORD",
                                "patient_id": tx.get("patient_id"),
                                "doctor_id": tx.get("doctor_id"),
                                "record_type": tx.get("record_type"),
                            }
                        )

                if not self.valid_proof(
                    transactions_for_validation,
                    block.get("previous_hash", ""),
                    block.get("nonce", 0),
                    MINING_DIFFICULTY,
                ):
                    logger.warning("Invalid proof of work at block %s", current_index)
                    return False

                last_block = block
                current_index += 1

            return True

        return _validate()

    def resolve_conflicts(self) -> bool:
        """
        Implement consensus by adopting the longest valid chain.

        Contacts all registered nodes and finds the longest valid blockchain.
        If a longer valid chain is found, replaces the current chain.
        This is the consensus algorithm that ensures all nodes in the network
        eventually agree on the same blockchain state.

        Returns:
            bool: True if our chain was replaced, False if our chain is authoritative

        Note:
            - Only replaces the chain if a longer valid chain is found
            - Uses a factory pattern to create properly scoped node checkers
            - Handles network and data errors gracefully
        """
        if not self.nodes:
            return False

        new_chain = None
        max_length = len(self.chain)

        # Create a factory function that returns a properly scoped node checker
        def create_node_checker(node_url):
            node_handlers = {
                requests.RequestException: lambda e: logger.error(
                    "Request error connecting to node %s: %s", node_url, str(e)
                )
                or None,
                ValueError: lambda e: logger.error(
                    "Value error with node %s: %s", node_url, str(e)
                )
                or None,
                KeyError: lambda e: logger.error(
                    "Key error with node data from %s: %s", node_url, str(e)
                )
                or None,
            }

            @handle_exceptions(node_handlers, fallback_handler=lambda e: None)
            def _check_node():
                response = requests.get(f"http://{node_url}/chain", timeout=3)

                if response.status_code == 200:
                    data = response.json()
                    length = data.get("length", 0)
                    chain = data.get("chain", [])

                    if length > max_length and self.valid_chain(chain):
                        return (length, chain)
                return None

            return _check_node

        for node in self.nodes:
            check_node = create_node_checker(node)
            result = check_node()
            if result:
                max_length, new_chain = result

        if new_chain:
            self.chain = new_chain
            logger.info("Chain replaced with longer chain of length %s", max_length)
            return True

        return False
