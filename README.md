# Blockchain Implementation Using Python

This repository contains a Python implementation of a basic blockchain structure. Initially, it served as a simple interaction API for hashing, proof of work (PoW), and blockchain information retrieval. It has now been revamped into a fully dynamic RESTful API suitable for blockchain interactions, mining, transaction management, node registration, and resolving conflicts.

## Definition and Representation of Blockchain

A blockchain is a distributed ledger, maintaining an immutable record of transactions. Each block in the blockchain includes transaction data, a timestamp, a proof-of-work (nonce), and a hash of the previous block, ensuring the chain's integrity.

Example block representation:

```python
block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'nonce': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

## Creating New Blocks

Upon initialization, the blockchain starts with a genesis block (the first block) which has no predecessors. New blocks are created through mining, involving proof-of-work computation.

## Understanding Proof of Work

Proof of Work (PoW) is an algorithm used to validate new blocks. It involves finding a computationally difficult-to-find number (nonce), ensuring security and preventing malicious activities. The hash of the block's contents, including the nonce, must meet specific difficulty criteria (e.g., ending with a certain number of zeros).

Example PoW implementation:

```python
from hashlib import sha256

x = 5
y = 0

while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "0":
    y += 1

print(f'The solution is y = {y}')
```

## REST API Endpoints

### Base URL
```
http://localhost:5000/
```

### Available Endpoints

- **GET `/`**: API status and endpoint information.
- **POST `/transactions/new`**: Submit new transaction.
  - JSON format: `{sender, recipient, amount, signature}`
- **GET `/chain`**: Retrieve the full blockchain.
- **GET `/mine`**: Mine a new block and add it to the blockchain.
- **POST `/nodes/register`**: Register new blockchain nodes.
  - JSON format: `{nodes: ["node_address_1", "node_address_2"]}`
- **GET `/nodes/resolve`**: Resolve blockchain conflicts through consensus.
- **GET `/nodes/get`**: List all registered nodes.

## Tech Stack Used

- **Flask**: For creating RESTful HTTP endpoints.
- **Requests**: For HTTP endpoint requests and JSON responses handling.

## How to Run the Project

1. Clone the repository:
```bash
git clone https://github.com/WomB0ComB0/hack-knight-25
```

2. Install `pipenv`:
```bash
pip3 install pipenv
```

3. Set up the environment:
```bash
pipenv sync
```

4. Run the blockchain server:
```bash
python -m blockchain
```

5. Test API endpoints using Postman or curl:

Example request for mining a new block:
```bash
curl -X GET http://localhost:5000/mine
```

Example transaction submission:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"sender": "address1", "recipient": "address2", "amount": 5, "signature": "signature_here"}' http://localhost:5000/transactions/new
```

---

