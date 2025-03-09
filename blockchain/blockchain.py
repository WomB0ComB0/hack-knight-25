import binascii
import hashlib
import json
from collections import OrderedDict
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Global constants for blockchain operation
MINING_SENDER = "THE BLOCKCHAIN"  # Special identifier for mining rewards
MINING_REWARD = 1  # Amount of cryptocurrency awarded for mining a block
MINING_DIFFICULTY = 2  # Difficulty of the proof of work (number of leading zeros required)


class Blockchain:
    """
    A class that implements a blockchain with proof of work mining, transaction handling,
    and distributed consensus mechanisms.

    This blockchain implementation supports:
    - Creation and validation of blocks
    - Secure transaction processing with cryptographic signatures
    - Proof of work mining algorithm
    - Distributed node registration and consensus
    - Chain validation and conflict resolution

    Attributes:
        chain (list): The blockchain itself - a list of blocks.
        transactions (list): Pending transactions to be included in the next block.
        nodes (set): Set of nodes in the network for consensus.
        node_id (str): Unique identifier for this node.
    """

    def __init__(self):
        """
        Initialize a new Blockchain instance.

        Creates an empty blockchain with a genesis block, initializes an empty
        transaction list, and generates a unique node ID.
        """
        self.chain = []  # The blockchain - a list of blocks
        self.transactions = []  # Pending transactions for the next block
        self.nodes = set()  # Set of nodes in the network for consensus
        self.node_id = str(uuid4()).replace("-", "")  # Unique identifier for this node
        # Create the genesis block (first block in the chain)
        self.new_block(0, "00")

    def new_block(self, nonce: int, previous_hash: str = None) -> dict:
        """
        Create a new Block in the Blockchain.

        Creates a new block containing the current transactions, a timestamp,
        the block index, the nonce value from proof of work, and the hash of the
        previous block. After creating the block, it resets the transaction list.

        Args:
            nonce: The nonce found by the Proof of Work algorithm
            previous_hash: (Optional) Hash of previous Block. If not provided, 
                           the hash of the last block in the chain is used.

        Returns:
            A dictionary representing the new block that was added to the chain.
        """
        block = {
            "index": len(self.chain) + 1,  # Block number in sequence
            "timestamp": time(),  # Current timestamp
            "transactions": self.transactions,  # List of transactions
            "nonce": nonce,  # Proof of work value
            "previous_hash": previous_hash or self.hash(self.chain[-1]),  # Link to previous block
        }

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        Creates a new transaction to go into the next mined Block.

        Records a new transaction between a sender and recipient for a specified amount.
        This transaction will be included in the next block to be mined.

        Args:
            sender: Address (public key) of the Sender
            recipient: Address (public key) of the Recipient
            amount: Amount of cryptocurrency to transfer

        Returns:
            The index of the Block that will hold this transaction
        """
        self.transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )

        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: dict) -> str:
        """
        Creates a SHA-256 hash of a Block.

        This is a critical cryptographic function that ensures the integrity
        of the blockchain. It converts a block to a consistently ordered JSON string,
        then creates a SHA-256 hash of that string.

        Args:
            block: Block dictionary to hash

        Returns:
            SHA-256 hexadecimal digest representing the block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Returns the last Block in the chain.

        This property provides convenient access to the most recent block
        in the blockchain.

        Returns:
            The last (most recent) block in the chain
        """
        return self.chain[-1]

    def proof_of_work(self) -> int:
        """
        Execute the Proof of Work algorithm.

        This consensus mechanism requires computational work to validate blocks.
        It searches for a value (nonce) that when combined with the transactions
        and the hash of the last block produces a hash with a specific pattern
        (leading zeros determined by MINING_DIFFICULTY).

        Returns:
            The nonce value that satisfies the mining condition
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    @staticmethod
    def valid_proof(transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Validate a proof of work solution.

        Checks if the hash of the combined transactions, last block hash, and nonce
        meets the difficulty requirement (having a specific number of leading zeros).

        Args:
            transactions: List of transactions to include in the hash
            last_hash: Hash of the previous block
            nonce: Value to include in the hash to meet the difficulty requirement
            difficulty: Number of leading zeros required in the hash

        Returns:
            True if the proof is valid (hash has required number of leading zeros),
            False otherwise
        """
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes in the network.

        This method adds a node address to the set of nodes, allowing the blockchain
        to communicate with other nodes for consensus.

        Args:
            address: Address of the node (e.g., 'http://192.168.0.5:5000')

        Raises:
            ValueError: If the provided address is invalid
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

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Verify the signature of a transaction.

        Uses public key cryptography to verify that a transaction was signed
        by the owner of the sender address (public key).

        Args:
            sender_address: Sender's address (public key in hex format)
            signature: Cryptographic signature of the transaction (hex format)
            transaction: OrderedDict containing the transaction data

        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Import the public key
            public_key = RSA.importKey(binascii.unhexlify(sender_address))
            verifier = pkcs1_15.new(public_key)

            # Create a SHA hash of the transaction
            transaction_hash = SHA.new(str(transaction).encode("utf8"))

            # Verify the signature using the public key
            try:
                verifier.verify(transaction_hash, binascii.unhexlify(signature))
                return True
            except (ValueError, TypeError):
                return False
        except (ValueError, TypeError, binascii.Error) as e:
            print(f"Signature verification error: {e}")
            return False

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a new transaction to the list of pending transactions.

        Validates the transaction signature (except for mining rewards) and 
        adds the transaction to the pending transactions list if valid.

        Args:
            sender_address: Sender's address (public key)
            recipient_address: Recipient's address
            value: Transaction amount
            signature: Transaction signature

        Returns:
            The index of the block that will include this transaction if valid,
            False otherwise
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

    def valid_chain(self, chain: list) -> bool:
        """
        Validate the entire blockchain.

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
                return False

            # Check that the Proof of Work is correct
            transactions = block.get("transactions", [])[:-1]
            if not transactions:
                transactions = []

            # Convert to OrderedDict for consistent hashing
            transaction_elements = ["sender_address", "recipient_address", "value"]
            transactions = [
                OrderedDict((k, transaction.get(k)) for k in transaction_elements)
                for transaction in transactions
                if all(k in transaction for k in transaction_elements)
            ]

            # Verify the nonce is valid for this block
            if not self.valid_proof(
                transactions,
                block.get("previous_hash"),
                block.get("nonce"),
                MINING_DIFFICULTY,
            ):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """
        Resolve conflicts between blockchain nodes by implementing consensus.

        This is the consensus algorithm that resolves conflicts by replacing
        our chain with the longest valid chain in the network.

        Returns:
            True if our chain was replaced with a longer valid chain,
            False if our chain is already the longest valid one
        """
        if not self.nodes:
            return False

        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
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
                print(f"Error connecting to node {node}: {e}")
                continue

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False
