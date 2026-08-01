import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.llm_service import LLMService

llm = LLMService()

response = llm.generate(
    "Explain what a Phase III clinical trial is in two sentences."
)

print(response)