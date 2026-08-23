from fastapi import FastAPI, HTTPException

from app.api_models import AskRequest, AskResponse
from app.services.rag_pipeline import RAGPipeline


app = FastAPI(
    title="TrialLens API",
    version="0.1.0",
    description="Backend API for TrialLens",
)


rag_pipeline = RAGPipeline()


@app.get("/")
def root():
    return {
        "message": "TrialLens API is running"
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = rag_pipeline.ask(
            request.question,
            top_k=request.top_k,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG pipeline failed: {str(e)}",
        )