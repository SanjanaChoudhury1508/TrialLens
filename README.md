# TrialLens – Multi-Agent Clinical Trial Intelligence Copilot

> **Current Version:** v0.5.0
> **Status:** 🟢 Working MVP / Active Development

TrialLens is an AI-powered clinical trial intelligence system designed to help researchers retrieve, cross-reference, and analyze evidence from multiple clinical data sources.

The system combines:

- Structured clinical trial metadata
- Clinical trial PDF documents
- Pharmacovigilance / adverse-event data
- Dense vector retrieval
- Keyword retrieval
- Cross-encoder reranking
- LangGraph-based multi-agent orchestration
- Evidence aggregation
- LLM-based synthesis
- Critic-based verification
- Source-aware responses

TrialLens provides a single research interface for questions that would normally require manually searching across ClinicalTrials.gov, clinical publications, trial documents, and FDA adverse-event reports.

Unlike a traditional document chatbot, TrialLens is designed around **evidence retrieval, source separation, multi-agent reasoning, and verification**.

## Project Vision

The long-term goal of TrialLens is to become a multimodal clinical research copilot capable of answering complex questions by combining:

```text
ClinicalTrials.gov
        +
Clinical Documents
        +
FAERS
        +
Tables
        +
Figures
        +
Publications
        ↓
Multimodal Retrieval
        ↓
Multi-Agent Reasoning
        ↓
Evidence Verification
        ↓
Citation-Grounded Answer
```

The current implementation represents the working MVP of this architecture.

---

## Problem Statement

Clinical researchers, biotech analysts, and regulatory teams often need to manually cross-reference information across multiple disconnected sources.

Typical sources include:

- ClinicalTrials.gov
- FDA Adverse Event Reporting System (FAERS)
- Clinical trial publications
- Clinical trial protocols
- Statistical Analysis Plans (SAPs)
- Other clinical research documents

Important information is distributed across structured databases and lengthy unstructured documents.

For example, answering a question such as:

> "What safety signals and adverse events have been reported for avelumab, and what is the current status of the related clinical trial?"

may require:

1. Finding the relevant clinical trial.
2. Reading the trial publication.
3. Extracting safety information from the document.
4. Checking the current trial status from ClinicalTrials.gov.
5. Searching adverse-event reports from FAERS.
6. Separating trial evidence from pharmacovigilance evidence.
7. Synthesizing the information.
8. Verifying that the generated answer is supported by retrieved evidence.

Traditional search systems and basic document chatbots generally do not provide this complete cross-source workflow.

TrialLens addresses this problem by building a unified AI-powered research assistant that retrieves, combines, and verifies evidence from multiple clinical data sources.

---

## Objectives

TrialLens aims to:

- Ingest structured clinical trial metadata.
- Discover and ingest relevant clinical documents.
- Parse complex clinical PDF documents.
- Preserve document structure during ingestion.
- Generate semantic chunks from clinical documents.
- Store document embeddings in PostgreSQL + pgvector.
- Perform dense semantic retrieval.
- Perform keyword-based retrieval.
- Combine retrieval strategies using Reciprocal Rank Fusion.
- Rerank retrieved evidence using a cross-encoder.
- Query structured clinical trial APIs directly.
- Retrieve pharmacovigilance data from openFDA FAERS.
- Route questions to specialized AI agents.
- Aggregate evidence from multiple sources.
- Generate evidence-grounded answers using an LLM.
- Verify generated numerical claims against retrieved evidence.
- Preserve clinical trial identifiers throughout the pipeline.
- Provide source-aware evidence cards in the frontend.
- Evaluate answer quality using a golden question dataset.

---

## Key Features

### 1. Clinical Trial Metadata Intelligence

TrialLens can retrieve structured information from ClinicalTrials.gov including:

- Clinical trial identifier
- Trial title
- Official title
- Study type
- Recruitment / overall status
- Phase
- Enrollment
- Start date
- Completion date
- Sponsor
- Locations
- Trial summary

### 2. Clinical Document Retrieval

Clinical PDF documents can be processed using Docling.

The ingestion pipeline extracts document structure and converts relevant content into retrievable semantic chunks.

The system preserves information such as:

