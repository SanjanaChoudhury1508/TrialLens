import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.retrieval_service import RetrievalService
from app.services.prompt_builder import PromptBuilder

retriever = RetrievalService()

question = "breast cancer immunotherapy"

chunks = retriever.retrieve(question)

prompt = PromptBuilder.build(question, chunks)

print(prompt)