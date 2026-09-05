from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api_models import AskRequest, AskResponse
from app.graph.triallens_graph import trial_lens_graph


app = FastAPI(
    title="TrialLens API",
    version="0.2.0",
    description="Multi-Agent Clinical Trial Intelligence Copilot API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_sources(result):
    """Convert graph evidence into API Source objects."""

    sources = []

    for item in result.get("evidence", []):

        source_type = item.get(
            "source_type",
            item.get("source", "Unknown"),
        )

        # Structured ClinicalTrials.gov evidence
        if source_type == "structured":

            data = item.get("data", {})

            sources.append({
                "document_id": "ClinicalTrials.gov",
                "trial_id": data.get("nct_id"),
                "source_type": "ClinicalTrials.gov",
                "section": "Structured Trial Metadata",
                "content": (
                    f"Status: {data.get('overall_status')}; "
                    f"Phase: {data.get('phase')}; "
                    f"Enrollment: {data.get('enrollment')}; "
                    f"Completion: {data.get('completion_date')}"
                ),
                "relevance_score": None,
            })

            continue

        # FAERS evidence
        if source_type == "safety":

            sources.append({
                "document_id": "openFDA FAERS",
                "trial_id": None,
                "source_type": "openFDA FAERS",
                "section": "Adverse Event Reports",
                "content": (
                    f"Drug: {item.get('drug')}; "
                    f"Records retrieved: "
                    f"{item.get('records_retrieved')}; "
                    f"Serious records: "
                    f"{item.get('serious_events')}; "
                    f"Top reactions: "
                    f"{item.get('top_reactions')}"
                ),
                "relevance_score": None,
            })

            continue

        # PDF / RAG evidence
        sources.append({
            "document_id": item.get(
                "document_id",
                "Unknown",
            ),
            "trial_id": item.get("trial_id"),
            "source_type": item.get(
                "source_type",
                "Unknown",
            ),
            "section": item.get("section"),
            "content": item.get("content"),
            "relevance_score": item.get(
                "relevance_score"
            ),
        })

    return sources


@app.get("/")
def root():

    return {
        "message": "TrialLens API is running",
        "architecture": "LangGraph multi-agent pipeline",
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        result = trial_lens_graph.invoke(
            {
                "question": request.question,
                "conversation_context": (
                    request.conversation_context
                ),
            }
        )

        answer = result.get(
            "final_answer",
            result.get("draft_answer", ""),
        )

        return AskResponse(
            question=request.question,
            answer=answer,
            sources=build_sources(result),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"TrialLens pipeline failed: {str(e)}",
        )