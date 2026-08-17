# NetOps AI Agent: Autonomous ISP Diagnostics Copilot

A capstone project for the LLM Zoomcamp. This agentic RAG system acts as a Level 2 Network Support Engineer for local ISPs. It ingests router telemetry, retrieves technical documentation, and safely interacts with hardware APIs using Human-in-the-Loop (HITL) and self-correction guardrails.

## Features
* **Agentic RAG:** Combines vector search (ChromaDB) with live REST API tool calling.
* **Data Engineering:** Uses `dlt` to ingest router logs into DuckDB for fast analytics.
* **Hardware Integration:** Connects directly to MikroTik RouterOS v7.
* **Safe Execution:** Implements HITL gates for destructive actions (e.g., DHCP resets) and self-correcting retry loops for API timeouts.
* **Observability:** Full execution tracing and LLM-as-a-judge evaluation via Logfire and LangSmith.

## Setup
1. `pip install -r requirements.txt`
2. Configure `.env` with credentials (use `.env.example` as a template).
3. Run `python agent/netops_agent.py` to test the agent.
4. Run `python evaluate_agent.py` to run the evaluation suite.
