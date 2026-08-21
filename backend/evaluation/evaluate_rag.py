import json
import sys
from pathlib import Path

# Allow imports from backend/app when running:
# python evaluation/evaluate_rag.py
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.rag_pipeline import RAGPipeline


DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def normalize(text: str) -> str:
    """Normalize text for simple keyword/concept matching."""

    return (
        text.lower()
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace(",", " ")
        .replace(".", " ")
    )


def check_expected_answer(
    answer: str,
    expected_answer: str,
) -> bool:

    answer_normalized = normalize(answer)
    expected_normalized = normalize(expected_answer)

    # Extract important concepts rather than requiring
    # an exact sentence match.

    concepts = []

    important_terms = [
        "disease free survival",
        "overall survival",
        "avelumab",
        "observation",
        "intention to treat",
        "stratum b",
        "residual disease",
        "neoadjuvant chemotherapy",
        "0.66",
        "did not significantly improve",
    ]

    for term in important_terms:

        if term in expected_normalized:
            concepts.append(term)

    if not concepts:
        return False

    matched = sum(
        term in answer_normalized
        for term in concepts
    )

    # Require most important concepts to be present.
    return matched / len(concepts) >= 0.6


def check_source(
    result,
    required_source: str,
) -> bool:

    sources = result.get("sources", [])

    source_text = str(sources)

    return required_source.lower() in source_text.lower()


def evaluate_question(
    pipeline: RAGPipeline,
    item: dict,
):

    question = item["question"]
    expected_answer = item["expected_answer"]
    required_source = item["required_source"]

    print("=" * 70)
    print(f"Question: {question}")
    print("=" * 70)

    result = pipeline.ask(
        question,
        top_k=5,
    )

    answer = result.get(
        "answer",
        "",
    )

    answer_correct = check_expected_answer(
        answer,
        expected_answer,
    )

    source_correct = check_source(
        result,
        required_source,
    )

    print("\nGenerated Answer:")
    print(answer)

    print("\nExpected:")
    print(expected_answer)

    print("\nSources:")
    print(result.get("sources"))

    print(
        f"\nAnswer Match : "
        f"{'✓' if answer_correct else '✗'}"
    )

    print(
        f"Source Match : "
        f"{'✓' if source_correct else '✗'}"
    )

    return {
        "id": item["id"],
        "question": question,
        "answer_correct": answer_correct,
        "source_correct": source_correct,
        "answer": answer,
        "sources": result.get("sources", []),
    }


def main():

    print("=" * 70)
    print("TRIALLENS RAG EVALUATION")
    print("=" * 70)

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        dataset = json.load(f)

    print(
        f"\nLoaded {len(dataset)} evaluation questions."
    )

    pipeline = RAGPipeline()

    results = []

    for item in dataset:

        result = evaluate_question(
            pipeline,
            item,
        )

        results.append(result)

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    total = len(results)

    answer_passed = sum(
        result["answer_correct"]
        for result in results
    )

    source_passed = sum(
        result["source_correct"]
        for result in results
    )

    answer_accuracy = (
        answer_passed / total
        if total
        else 0
    )

    source_accuracy = (
        source_passed / total
        if total
        else 0
    )

    print("\n")
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Questions Tested : {total}"
    )

    print(
        f"Answer Accuracy   : "
        f"{answer_accuracy:.2%}"
    )

    print(
        f"Source Accuracy   : "
        f"{source_accuracy:.2%}"
    )

    print(
        f"Answer Passed     : "
        f"{answer_passed}/{total}"
    )

    print(
        f"Source Passed     : "
        f"{source_passed}/{total}"
    )

    # Save detailed results
    output_path = (
        Path(__file__).parent
        / "evaluation_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nDetailed results saved to:"
    )

    print(output_path)


if __name__ == "__main__":
    main()