- Document sections
- Paragraphs
- Clinical terminology
- Tables / structured elements
- Trial identifiers
- Document metadata

### 3. Hybrid Retrieval

TrialLens combines multiple retrieval signals:

```text
Dense Vector Retrieval
        +
Keyword Retrieval
        ↓
Reciprocal Rank Fusion
        ↓
Source / Trial Scoring
        ↓
Cross-Encoder Reranking
        ↓
Relevant Evidence
```

This allows the system to handle both semantic questions and exact clinical terminology.

### 4. Pharmacovigilance Retrieval

TrialLens integrates openFDA FAERS for adverse-event reports.

The system can retrieve:

- Reported reactions
- Serious-event indicators
- Drug-specific reports
- Other available report-level information

FAERS results are kept separate from clinical trial evidence.

### 5. Multi-Agent Architecture

TrialLens uses LangGraph to coordinate specialized agents:

- Router Agent
- Retriever Agent
- Structured Data Agent
- Safety Signal Agent
- Evidence Aggregator
- Synthesis Agent
- Critic / Verification Agent

### 6. Evidence Verification

The critic stage checks generated numerical claims against retrieved evidence.

The system also applies grounding rules during answer generation to reduce unsupported claims.

### 7. Evidence-Oriented Frontend

The Next.js frontend provides:

- Research question input
- Loading states
- Evidence-grounded answer display
- Trial identifiers
- Source types
- Expandable evidence cards
- Clinical document sources
- ClinicalTrials.gov sources
- openFDA FAERS sources

---

## Data Sources

TrialLens currently works with publicly available clinical research data sources.

### ClinicalTrials.gov API v2

ClinicalTrials.gov is used as the structured clinical trial data source.

TrialLens retrieves information such as:

- NCT identifiers
- Trial titles
- Study phase
- Study status
- Enrollment
- Dates
- Sponsors
- Locations
- Study descriptions

The structured agent can perform both:

- Direct trial lookup using an NCT identifier
- Trial searches using extracted query terms

### openFDA FAERS

The openFDA FAERS API is used for pharmacovigilance and adverse-event retrieval.

TrialLens extracts information such as:

- Drug name
- Report date
- Serious-event indicators
- Seriousness categories
- Reported reactions

**Important Interpretation:** FAERS reports represent reported adverse events and should not be interpreted as proof that a particular drug caused a particular event.

TrialLens therefore explicitly labels FAERS evidence as pharmacovigilance data and maintains a distinction between:

```text
Reported Event
      ≠
Confirmed Drug Causality
```

### Clinical Trial Documents

TrialLens also uses publicly available clinical documents such as:

- Clinical trial publications
- Protocol-related documents
- Other research PDFs

These documents are processed through the PDF ingestion pipeline and indexed for retrieval.

### Future Data Sources

Planned future integrations include:

- Statistical Analysis Plans
- Additional public clinical documents
- Additional regulatory datasets
- Expanded publication sources

---

## Current System Architecture

The current TrialLens MVP follows the architecture below:

```text
                              User
                                │
                                ▼
                         Next.js Frontend
                                │
                                ▼
                         FastAPI Backend
                                │
                                ▼
                       LangGraph Orchestrator
                                │
                                ▼
                           Router Agent
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       Retriever Agent   Structured Agent    Safety Agent
              │                 │                 │
              ▼                 ▼                 ▼
       Retrieval Service  ClinicalTrials.gov  openFDA FAERS
              │                 │                 │
              ▼                 │                 │
      PostgreSQL + pgvector     │                 │
              │                 │                 │
              ▼                 │                 │
       Clinical PDF KB          │                 │
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                       Evidence Aggregator
                                │
                                ▼
                        Synthesis Agent
                                │
                                ▼
                       Critic / Verifier
                                │
                                ▼
                         Final Answer
                                │
                                ▼
                      Answer + Evidence Sources
```

---

## Retrieval-Augmented Generation Architecture

The document RAG pipeline consists of ingestion, parsing, chunking, embedding, retrieval, fusion, reranking, and synthesis.

