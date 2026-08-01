# TrialLens – Multi-Agent Clinical Trial Intelligence Copilot
> **Current Version:** v0.4.0 (Metadata RAG Complete)
>
> TrialLens currently supports metadata-based Retrieval-Augmented Generation (RAG) using ClinicalTrials.gov data, PostgreSQL + pgvector, and Gemini 2.5 Flash. PDF ingestion, Hybrid Retrieval, and LangGraph orchestration are under active development.

TrialLens is an AI-powered clinical trial intelligence system that combines structured clinical trial metadata, adverse event reports, and unstructured clinical documents to provide citation-backed answers to complex research questions.

Unlike traditional document chatbots, TrialLens integrates structured APIs, document retrieval, table understanding, and multi-agent reasoning to generate verified responses supported by evidence from multiple sources.

> **Project Status:**
🟡 Active Development

Current milestone:
✅ Metadata RAG Pipeline Complete

Next milestone:
⬜ PDF Knowledge Base Integration

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

# Current Architecture
                         User
                           │
                     Python Script
                           │
                    RAG Pipeline
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
 Retrieval Service                   Prompt Builder
        │                                     │
        ▼                                     ▼
Embedding Service                     Gemini 2.5 Flash
        │
        ▼
 PostgreSQL + pgvector
        │
        ▼
ClinicalTrials.gov Metadata

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
├── backend/app/

├── api/
├── database/
│   └── vector_store.py
├── ingestion/
│   ├── chunker.py
│   ├── parser.py
│   └── text_builder.py
├── services/
│   ├── embedding_service.py
│   ├── retrieval_service.py
│   ├── prompt_builder.py
│   ├── llm_service.py
│   └── rag_pipeline.py
├── models.py
├── config.py
├── frontend/
├── docs/
├── docker/
├── scripts/
├── index_metadata.py
├── test_vector_search.py
├── test_retrieval_service.py
├── test_prompt_builder.py
├── test_llm.py
└── test_rag_pipeline.py
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

## Demo

Coming soon.

- Semantic Retrieval
- RAG Question Answering
- Trial Search Interface
---

# Current Status

## Features

- ClinicalTrials.gov metadata ingestion
- PubMed publication discovery
- Structured trial metadata extraction
- Semantic text chunking
- BAAI BGE-small embedding generation
- PostgreSQL + pgvector vector database
- Semantic similarity search
- Retrieval Service
- Prompt Builder
- Gemini 2.5 Flash integration
- Retrieval-Augmented Generation (RAG) pipeline
- Source-aware AI responses with NCT trial IDs

Upcoming:
- PDF ingestion with Docling
- Hybrid Retrieval (Vector + Keyword Search)
- FastAPI REST API
- LangGraph Agent
- React Frontend

## Current Knowledge Base

- 300 Clinical Trials Indexed
- 2,534 Semantic Chunks
- BAAI/bge-small-en-v1.5 Embeddings
- PostgreSQL + pgvector Vector Store
- Gemini 2.5 Flash RAG Pipeline

## Example Query

Question

What breast cancer immunotherapy trials are available?

Answer

Based on the indexed ClinicalTrials.gov metadata, TrialLens retrieved relevant breast cancer immunotherapy studies and generated an evidence-grounded summary with supporting NCT identifiers.

Sources

- NCT00017537
- NCT02706392
- NCT04013542
---

# License

This project is licensed under the MIT License.