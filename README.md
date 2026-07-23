# TrialLens – Multi-Agent Clinical Trial Intelligence Copilot

TrialLens is an AI-powered clinical trial intelligence system that combines structured clinical trial metadata, adverse event reports, and unstructured clinical documents to provide citation-backed answers to complex research questions.

Unlike traditional document chatbots, TrialLens integrates structured APIs, document retrieval, table understanding, and multi-agent reasoning to generate verified responses supported by evidence from multiple sources.

> **Project Status:** 🚧 In Development

---

# Problem Statement

Clinical researchers, biotech analysts, and regulatory affairs teams often spend hours manually searching across multiple disconnected sources such as:

- ClinicalTrials.gov
- FDA Adverse Event Reporting System (FAERS)
- Clinical trial protocols
- Statistical Analysis Plans (SAPs)

Important information is distributed across structured databases and lengthy PDF documents, making it difficult to efficiently answer research questions that require evidence from multiple sources.

TrialLens aims to solve this by building a unified AI-powered research assistant capable of retrieving, verifying, and synthesizing information from both structured and unstructured clinical data.

---

# Objectives

The project aims to:

- Ingest structured clinical trial metadata
- Parse complex clinical trial PDF documents
- Extract tables separately from document text
- Build a Hybrid Retrieval-Augmented Generation (Hybrid RAG) pipeline
- Perform visual document retrieval for difficult layouts
- Answer questions using multiple specialized AI agents
- Verify responses before presenting them
- Provide citation-backed answers
- Measure system quality using automated evaluation

---

# Data Sources

TrialLens uses publicly available datasets.

- ClinicalTrials.gov API (v2)
- openFDA FAERS API
- Public clinical trial protocol PDFs
- Statistical Analysis Plans (SAPs)

---

# Planned Architecture

```
                         User
                           │
                    Next.js Frontend
                           │
                     FastAPI Backend
                           │
                  LangGraph Orchestrator
                           │
        ┌──────────────────┼───────────────────┐
        │                  │                   │
 Retriever Agent     Structured Agent    Safety Agent
        │                  │                   │
        │                  │                   │
 Hybrid Retrieval    ClinicalTrials API   openFDA API
        │
        │
    Vector Database
        │
        │
    PDF Parsing Pipeline
```

---

# Planned Features

- Clinical trial search
- Hybrid semantic + keyword retrieval
- Citation-backed question answering
- Clinical protocol parsing
- Table extraction
- Visual document retrieval
- Multi-agent reasoning
- Safety signal analysis
- Automated evaluation framework
- Observability and tracing

---

# Technology Stack

## Frontend

- Next.js
- TypeScript
- Tailwind CSS

## Backend

- FastAPI
- LangGraph
- Python

## Database

- PostgreSQL
- pgvector

## Retrieval

- Hybrid RAG
- Dense Embeddings
- BM25
- Reranking

## Document Processing

- Docling / unstructured.io
- Visual Document Retrieval
- Table Question Answering

## Evaluation

- RAGAS
- DeepEval

## Observability

- Langfuse / Arize Phoenix

---

# Repository Structure

```
TrialLens/
│
├── backend/
├── frontend/
├── docs/
├── docker/
├── scripts/
├── tests/
├── .github/
│
├── README.md
├── LICENSE
└── docker-compose.yml
```

---

# Development Roadmap

## Phase 0

- Repository setup
- Project structure
- Development environment
- Docker
- PostgreSQL
- Documentation

## Phase 1

- ClinicalTrials.gov API integration
- PDF ingestion pipeline
- Document parsing

## Phase 2

- Hybrid retrieval
- Visual document retrieval
- Table question answering

## Phase 3

- Multi-agent orchestration using LangGraph

## Phase 4

- Evaluation framework
- Golden dataset
- CI regression testing

## Phase 5

- Observability
- Deployment
- Documentation

---

# Current Status

Project initialization is currently in progress.

The repository structure, backend, frontend, Docker environment, and database are being prepared before implementing the ingestion and retrieval pipeline.

---

# License

This project is licensed under the MIT License.