```text
                    Clinical PDF
                         │
                         ▼
                       Docling
                         │
                         ▼
              Document Structure Extraction
                         │
                         ▼
                  Semantic Chunking
                         │
                         ▼
              BAAI/bge-small-en-v1.5
                         │
                         ▼
                 PostgreSQL + pgvector
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      Dense Retrieval          Keyword Retrieval
             │                       │
             └───────────┬───────────┘
                         ▼
              Reciprocal Rank Fusion
                         │
                         ▼
                 Source / Trial Scoring
                         │
                         ▼
                Cross-Encoder Reranking
                         │
                         ▼
                  Top Evidence Chunks
                         │
                         ▼
                   Prompt Builder
                         │
                         ▼
                       Gemini
                         │
                         ▼
                 Grounded Answer
```

### Dense Retrieval

TrialLens uses:

```text
BAAI/bge-small-en-v1.5
```

to generate 384-dimensional embeddings.

Embeddings are stored in PostgreSQL using pgvector.

### Keyword Retrieval

Keyword retrieval complements semantic retrieval by matching exact terms that are important in clinical research, including:

- NCT identifiers
- Drug names
- Endpoint names
- Hazard ratios
- Percentages
- Clinical terminology

### Reciprocal Rank Fusion

Dense and keyword retrieval results are combined using Reciprocal Rank Fusion (RRF).

This provides a unified ranking signal before the final reranking stage.

### Cross-Encoder Reranking

Retrieved candidates are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The cross-encoder provides a relevance score for candidate evidence relative to the user query.

These scores are treated as relevance scores and are not interpreted as probabilities or confidence percentages.

---

## Document Ingestion Architecture

Clinical documents are processed through a structured ingestion pipeline.

```text
PDF Document
     │
     ▼
Document Loader
     │
     ▼
Docling Parser
     │
     ▼
Document Structure
     │
     ├──────────────► Sections
     │
     ├──────────────► Text
     │
     ├──────────────► Tables / Structured Elements
     │
     └──────────────► Metadata
     │
     ▼
Semantic Chunker
     │
     ▼
Embedding Service
     │
     ▼
PostgreSQL + pgvector
```

The ingestion layer is designed to preserve document structure rather than treating a PDF as an undifferentiated block of text.

This is important for clinical documents because headings, sections, tables, and trial identifiers provide useful retrieval context.

---

## Multi-Agent Architecture

TrialLens uses LangGraph to orchestrate specialized agents.

### Agent Workflow

```text
                         User Question
                              │
                              ▼
                        Router Agent
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   Retriever Agent     Structured Agent     Safety Agent
          │                   │                   │
          ▼                   ▼                   ▼
   Clinical PDFs       ClinicalTrials.gov     openFDA FAERS
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                     Evidence Aggregator
                              │
                              ▼
                       Synthesis Agent
                              │
                              ▼
                     Critic / Verifier
                              │
                              ▼
                        Final Answer
```

### Router Agent

The Router Agent analyzes the question and determines which specialist capabilities are required.

For example:

```text
"What safety signals have been reported for avelumab
and what is the status of NCT02926196?"
```

can activate:

```text
Retriever Agent
+
Safety Agent
+
Structured Data Agent
```

### Retriever Agent

Responsible for retrieving relevant evidence from the indexed clinical document knowledge base.

It uses the existing retrieval service and returns candidate document chunks.

### Structured Data Agent

Responsible for direct ClinicalTrials.gov API access.

It supports:

- NCT identifier extraction
- Direct trial lookup
- Trial search
- Structured metadata parsing

### Safety Signal Agent

Responsible for querying openFDA FAERS.

It extracts:

- Drug name
- Number of records retrieved
- Serious-event count
- Reported reactions
- Report-level information

The agent explicitly distinguishes adverse-event reporting from causal inference.

### Evidence Aggregator

The Evidence Aggregator combines outputs from:

```text
Retriever Agent
Structured Data Agent
Safety Signal Agent
```

into a common evidence representation used by the synthesis stage.

### Synthesis Agent

The Synthesis Agent converts the aggregated evidence into a natural-language answer using the configured LLM.

The synthesis prompt enforces evidence-grounding requirements.

### Critic / Verification Agent

The Critic verifies the generated response after synthesis.

Current verification includes checks for:

