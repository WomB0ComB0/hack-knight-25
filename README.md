# Hack Knight '25: Secure Blockchain-Based Healthcare Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Bun](https://img.shields.io/badge/Bun-latest-orange)](https://bun.sh/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC)](https://tailwindcss.com/)

Hack Knight '25 is a decentralized healthcare management ecosystem that leverages blockchain technology to ensure the integrity, security, and portability of medical records. By combining a robust Python-based blockchain backend with a high-performance Next.js frontend, the platform provides a transparent, immutable ledger for patient data, medical appointments, and provider interactions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

Traditional healthcare data management systems often suffer from fragmentation, lack of interoperability, and vulnerability to centralized points of failure. **Hack Knight '25** addresses these challenges by implementing a custom-built blockchain tailored for healthcare.

The system utilizes a **Proof-of-Work (PoW)** consensus mechanism to secure the ledger. Every medical record added to the system is hashed, linked to previous blocks, and distributed across the network nodes. With integrated **Fernet symmetric encryption**, sensitive patient data (PHI) remains confidential, accessible only to authorized entities holding the decryption keys.

---

## Features

### Core Blockchain Engine
- **Custom Blockchain Core**: Native implementation of a linked-block structure with SHA-256 cryptographic hashing.
- **Proof-of-Work (PoW)**: Robust mining algorithm (Nonce-based) ensures network security and prevents record tampering.
- **Immutable Ledger**: Once a medical record is mined into a block, it cannot be altered without recalculating every subsequent hash.
- **Consensus Logic**: Automatic conflict resolution utilizing the "Longest Chain Rule" for multi-node synchronization.

### Healthcare & Security
- **Medical Encryption Layer**: Integrated symmetric encryption (via `medical_encryption.key`) to protect Protected Health Information (PHI) at rest.
- **Healthcare Data Models**: Specialized schemas for appointments, patient registration, and provider credentials.
- **Auditability**: Complete, timestamped history of every medical transaction.

### Modern Web Experience
- **Next.js 14 Dashboard**: A high-performance, React-based interface for patients and providers.
- **Real-time Blockchain Metrics**: Visual representation of chain height, mining difficulty, and transaction volume via the `BlockchainInfoCard`.
- **Responsive UI/UX**: Built with Radix UI, Tailwind CSS, and Shadcn/UI for a seamless mobile and desktop experience.
- **Interactive Chat**: Integrated patient-provider communication interface.
- **Storybook Integration**: Documented and isolated UI component development for design consistency.

---

## Architecture

The project follows a decoupled micro-service architecture, separating the cryptographic heavy-lifting of the blockchain from the user-facing application.

```mermaid
graph TD
    subgraph Frontend_Layer [Next.js 14 Client]
        Dashboard[Patient Dashboard]
        Register[Registration System]
        Appts[Appointment Manager]
        Chat[Provider Chat UI]
        API_Client[API Client & Hooks]
    end

    subgraph API_Gateway [Communication Layer]
        Flask_API[Flask REST Server]
        Middleware[Auth & Logging]
    end

    subgraph Blockchain_Engine [Core Backend]
        BC_Manager[Blockchain Manager]
        Mempool[Transaction Pool]
        Miner[PoW Mining Engine]
        Enc[Symmetric Encryption Layer]
        Consensus[Node Consensus Logic]
    end

    subgraph Persistence [Data Layer]
        Ledger[(Immutable Ledger)]
        State[(Node State)]
        Keys[(Medical Keys)]
    end

    Dashboard --> API_Client
    API_Client --> Flask_API
    Flask_API --> BC_Manager
    BC_Manager --> Mempool
    Mempool --> Miner
    Miner --> Ledger
    BC_Manager --> Enc
    Enc --> Keys
    Flask_API --> Consensus
    Consensus --> State
```

---

## Project Structure

### Blockchain Backend (`/blockchain`)
- `blockchain.py`: The core logic for block creation, hashing, and Proof-of-Work.
- `app.py`: Flask-based REST API exposing blockchain functionality.
- `healthcare_structure.py`: Definitions for medical records and healthcare-specific data objects.
- `auth_service.py`: Handles user authentication and role-based access.
- `medical_encryption.key`: The symmetric key used for PHI encryption.

