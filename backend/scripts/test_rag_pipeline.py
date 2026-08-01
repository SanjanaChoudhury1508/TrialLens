import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.rag_pipeline import RAGPipeline

rag = RAGPipeline()

response = rag.ask(
    "What breast cancer immunotherapy trials are available?"
)

print("\nAnswer\n")
print(response["answer"])

print("\nSources\n")

for source in response["sources"]:
    print(source)