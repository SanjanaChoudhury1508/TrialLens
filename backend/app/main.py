from fastapi import FastAPI

app = FastAPI(
    title="TrialLens API",
    version="0.1.0",
    description="Backend API for TrialLens"
)

@app.get("/")
def root():
    return {
        "message": "TrialLens API is running"
    }