- Unsupported numerical claims
- Missing evidence
- Evidence grounding

The final answer is returned together with its supporting sources.

---

## End-to-End Query Flow

A complete TrialLens request follows this sequence:

```text
1. User enters a clinical research question
                    │
                    ▼
2. Next.js sends POST /ask
                    │
                    ▼
3. FastAPI receives the request
                    │
                    ▼
4. LangGraph initializes TrialLens state
                    │
                    ▼
5. Router identifies required agents
                    │
                    ▼
6. Specialist agents retrieve evidence
                    │
                    ├── Clinical PDFs
                    ├── ClinicalTrials.gov
                    └── openFDA FAERS
                    │
                    ▼
7. Evidence Aggregator combines results
                    │
                    ▼
8. Prompt Builder constructs grounded prompt
                    │
                    ▼
9. Gemini generates draft answer
                    │
                    ▼
10. Critic / Verifier checks the answer
                    │
                    ▼
11. FastAPI returns:
                    │
                    ├── Answer
                    └── Sources
                    │
                    ▼
12. Next.js renders answer + evidence cards
```

---

## Example Multi-Agent Query

### Question

> What safety signals and adverse events have been reported for avelumab, and what is the current status of NCT02926196?

### Agent Routing

```text
Router
  │
  ├── Retriever Agent
  │
  ├── Safety Agent
  │
  └── Structured Data Agent
```

### Evidence Sources

```text
Clinical PDF
     +
ClinicalTrials.gov
     +
openFDA FAERS
```

### Result

TrialLens produces an evidence-grounded response describing:

- Clinical-trial safety findings
- Reported adverse events
- FAERS pharmacovigilance information
- Current ClinicalTrials.gov trial status

The interface displays the answer alongside the retrieved evidence sources.

### Example Output

> The A-BRAVE trial reported thyroid dysfunction as the most frequent immune-related adverse event associated with avelumab, including hypothyroidism and hyperthyroidism. Grade 3 immune-related toxicities included transaminase, lipase, and amylase increases and colitis.

ClinicalTrials.gov reports the overall status of NCT02926196 as:

```text
COMPLETED
```

FAERS reports are presented separately as pharmacovigilance evidence and are not treated as proof of drug causality.

> **Note:** the example output above reflects sample data from this project's own pipeline output, not an independently verified clinical claim. Anyone relying on trial-level safety data should confirm it against the primary source (e.g., the trial publication or ClinicalTrials.gov record).

---

## Frontend Architecture

TrialLens uses Next.js, React, TypeScript, and Tailwind CSS.

```text
                    Next.js Application
                           │
                           ▼
                     Research UI
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Question Input              Answer Display
                                         │
                                         ▼
                                  Evidence Sources
                                         │
                           ┌─────────────┼─────────────┐
                           │             │             │
                           ▼             ▼             ▼
                      Clinical PDF  ClinicalTrials  FAERS
```

The interface provides:

- Clinical research question input
- Example questions
- Loading states
- Error handling
- Evidence-grounded answer indicator
- Source cards
- Expandable evidence
- Trial IDs
- Source types
- Relevance scores where available

The frontend communicates with the FastAPI backend through:

```text
POST /ask
```

---

## Backend API

TrialLens exposes a FastAPI REST API.

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "TrialLens API is running",
  "architecture": "LangGraph multi-agent pipeline"
}
```

### Ask Question

```http
POST /ask
```

Example request:

```json
{
  "question": "What is the current status of NCT02926196?",
  "top_k": 5,
  "conversation_context": null
}
```

Example response structure:

```json
{
  "question": "What is the current status of NCT02926196?",
  "answer": "The overall status for Clinical Trial NCT02926196 is COMPLETED.",
  "sources": [
    {
      "document_id": "ClinicalTrials.gov",
      "trial_id": "NCT02926196",
      "source_type": "ClinicalTrials.gov",
      "section": "Structured Trial Metadata",
      "content": "Status: COMPLETED; Phase: ['PHASE3']; Enrollment: 474; Completion: 2025-10-09"
    }
  ]
}
```

---

## Evaluation

TrialLens includes a golden evaluation dataset containing 20 research questions.

The evaluation dataset is designed to test:

- Clinical fact retrieval
- Trial identifier retrieval
- Numerical values
- Source requirements
- Answer correctness
- Retrieval success

### Current Evaluation Results

```text
Questions evaluated:       20
Successful executions:     20/20
Answer accuracy:           80%
Required-source accuracy:  100%
```

> These figures are this project's own internal evaluation results on its own 20-question golden dataset, not benchmark numbers from an external or peer-reviewed source.

### Evaluation Checks

The current evaluator checks:

```text
Question
   │
   ▼
