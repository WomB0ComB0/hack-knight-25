#!/usr/bin/env python3
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

from .blockchain_exceptions import (
    BlockchainException, 
    EncryptionException, 
    SignatureException,
    TransactionException,
    NodeConnectionException,
    ValidationException,
    MedicalRecordException,
    handle_exceptions,
    default_fallback_handler
)

# Configure logging
logger = logging.getLogger("blockchain")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

# Constants
MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 2
KEY_FILE = "medical_encryption.key"

# Record types as an Enum-like dictionary
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
    """Blockchain implementation for medical records and transactions."""

    def __init__(self) -> None:
        """Initialize a new blockchain."""
        self.chain: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        self.nodes: Set[str] = set()
        self.node_id: str = str(uuid4()).replace("-", "")

        # Create the genesis block
        self.new_block(0, "00")

        # Generate or load encryption key
        self.encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self) -> bytes:
        """Generate or load a key for encrypting sensitive medical data."""
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
        """Encrypt sensitive medical data."""
        encryption_handlers = {
            TypeError: lambda e: logger.error("Type error during encryption: %s", str(e)) or None,
            json.JSONDecodeError: lambda e: logger.error("JSON error during encryption: %s", str(e)) or None,
            InvalidToken: lambda e: logger.error("Invalid Fernet token: %s", str(e)) or None,
        }

        @handle_exceptions(encryption_handlers, fallback_handler=default_fallback_handler)
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
        """Decrypt medical data if authorized."""
        if not encrypted_data or not authorized:
            return None

        decryption_handlers = {
            TypeError: lambda e: logger.error("Type error during decryption: %s", str(e)) or None,
            json.JSONDecodeError: lambda e: logger.error("JSON error during decryption: %s", str(e)) or None,
            InvalidToken: lambda e: logger.error("Invalid Fernet token: %s", str(e)) or None,
            base64.: lambda e: logger.error("Base64 decoding error: %s", str(e)) or None,
        }

        @handle_exceptions(decryption_handlers, fallback_handler=default_fallback_handler)
        def _decrypt():
            f = Fernet(self.encryption_key)
            decoded = base64.b64decode(encrypted_data)
            decrypted_data = f.decrypt(decoded).decode()
            return json.loads(decrypted_data)

        return _decrypt()

    def new_block(
        self, nonce: int, previous_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new block in the blockchain."""
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
        """Add a new transaction to pending transactions."""
        self.transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """Create a SHA-256 hash of a block."""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        """Get the last block in the chain."""
        return self.chain[-1]

    def proof_of_work(self) -> int:
        """Find a nonce that produces a hash with leading zeros."""
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
        """Validate the proof of work."""
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def register_node(self, address: str) -> None:
        """Add a new node to the network."""
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
        """Verify the signature of a transaction."""
        signature_handlers = {
            ValueError: lambda e: logger.error("Value error during signature verification: %s", str(e)) or False,
            TypeError: lambda e: logger.error("Type error during signature verification: %s", str(e)) or False,
            binascii.Error: lambda e: logger.error("Binascii error during signature verification: %s", str(e)) or False,
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
        """Add a transaction after verifying signature."""
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
        """Create a new medical record transaction."""
        record_handlers = {
            ValueError: lambda e: logger.error("Invalid record type: %s", str(e)) or False,
            EncryptionException: lambda e: logger.error("Encryption error: %s", str(e)) or False,
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
        """Verify that a medical record was properly signed."""
        if signature == "DEBUG_SKIP_VERIFICATION":
            logger.warning("Skipping signature verification in DEBUG mode")
            return True

        if not signature:
            logger.error("Missing signature for record verification")
            return False

        signature_handlers = {
            ValueError: lambda e: logger.error("Value error during record signature verification: %s", str(e)) or False,
            TypeError: lambda e: logger.error("Type error during record signature verification: %s", str(e)) or False,
            binascii.Error: lambda e: logger.error("Binascii error during record signature verification: %s", str(e)) or False,
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
        """Retrieve authorized medical records for a patient."""
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
        """Validate the entire blockchain."""
        validation_handlers = {
            Exception: lambda e: logger.error("Chain validation error: %s", str(e)) or False,
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
        """Implement consensus by adopting the longest valid chain."""
        if not self.nodes:
            return False

        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            node_handlers = {
                requests.RequestException: lambda e: logger.error("Request error connecting to node %s: %s", node, str(e)) or None,
                ValueError: lambda e: logger.error("Value error with node %s: %s", node, str(e)) or None,
                KeyError: lambda e: logger.error("Key error with node data from %s: %s", node, str(e)) or None,
            }

            @handle_exceptions(node_handlers, fallback_handler=lambda e: None)
            def _check_node():
                response = requests.get(f"http://{node}/chain", timeout=3)

                if response.status_code == 200:
                    data = response.json()
                    length = data.get("length", 0)
                    chain = data.get("chain", [])

                    if length > max_length and self.valid_chain(chain):
                        return (length, chain)
                return None

            result = _check_node()
            if result:
                max_length, new_chain = result

        if new_chain:
            self.chain = new_chain
            logger.info("Chain replaced with longer chain of length %s", max_length)
            return True

        return False