### Frontend (`/frontend`)
- `src/app/`: Next.js App Router directories for `dashboard`, `chat`, `signin`, and `register`.
- `src/components/`: Modular UI components, including specialized `blockchain-info-card` and `patient-dashboard`.
- `src/hooks/`: Custom React hooks for data fetching and UI state.
- `src/lib/utils.ts`: Utility functions for Tailwind class merging and data formatting.

---

## Quick Start

### Prerequisites
- **Python**: 3.9+
- **Node.js**: 18+ or **Bun** (Recommended)
- **Git**

### 1. Installation

Clone the repository and install dependencies for both the frontend and the blockchain service.

```bash
# Clone the repository
git clone https://github.com/WomB0ComB0/hack-knight-25.git
cd hack-knight-25

# Install Frontend dependencies
cd frontend
bun install

# Install Backend dependencies
cd ../blockchain
pip install -r requirements.txt
```

### 2. Launching the Services

You can start the services independently.

**Start the Blockchain Backend:**
```bash
cd blockchain
python app.py
```
*The backend will run on: `http://localhost:5000`*

**Start the Next.js Frontend:**
```bash
cd frontend
bun run dev
```
*The frontend will run on: `http://localhost:3000`*

---

## Usage

### Mining a Block
New medical transactions are held in a "mempool" (pending transactions) until they are mined. To finalize transactions and secure them into the ledger:
```bash
curl -X GET http://localhost:5000/mine
```

### Adding a Medical Record
Submit a POST request with the transaction details. The `medical_data` field is automatically encrypted by the `MedicalEncryption` service before storage.
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "sender": "Doctor_ID_082",
  "recipient": "Patient_UUID_44",
  "amount": 1,
  "medical_data": "Diagnosis: Type II Diabetes. Recommendation: Low glycemic diet."
}' \
http://localhost:5000/transactions/new
```

### Registering Network Nodes
To form a decentralized cluster, register neighboring nodes to enable consensus:
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
  "nodes": ["http://192.168.1.15:5000", "http://192.168.1.20:5000"]
}' \
http://localhost:5000/nodes/register
```

---

## Configuration

### Backend Configuration (`blockchain/config.ini`)
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `difficulty` | Number of leading zeros required for a valid hash (PoW) | `4` |
| `mining_reward` | Tokens granted to the node that successfully mines a block | `1` |
| `node_identifier` | Unique UUID for the current network node | `random-uuid` |

### Frontend Environment (`frontend/.env`)
```env
NEXT_PUBLIC_BLOCKCHAIN_API=http://localhost:5000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## API Reference

### Blockchain Core API
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/chain` | GET | Returns the full blockchain ledger and current chain length. |
| `/mine` | GET | Triggers the mining process for all pending transactions. |
| `/transactions/new` | POST | Creates a new medical transaction/record. |
| `/nodes/register` | POST | Adds new neighbor nodes to the internal registry. |
| `/nodes/resolve` | GET | Runs the consensus algorithm to ensure the node has the longest chain. |

### Application & Scheduling API
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/appointments` | GET | Fetches all scheduled medical appointments. |
| `/api/appointments` | POST | Creates a new appointment entry in the system. |
| `/api/appointments/[id]` | DELETE | Removes a specific appointment by ID. |
| `/api/health` | GET | Checks the health status of the API and database connectivity. |

---

## Development

### UI Component Development
The project uses **Storybook** for developing UI components in isolation. This ensures that the design system remains robust across the dashboard.
```bash
cd frontend
bun run storybook
```

### Code Style & Linting
- **Frontend**: Prettier and ESLint are configured for TypeScript.
- **Backend**: Follows PEP 8 standards.

### Core Logic: Proof of Work
The mining algorithm resides in `blockchain/blockchain.py`:
```python
def proof_of_work(self, last_proof):
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
        proof += 1
    return proof
```

---

## Contributing

1. **Fork the Repository**: Create your own fork of the project.
2. **Create a Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add some amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**: Submit your changes for review.

---

## Roadmap

- [ ] **Smart Contracts**: Implement programmable medical logic (e.g., auto-release of insurance funds).
- [ ] **Zero-Knowledge Proofs (ZKP)**: Allow patients to prove eligibility/health status without revealing underlying PHI.
- [ ] **Mobile Integration**: Dedicated React Native app for patient access on the go.
- [ ] **Multi-Signature Records**: Require both doctor and patient signatures before a record is committed to the block.
- [ ] **IPFS Integration**: Move large medical images (DICOM/X-Rays) to IPFS, storing only the hash on the blockchain.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.