TrialLens
   │
   ▼
Generated Answer
   │
   ├── Expected clinical concepts
   ├── Expected numerical values
   ├── Required identifiers
   └── Required sources
   │
   ▼
Evaluation Result
```

### Known Evaluation Ambiguity

One evaluation question exposes an ambiguity in the underlying clinical document where the number of randomized patients differs from the ITT efficacy population.

The retrieval pipeline correctly retrieves the relevant evidence containing both values.

The evaluation wording should therefore distinguish between:

```text
Patients randomized
```

and

```text
Patients included in the ITT efficacy population
```

rather than modifying retrieval behavior to force a particular number.

### Future Evaluation

Planned improvements include:

- RAGAS
- DeepEval
- Context precision
- Context recall
- Faithfulness
- Answer relevance
- Larger golden datasets
- CI regression gating

---

## Verification and Safety Guardrails

TrialLens uses multiple mechanisms to reduce unsupported answers.

### Evidence Grounding

The synthesis prompt instructs the LLM to answer using retrieved evidence rather than unsupported outside knowledge.

### Numerical Verification

The Critic / Verification Agent extracts numerical claims from the generated answer and checks whether the values are present in the retrieved evidence.

This helps detect unsupported:

- Patient counts
- Percentages
- Hazard ratios
- Dates
- Other numerical claims

### Trial Identity Preservation

Trial identifiers such as:

```text
NCT02926196
```

are preserved throughout the retrieval and synthesis process.

This reduces the risk of accidentally combining evidence from unrelated trials.

### Source Separation

TrialLens distinguishes between:

```text
Clinical Trial Evidence
ClinicalTrials.gov Structured Data
openFDA FAERS Pharmacovigilance Data
```

This is particularly important for safety analysis.

### FAERS Causality Guardrail

FAERS reports are not treated as causal evidence.

The system explicitly communicates that:

```text
Reported adverse event
        ≠
Confirmed drug causality
```

### Medical Advice Guardrail

TrialLens is a research assistance system and is not designed to provide personalized medical advice or replace clinical expertise.

---

## Current Knowledge Base

The current MVP knowledge base contains:

```text
Clinical PDF documents:       7
Semantic chunks:              482

Embedding model:
BAAI/bge-small-en-v1.5

Vector database:
PostgreSQL + pgvector

Document parser:
Docling

Reranker:
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The current dataset is intentionally focused on the working MVP and demonstration pipeline rather than production-scale clinical coverage.

The system architecture is designed to support substantially larger document collections in future iterations.

---

## Technology Stack

**Frontend**
- Next.js
- React
- TypeScript
- Tailwind CSS

**Backend**
- Python
- FastAPI
- LangGraph

**Database**
- PostgreSQL
- pgvector

**Retrieval**
- Dense Embeddings — BAAI/bge-small-en-v1.5
- Keyword Retrieval
- Reciprocal Rank Fusion
- Cross-Encoder Reranking

**Document Processing**
- Docling
- PDF Parsing
- Document Structure Extraction
- Semantic Chunking

**LLM**
- Gemini

**External APIs**
- ClinicalTrials.gov API v2
- openFDA FAERS API

**Infrastructure**
- Docker
- Docker Compose
- PostgreSQL + pgvector

---

## Repository Structure

