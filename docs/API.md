# API Design

## Purpose

This document describes the REST API exposed by the TrialLens backend.

---

## Planned Endpoints

### Trial Search

```
GET /trials/search
```

Search clinical trials.

---

### Trial Details

```
GET /trials/{trial_id}
```

Retrieve complete trial metadata.

---

### Upload Documents

```
POST /documents/upload
```

Upload protocol PDFs.

---

### Ask Questions

```
POST /ask
```

Query the TrialLens system.

---

### Health Check

```
GET /
```

Verify backend status.

---

## Status

API endpoints will be implemented incrementally during development.