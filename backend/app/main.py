from fastapi import FastAPI

app = FastAPI(title="TrialLens API")


@app.get("/")
def root():
    return {"message": "TrialLens API is running"}