```text
TrialLens/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── state.py
│   │   │   ├── router_agent.py
│   │   │   ├── retriever_agent.py
│   │   │   ├── structured_agent.py
│   │   │   ├── safety_agent.py
│   │   │   ├── evidence_agent.py
│   │   │   ├── synthesis_agent.py
│   │   │   └── critic_agent.py
│   │   │
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   └── triallens_graph.py
│   │   │
│   │   ├── api/
│   │   │
│   │   ├── database/
│   │   │   └── vector_store.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── loader.py
│   │   │   ├── parser.py
│   │   │   └── chunker.py
│   │   │
│   │   ├── services/
│   │   │   ├── clinicaltrials_api.py
│   │   │   ├── faers_api.py
│   │   │   ├── embedding_service.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── reranker.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── llm_service.py
│   │   │   └── rag_pipeline.py
│   │   │
│   │   ├── models.py
│   │   ├── document_models.py
│   │   ├── chunk_models.py
│   │   ├── document_structure.py
│   │   ├── api_models.py
│   │   └── main.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── metadata/
│   │   └── sample_papers/
│   │
│   ├── evaluation/
│   │   └── golden_dataset.json
│   │
│   ├── scripts/
│   │
│   ├── tests/
│   │
│   └── test_langgraph.py
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## Local Setup

### Prerequisites

Install the following:

- Python 3.11+
- Node.js
- npm
- Docker Desktop
- Git

### 1. Clone the Repository

```bash
git clone <https://github.com/SanjanaChoudhury1508/TrialLens>
cd TrialLens
```

### 2. Backend Setup

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Database Setup

Start PostgreSQL + pgvector:

```powershell
docker compose up -d
```

Verify running containers:

```powershell
docker ps
```

### 4. Environment Variables

Create `backend/.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=triallens
DB_USER=postgres
DB_PASSWORD=postgres

GEMINI_API_KEY=<your-api-key>
```

Never commit API keys to Git.

### 5. Start Backend

```powershell
cd backend

python -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/
```

### 6. Start Frontend

Open another terminal:

```powershell
cd frontend

npm install

npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

## Testing

TrialLens contains tests for the major pipeline components.

### Backend Tests

Examples include:

```text
test_langgraph.py
test_structured_agent.py
test_safety_agent.py
```

Additional component-level tests cover:

- Vector search
- Retrieval
- Prompt construction
- LLM integration
- RAG pipeline behavior

### API Test

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"What is the current status of NCT02926196?"}'
```

### Frontend Build

Production build verification:

```powershell
cd frontend
npm run build
```

The current frontend production build completes successfully with TypeScript validation and static page generation.

---

## Demo

The current TrialLens MVP provides a working web interface for clinical research questions.

### Demo Query 1

```text
What were the coprimary endpoints of the A-BRAVE trial?
```

Expected result:

```text
The coprimary endpoints were:

1. Disease-free survival (DFS) in the intention-to-treat (ITT) population.
2. Disease-free survival (DFS) in the stratum B population.
```

### Demo Query 2

```text
What is the current status of NCT02926196?
```

Expected result:

```text
The A-BRAVE trial (NCT02926196) has an overall status of COMPLETED.
```

### Demo Query 3

```text
What safety signals and adverse events have been reported for
avelumab, and what is the current status of NCT02926196?
```

This query demonstrates the multi-agent architecture by combining:

```text
Retriever Agent
       +
Structured Data Agent
       +
Safety Signal Agent
       ↓
Evidence Aggregator
       ↓
Synthesis Agent
       ↓
Critic / Verifier
       ↓
