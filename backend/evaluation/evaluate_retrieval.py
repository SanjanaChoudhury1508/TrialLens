import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.retrieval_service import RetrievalService


DATASET_PATH = (
    Path(__file__).parent / "golden_dataset.json"
)


def normalize(text: str) -> str:
    return (
        text.lower()
        .replace("-", " ")
        .replace("/", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace(",", " ")
        .replace(".", " ")
    )


def keyword_match(result, keywords):
    content = normalize(
        result.get("content", "")
    )

    matched = 0

    for keyword in keywords:

        if normalize(keyword) in content:
            matched += 1

    if not keywords:
        return 0.0

    return matched / len(keywords)


def evaluate_question(
    retriever,
    item,
    top_k=5,
):

    question = item["question"]
    required_source = item["required_source"]
    keywords = item.get(
        "expected_keywords",
        [],
    )

    results = retriever.retrieve(
        question,
        top_k=top_k,
    )

    # -------------------------------------------------
    # Source Recall@K
    # -------------------------------------------------

    source_rank = None

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if (
            result.get("trial_id")
            == required_source
            or result.get("document_id")
            == required_source
        ):

            source_rank = rank
            break

    recall_at_k = (
        1 if source_rank is not None else 0
    )

    # -------------------------------------------------
    # MRR
    # -------------------------------------------------

    reciprocal_rank = (
        1 / source_rank
        if source_rank is not None
        else 0
    )

    # -------------------------------------------------
    # Keyword coverage
    # -------------------------------------------------

    combined_content = " ".join(
        result.get("content", "")
        for result in results
    )
    
    combined_content = normalize(
        combined_content
    )
    
    matched = 0
    
    for keyword in keywords:
    
        if normalize(keyword) in combined_content:
            matched += 1
    
    keyword_coverage = (
        matched / len(keywords)
        if keywords
        else 0.0
    )

    return {
        "id": item["id"],
        "question": question,
        "source_rank": source_rank,
        "recall_at_5": recall_at_k,
        "reciprocal_rank": reciprocal_rank,
        "keyword_coverage": keyword_coverage,
    }


def main():

    print("=" * 70)
    print("TRIALLENS RETRIEVAL EVALUATION")
    print("=" * 70)

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        dataset = json.load(f)

    print(
        f"\nLoaded {len(dataset)} questions."
    )

    retriever = RetrievalService()

    results = []

    for item in dataset:

        print("\n" + "-" * 70)
        print(item["question"])

        result = evaluate_question(
            retriever,
            item,
        )

        results.append(result)

        print(
            f"Source Rank     : "
            f"{result['source_rank']}"
        )

        print(
            f"Recall@5        : "
            f"{result['recall_at_5']}"
        )

        print(
            f"Reciprocal Rank : "
            f"{result['reciprocal_rank']:.3f}"
        )

        print(
            f"Keyword Coverage: "
            f"{result['keyword_coverage']:.2%}"
        )

    # -------------------------------------------------
    # Aggregate metrics
    # -------------------------------------------------

    total = len(results)

    recall_at_5 = (
        sum(
            r["recall_at_5"]
            for r in results
        ) / total
        if total
        else 0
    )

    mrr = (
        sum(
            r["reciprocal_rank"]
            for r in results
        ) / total
        if total
        else 0
    )

    keyword_coverage = (
        sum(
            r["keyword_coverage"]
            for r in results
        ) / total
        if total
        else 0
    )

    print("\n")
    print("=" * 70)
    print("RETRIEVAL EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Questions Tested : {total}"
    )

    print(
        f"Recall@5         : {recall_at_5:.2%}"
    )

    print(
        f"MRR              : {mrr:.3f}"
    )

    print(
        f"Keyword Coverage : "
        f"{keyword_coverage:.2%}"
    )

    output_path = (
        Path(__file__).parent
        / "retrieval_results.json"
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
        )

    print(
        f"\nResults saved to:"
    )

    print(output_path)


if __name__ == "__main__":
    main()