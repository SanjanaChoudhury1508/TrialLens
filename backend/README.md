# TrialLens Backend

The backend provides the API, data ingestion, retrieval pipeline, and multi-agent reasoning workflow for TrialLens.

## Overview

The backend is built with **Python, FastAPI, PostgreSQL/pgvector, LangGraph, and Gemini**.

It combines:

- Clinical trial data from ClinicalTrials.gov
- Adverse-event data from openFDA FAERS
- Clinical trial documents in PDF format
- Hybrid document retrieval
- Multi-agent question answering
- Evidence aggregation and verification

The backend exposes a REST API that the frontend uses to submit research questions and receive evidence-grounded answers.

## Architecture

```text
User Question
      │
      ▼
   FastAPI
      │
      ▼
 LangGraph Router
      │
      ├───────────────┐
      ▼               ▼
 Retriever       Structured Data
   Agent             Agent
      │               │
      │               └── ClinicalTrials.gov
      │
      ├───────────────┐
      ▼               ▼
 Safety Agent    Evidence Aggregator
      │               │
      └── openFDA     ▼
          FAERS     Synthesis Agent
                       │
                       ▼
                 Critic / Verifier
                       │
                       ▼
                 Final Answer