Answer + Sources
```

The resulting interface displays:

- Evidence-grounded answer
- Clinical PDF sources
- ClinicalTrials.gov structured metadata
- openFDA FAERS evidence
- Trial identifiers
- Expandable evidence cards

---

## Development Roadmap

### Phase 0 — Repository & Infrastructure

- [x] Repository setup
- [x] Project structure
- [x] Development environment
- [x] Docker
- [x] PostgreSQL
- [x] pgvector
- [x] Initial documentation

### Phase 1 — Data Ingestion

- [x] ClinicalTrials.gov API integration
- [x] Clinical trial metadata extraction
- [x] Publication/document discovery
- [x] PDF ingestion
- [x] Docling parsing
- [x] Document structure extraction
- [x] Semantic chunking
- [x] Embedding generation
- [x] Vector database indexing

### Phase 2 — Retrieval

- [x] Dense vector retrieval
- [x] Keyword retrieval
- [x] Reciprocal Rank Fusion
- [x] Source/trial-aware scoring
- [x] Cross-encoder reranking
- [x] Retrieval service

**Future Retrieval Work**

- [ ] Advanced table extraction
- [ ] Dedicated Table QA
- [ ] Visual Document Retrieval
- [ ] ColPali-style retrieval
- [ ] Vision-language document understanding

### Phase 3 — Multi-Agent Orchestration

- [x] LangGraph integration
- [x] TrialLens state model
- [x] Router Agent
- [x] Retriever Agent
- [x] Structured Data Agent
- [x] Safety Signal Agent
- [x] Evidence Aggregator
- [x] Synthesis Agent
- [x] Critic / Verification Agent
- [x] FastAPI integration
- [x] Next.js frontend integration

### Phase 4 — Evaluation

- [x] Golden dataset
- [x] Automated evaluation
- [x] Answer accuracy evaluation
- [x] Required-source evaluation
- [x] Numerical claim checking

**Future Evaluation Work**

- [ ] RAGAS
- [ ] DeepEval
- [ ] Context precision
- [ ] Context recall
- [ ] Faithfulness scoring
- [ ] Answer relevance
- [ ] CI regression gating
- [ ] Larger evaluation dataset

### Phase 5 — Observability & Deployment

- [ ] Langfuse integration
- [ ] Arize Phoenix integration
- [ ] Token usage tracking
- [ ] Cost tracking
- [ ] Latency monitoring
- [ ] p95 dashboards
- [ ] Production deployment
- [ ] CI/CD pipeline

### Phase 6 — Multimodal Clinical Intelligence

- [ ] Advanced table understanding
- [ ] Figure understanding
- [ ] Visual Document Retrieval
- [ ] Protocol-level reasoning
- [ ] SAP analysis
- [ ] Cross-trial comparison
- [ ] Advanced safety signal classification

---

## Future Architecture

The planned long-term architecture expands the current MVP into a multimodal clinical research system.

```text
                              User
                                │
                                ▼
                         Next.js Frontend
                                │
                                ▼
                         FastAPI Backend
                                │
                                ▼
                       LangGraph Orchestrator
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
 Retriever Agent        Structured Agent          Safety Agent
        │                       │                        │
        ▼                       ▼                        ▼
 Hybrid Retrieval       ClinicalTrials.gov         openFDA FAERS
        │                       │                        │
        ▼                       │                        │
 PostgreSQL + pgvector          │                        │
        │                       │                        │
        ▼                       │                        │
 Clinical Documents             │                        │
        │                       │                        │
   ┌────┴────┐                  │                        │
   │         │                  │                        │
   ▼         ▼                  │                        │
 Tables    Figures              │                        │
   │         │                  │                        │
   ▼         ▼                  │                        │
Table QA   Visual Retrieval     │                        │
           / VLM                │                        │
   │         │                  │                        │
   └────┬────┘                  │                        │
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                ▼
                       Evidence Aggregator
                                │
                                ▼
                         Critic / Verifier
                                │
                                ▼
                         Final Synthesis
                                │
                                ▼
                     Citation-Grounded Answer
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
        Langfuse / Phoenix                    Evaluation
              │                                   │
              ▼                                   ▼
      Cost / Latency Metrics              RAGAS / DeepEval
