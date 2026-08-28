# Nebius x NVIDIA Global AI Hackathon Submission
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## 📌 Project Overview: OmniClaim & Agentic Security Platform

This repository is built for the **Nebius x NVIDIA Global AI Hackathon** ("Build the next frontier of AI on open infrastructure"). It provides an enterprise-grade multi-agent AI platform built on **Nebius Token Factory**, **Nebius Serverless Endpoints & Jobs**, and open-source **NVIDIA Nemotron** models.

The project demonstrates implementations across two primary competition tracks:
1. **Best Apps and Agents Track**: **OmniClaim-AI** – Autonomous Insurance Claim Processing & Fraud Detection Copilot utilizing multi-model routing (Nemotron 3 Ultra for deep reasoning + Nemotron 3 Nano for fast, cost-efficient calls).
2. **Coding and Agentic Engineering Track**: **SafeCode-AI** – Sandboxed vulnerability refactoring agent running inside Nebius Token Factory Sandboxes under **NVIDIA OpenShell** L7 proxy & kernel-level isolation.

---

## 🏗 Architecture & Tech Stack

```
+-----------------------------------------------------------------------+
|                           User / Web Client                           |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    FastAPI App / Serverless Endpoint                  |
+-----------------------------------------------------------------------+
         |                                                 |
         v (Routing)                                       v (Sandboxed)
+-----------------------------------+     +-----------------------------------+
|      OmniClaim Agent (Apps)       |     |       SafeCode Agent (Coding)     |
+-----------------------------------+     +-----------------------------------+
| Nemotron 3 Nano (Fast OCR/Parse)  |     | Nebius Token Factory Sandbox      |
| Nemotron 3 Ultra (Fraud Reasoning)|     | NVIDIA OpenShell Governance Proxy |
+-----------------------------------+     +-----------------------------------+
         |                                                 |
         +------------------------+------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|             Nebius Token Factory / Nebius AI Cloud Infrastructure      |
+-----------------------------------------------------------------------+
```

### Key Technical Components:
* **Nebius Token Factory**: Serving open-weight NVIDIA Nemotron models via OpenAI-compatible endpoints with high throughput.
* **NVIDIA Nemotron 3 Ultra (`nvidia/nemotron-4-340b-instruct`)**: Used for complex fraud pattern detection, multi-document reasoning, and security vulnerability patching.
* **NVIDIA Nemotron 3 Nano (`nvidia/nemotron-4-8b-instruct`)**: Used for high-speed metadata extraction, classification, and pre-filtering to minimize credit usage.
* **Nebius Serverless Endpoints**: Low-latency REST API serving for real-time agent interactions.
* **Nebius Serverless Jobs**: Asynchronous background worker queue for processing high-volume batch jobs (e.g., thousands of overnight insurance claims).
* **NVIDIA OpenShell**: Secure runtime sandbox preventing unauthorized egress, securing credentials, and enforcing safe tool execution.

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.10+
* Nebius Token Factory API Key (`NEBIUS_API_KEY`)

### 2. Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/nebius-nvidia-agent-platform.git
cd nebius-nvidia-agent-platform
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your Nebius credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
NEBIUS_API_KEY=your_nebius_api_key_here
NEBIUS_BASE_URL=https://api.studio.nebius.ai/v1/
MODEL_NVIDIA_NEMOTRON_ULTRA=nvidia/nemotron-4-340b-instruct
MODEL_NVIDIA_NEMOTRON_NANO=nvidia/nemotron-4-8b-instruct
```

### 4. Running the Platform API & Interactive Demo

Start the server:
```bash
python app.py
```
Or with full python path on Windows:
```bash
python -m uvicorn app:app --reload
```

Open your browser and navigate to:
* **Demo Landing Page**: [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Automated Tests

Run the test suite to verify agent routing, sandboxing logic, and Nebius serverless jobs:
```bash
python -m pytest -v
```

---

## 📜 License

This project is open source under the [Apache 2.0 License](LICENSE).
