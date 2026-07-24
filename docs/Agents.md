# Multi-Agent Design

## Overview

TrialLens will use LangGraph to coordinate multiple specialized AI agents.

Each agent will have a single responsibility.

---

## Planned Agents

### Retriever Agent

Responsible for retrieving relevant documents using Hybrid RAG.

---

### Structured Data Agent

Queries structured APIs such as ClinicalTrials.gov and openFDA.

---

### Safety Signal Agent

Analyzes adverse event information.

---

### Critic Agent

Verifies generated responses before they are returned.

---

## Status

Agent implementation will begin after the retrieval pipeline is completed.