```

The future architecture will extend TrialLens beyond text-based retrieval toward multimodal clinical document understanding.

---

## Limitations

TrialLens is currently a research prototype / MVP.

It should not be used as a substitute for:

- Clinical expertise
- Medical advice
- Regulatory review
- Professional pharmacovigilance analysis
- Clinical decision-making

Current limitations include:

- Limited indexed document coverage
- Limited FAERS query sophistication
- No formal causal inference from FAERS
- No dedicated visual document retrieval model
- No dedicated Table QA model
- No production-scale evaluation
- No production observability platform
- No CI regression gating
- No production deployment
- Retrieval quality depends on indexed evidence
- External APIs require network access
- LLM output depends on the configured model and API availability

TrialLens is intended to assist research workflows, not replace expert judgment.

---

## Design Principles

**Evidence First** — TrialLens prioritizes retrieved evidence over unsupported general knowledge.

**Source Separation** — Structured API data, clinical documents, and pharmacovigilance reports are treated as distinct evidence sources.

**Trial Identity Preservation** — NCT identifiers are preserved throughout retrieval, evidence aggregation, and synthesis.

**Verification Before Presentation** — Generated responses pass through a critic / verification stage before being returned to the user.

**Numerical Accuracy** — Numerical claims are treated as high-value evidence and are checked against retrieved sources.

**Transparent Uncertainty** — When evidence is insufficient, the system should avoid presenting unsupported conclusions.

**Research, Not Medical Advice** — TrialLens is designed as a clinical research assistant and not as a medical decision-making system.

---

## Future Vision

TrialLens is designed to evolve from a document retrieval assistant into a multimodal clinical research copilot.

The long-term workflow is:

```text
ClinicalTrials.gov
        │
        ├──────────────┐
        │              │
        ▼              ▼
 Structured Data    Trial Documents
                       │
                       ▼
                Protocols / SAPs
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
           Tables             Figures
             │                   │
             ▼                   ▼
         Table QA          Visual Retrieval
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                  Hybrid RAG
                       │
                       ▼
                Multi-Agent AI
                       │
                       ▼
                Evidence Critic
                       │
                       ▼
              Verified Synthesis
                       │
                       ▼
             Citation-Grounded Answer
```

Potential future capabilities include:

- Protocol question answering
- Statistical Analysis Plan analysis
- Table-aware clinical reasoning
- Figure and chart understanding
- Cross-trial comparison
- Safety signal classification
- Evidence grading
- Longitudinal trial monitoring
- Automated research workflows
- Research trace visualization
- Cost and latency monitoring

---

## Current Project Status

### 🟢 Working MVP

**Data**
- [x] ClinicalTrials.gov API v2
- [x] Clinical trial metadata extraction
- [x] Clinical document discovery
- [x] Clinical PDF knowledge base
- [x] openFDA FAERS integration

**RAG**
- [x] PDF ingestion
- [x] Docling parsing
- [x] Semantic chunking
- [x] BAAI/bge-small-en-v1.5 embeddings
- [x] PostgreSQL + pgvector
- [x] Dense retrieval
- [x] Keyword retrieval
- [x] Reciprocal Rank Fusion
- [x] Cross-encoder reranking
- [x] Evidence aggregation
- [x] Gemini synthesis

**Multi-Agent System**
- [x] LangGraph
- [x] Router Agent
- [x] Retriever Agent
- [x] Structured Data Agent
- [x] Safety Signal Agent
- [x] Evidence Aggregator
- [x] Synthesis Agent
- [x] Critic / Verification Agent

**Application**
- [x] FastAPI REST API
- [x] Next.js frontend
- [x] Evidence source display
- [x] Expandable evidence cards
- [x] End-to-end question answering

**Evaluation**
- [x] 20-question golden dataset
- [x] Automated evaluation
- [x] 20/20 successful executions
- [x] 80% answer accuracy
- [x] 100% required-source accuracy

**Verification**
- [x] Backend API tested
- [x] Multi-agent query tested
- [x] Structured trial query tested
- [x] Safety query tested
- [x] Frontend tested
- [x] Production frontend build verified

---

## Implementation Status

TrialLens contains both implemented MVP components and planned research extensions.

### Implemented

- ClinicalTrials.gov structured data integration
- openFDA FAERS integration
- Clinical PDF ingestion
- Docling document parsing
- Semantic chunking
- Embedding generation
- PostgreSQL + pgvector
- Dense retrieval
- Keyword retrieval
- Reciprocal Rank Fusion
- Cross-encoder reranking
- LangGraph orchestration
- Specialized agents
- Evidence aggregation
- Gemini synthesis
- Critic / verification
- FastAPI API
- Next.js frontend
- Golden dataset evaluation

### Planned

The following are architectural extensions and are not currently part of the MVP implementation:

- ColPali / advanced visual document retrieval
- Qwen2-VL-style document reasoning
- Dedicated Table QA model
- RAGAS
- DeepEval
- Langfuse
- Arize Phoenix
- CI regression gating
- Production deployment
- Advanced multimodal reasoning

---

## License

This project is licensed under the MIT License.
