import argparse
import json
import re
import sys
import time
from pathlib import Path

# Allow imports from backend/app when running:
# python evaluation/evaluate_rag.py
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.rag_pipeline import RAGPipeline


DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "evaluation_results.json"


# =========================================================
# GEMINI RATE-LIMIT SETTINGS
# =========================================================

REQUEST_DELAY_SECONDS = 15
RATE_LIMIT_RETRY_SECONDS = 30
MAX_RETRIES = 3


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize(text: str) -> str:
    """
    Normalize text for robust keyword/concept matching.
    """

    if not text:
        return ""

    text = text.lower()

    # Normalize common variants.
    replacements = {
        "intention-to-treat": "intention to treat",
        "intention–to–treat": "intention to treat",
        "intention— to—treat": "intention to treat",
        "disease-free": "disease free",
        "triple-negative": "triple negative",
        "high-risk": "high risk",
        "one-year": "one year",
        "pd-l1": "pd l1",
        "pd–l1": "pd l1",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Replace punctuation with spaces.
    text = re.sub(r"[^a-z0-9.%]+", " ", text)

    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================================================
# KEYWORD ALIASES
# =========================================================

KEYWORD_ALIASES = {
    "disease-free survival": [
        "disease free survival",
        "dfs",
    ],

    "intention-to-treat": [
        "intention to treat",
        "intention-to-treat",
        "itt population",
        "itt",
    ],

    "stratum b": [
        "stratum b",
    ],

    "avelumab": [
        "avelumab",
    ],

    "observation": [
        "observation",
        "control",
    ],

    "one year": [
        "one year",
        "1 year",
        "12 months",
        "twelve months",
    ],

    "invasive residual disease": [
        "invasive residual disease",
        "residual invasive disease",
    ],

    "breast": [
        "breast",
    ],

    "nodes": [
        "nodes",
        "lymph nodes",
        "lymph node",
    ],

    "neoadjuvant chemotherapy": [
        "neoadjuvant chemotherapy",
        "neoadjuvant treatment",
        "neoadjuvant therapy",
    ],

    "did not": [
        "did not",
        "didn't",
        "didnt",
        "no",
        "not",
    ],

    "significantly improve": [
        "significantly improve",
        "significantly improved",
        "significant improvement",
    ],

    "overall survival": [
        "overall survival",
        "os",
    ],

    "hazard ratio": [
        "hazard ratio",
        "hazard ratios",
        "hr",
    ],

    "phase iii": [
        "phase iii",
        "phase 3",
    ],

    "randomized": [
        "randomized",
        "randomised",
        "randomly assigned",
    ],

    "466": [
        "466",
    ],

    "0.66": [
        "0.66",
    ],

    "0.81": [
        "0.81",
    ],

    "0.80": [
        "0.80",
        "0.8",
    ],

    "pd l1": [
        "pd l1",
        "pd-l1",
        "pdl1",
    ],

    "cancer immunotherapy": [
        "cancer immunotherapy",
        "cancer immunotherapies",
        "immunotherapy for cancer",
    ],

    "checkpoint immunotherapy": [
        "checkpoint immunotherapy",
        "immune checkpoint immunotherapy",
        "checkpoint inhibitors",
        "immune checkpoint inhibitors",
        "checkpoint therapy",
    ],

    "pitfalls": [
        "pitfalls",
        "pitfall",
    ],

    "limitations": [
        "limitations",
        "limitation",
    ],

    "personalized cancer vaccines": [
        "personalized cancer vaccines",
        "personalised cancer vaccines",
        "personalized cancer vaccine",
        "personalised cancer vaccine",
    ],

    "microbiome": [
        "microbiome",
    ],

    "tumour microenvironment": [
        "tumour microenvironment",
        "tumor microenvironment",
    ],

    "metabolomics": [
        "metabolomics",
    ],

    "statistical analysis": [
        "statistical analysis",
        "statistical analyses",
        "statistical analysis plan",
        "statistical planning",
    ],

    "clinical trial": [
        "clinical trial",
        "clinical trials",
    ],

    "immunotherapy": [
        "immunotherapy",
        "immunotherapies",
    ],

    "toxicity": [
        "toxicity",
        "toxicities",
        "toxic effects",
    ],

    "triple-negative breast cancer": [
        "triple negative breast cancer",
        "triple-negative breast cancer",
        "tnbc",
    ],

    "high-risk": [
        "high risk",
        "high-risk",
    ],

    "early": [
        "early",
        "early stage",
    ],

    "did not improve": [
        "did not improve",
        "didn't improve",
        "didnt improve",
        "failed to improve",
        "no improvement",
    ],

    "potential favorable impact": [
        "potential favorable impact",
        "potentially favorable impact",
        "potential benefit",
        "favorable impact",
        "favourable impact",
    ],
}


def get_keyword_variants(keyword: str):
    """
    Return normalized variants for a golden-dataset keyword.
    """

    normalized_keyword = normalize(keyword)

    if normalized_keyword in KEYWORD_ALIASES:
        return [
            normalize(value)
            for value in KEYWORD_ALIASES[normalized_keyword]
        ]

    return [normalized_keyword]


# =========================================================
# KEYWORD MATCHING
# =========================================================

def keyword_matches(answer: str, keyword: str) -> bool:
    """
    Check whether a golden keyword or one of its known
    equivalent forms appears in the generated answer.
    """

    answer_normalized = normalize(answer)

    variants = get_keyword_variants(keyword)

    return any(
        variant and variant in answer_normalized
        for variant in variants
    )


def evaluate_keywords(answer: str, expected_keywords):
    """
    Evaluate every expected keyword independently.

    Returns:
        matched_keywords
        missing_keywords
        coverage
    """

    matched_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        if keyword_matches(answer, keyword):
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    total = len(expected_keywords)

    coverage = (
        len(matched_keywords) / total
        if total
        else 0.0
    )

    return (
        matched_keywords,
        missing_keywords,
        coverage,
    )


# =========================================================
# EXPECTED ANSWER SUPPORT
# =========================================================

def extract_important_numbers(text: str):
    """
    Extract numeric values that may represent important
    clinical/statistical facts.

    Examples:
        466
        0.81
        0.66
        12.5
    """

    if not text:
        return []

    return re.findall(
        r"(?<!\w)(?:\d+(?:\.\d+)?)(?!\w)",
        text,
    )


def check_expected_numbers(
    answer: str,
    expected_answer: str,
):
    """
    Check whether important numbers in the expected answer
    appear in the generated answer.

    This prevents cases such as:
        expected = 466
        generated = 477
    from being incorrectly marked correct.
    """

    expected_numbers = extract_important_numbers(expected_answer)
    answer_numbers = extract_important_numbers(answer)

    if not expected_numbers:
        return True, [], []

    matched = []
    missing = []

    for number in expected_numbers:
        if number in answer_numbers:
            matched.append(number)
        else:
            missing.append(number)

    return (
        len(missing) == 0,
        matched,
        missing,
    )


# =========================================================
# ANSWER EVALUATION
# =========================================================

def check_expected_answer(
    answer: str,
    expected_answer: str,
    expected_keywords=None,
):
    """
    Evaluate the generated answer against the golden dataset.

    Primary evaluation:
        - expected_keywords
        - important numeric facts

    The expected answer is retained as explanatory context,
    but exact string matching is intentionally avoided.
    """

    if not answer:
        return {
            "correct": False,
            "keyword_coverage": 0.0,
            "matched_keywords": [],
            "missing_keywords": expected_keywords or [],
            "numbers_correct": False,
            "matched_numbers": [],
            "missing_numbers": extract_important_numbers(
                expected_answer
            ),
        }

    expected_keywords = expected_keywords or []

    (
        matched_keywords,
        missing_keywords,
        keyword_coverage,
    ) = evaluate_keywords(
        answer,
        expected_keywords,
    )

    (
        numbers_correct,
        matched_numbers,
        missing_numbers,
    ) = check_expected_numbers(
        answer,
        expected_answer,
    )

    # -----------------------------------------------------
    # Correctness rule
    # -----------------------------------------------------
    #
    # All expected keywords should normally be present.
    #
    # For questions with several keywords, we allow 80%
    # coverage to tolerate natural wording differences.
    #
    # However, ALL important numeric facts must match.
    #

    if expected_keywords:
        keyword_correct = keyword_coverage >= 0.80
    else:
        keyword_correct = True

    correct = keyword_correct and numbers_correct

    return {
        "correct": correct,
        "keyword_coverage": keyword_coverage,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "numbers_correct": numbers_correct,
        "matched_numbers": matched_numbers,
        "missing_numbers": missing_numbers,
    }


# =========================================================
# SOURCE EVALUATION
# =========================================================

def check_source(
    result,
    required_source: str,
) -> bool:
    """
    Check whether the required source appears
    in the retrieved sources.
    """

    sources = result.get("sources", [])

    source_text = str(sources)

    return required_source.lower() in source_text.lower()


# =========================================================
# GEMINI ERROR DETECTION
# =========================================================

def is_retryable_error(error_text: str) -> bool:
    """
    Determine whether an error is likely temporary.
    """

    error_lower = error_text.lower()

    retryable_terms = [
        "429",
        "resource_exhausted",
        "quota",
        "503",
        "unavailable",
    ]

    return any(
        term in error_lower
        for term in retryable_terms
    )


# =========================================================
# EVALUATE EXISTING RESULT
# =========================================================

def evaluate_existing_result(
    item: dict,
    result: dict,
):
    """
    Evaluate an already-generated RAG result.

    IMPORTANT:
    This function does NOT call Gemini.
    """

    answer = result.get("answer", "")

    expected_answer = item["expected_answer"]

    expected_keywords = item.get(
        "expected_keywords",
        [],
    )

    required_source = item["required_source"]

    evaluation = check_expected_answer(
        answer=answer,
        expected_answer=expected_answer,
        expected_keywords=expected_keywords,
    )

    source_correct = check_source(
        result,
        required_source,
    )

    print("=" * 70)
    print(f"{item['id']}: {item['question']}")
    print("=" * 70)

    print("\nGenerated Answer:")
    print(answer)

    print("\nExpected Answer:")
    print(expected_answer)

    print("\nExpected Keywords:")
    print(expected_keywords)

    print("\nMatched Keywords:")
    print(evaluation["matched_keywords"])

    print("\nMissing Keywords:")
    print(evaluation["missing_keywords"])

    print(
        f"\nKeyword Coverage: "
        f"{evaluation['keyword_coverage']:.2%}"
    )

    print("\nMatched Numbers:")
    print(evaluation["matched_numbers"])

    print("\nMissing Numbers:")
    print(evaluation["missing_numbers"])

    print(
        f"\nAnswer Match : "
        f"{'✓' if evaluation['correct'] else '✗'}"
    )

    print(
        f"Source Match : "
        f"{'✓' if source_correct else '✗'}"
    )

    return {
        "id": item["id"],
        "question": item["question"],
        "answer_correct": evaluation["correct"],
        "source_correct": source_correct,
        "answer": answer,
        "sources": result.get("sources", []),

        # Evaluation diagnostics
        "expected_keywords": expected_keywords,
        "matched_keywords": evaluation[
            "matched_keywords"
        ],
        "missing_keywords": evaluation[
            "missing_keywords"
        ],
        "keyword_coverage": evaluation[
            "keyword_coverage"
        ],
        "expected_numbers": extract_important_numbers(
            expected_answer
        ),
        "matched_numbers": evaluation[
            "matched_numbers"
        ],
        "missing_numbers": evaluation[
            "missing_numbers"
        ],
    }


# =========================================================
# FRESH GEMINI EVALUATION
# =========================================================

def evaluate_question(
    pipeline: RAGPipeline,
    item: dict,
):
    """
    Run one question through the complete RAG pipeline.

    API failures are recorded separately.
    """

    question = item["question"]

    print("=" * 70)
    print(f"Question: {question}")
    print("=" * 70)

    result = None
    error_text = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            result = pipeline.ask(
                question,
                top_k=5,
            )

            break

        except Exception as e:

            error_text = str(e)

            if is_retryable_error(error_text):

                print(
                    "\n⚠ Temporary Gemini error."
                )

                print(
                    f"Attempt "
                    f"{attempt}/{MAX_RETRIES}"
                )

                if attempt < MAX_RETRIES:

                    print(
                        f"Waiting "
                        f"{RATE_LIMIT_RETRY_SECONDS}s "
                        f"before retry..."
                    )

                    time.sleep(
                        RATE_LIMIT_RETRY_SECONDS
                    )

                    continue

            print(
                "\n✗ Gemini/API error:"
            )

            print(error_text)

            return {
                "id": item["id"],
                "question": question,
                "answer_correct": False,
                "source_correct": False,
                "answer": "",
                "sources": [],
                "error": error_text,
            }

    if result is None:

        return {
            "id": item["id"],
            "question": question,
            "answer_correct": False,
            "source_correct": False,
            "answer": "",
            "sources": [],
            "error": (
                error_text
                or
                "Gemini request failed"
            ),
        }

    expected_answer = item["expected_answer"]

    expected_keywords = item.get(
        "expected_keywords",
        [],
    )

    evaluation = check_expected_answer(
        answer=result.get("answer", ""),
        expected_answer=expected_answer,
        expected_keywords=expected_keywords,
    )

    source_correct = check_source(
        result,
        item["required_source"],
    )

    return {
        "id": item["id"],
        "question": question,
        "answer_correct": evaluation["correct"],
        "source_correct": source_correct,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),

        "expected_keywords": expected_keywords,
        "matched_keywords": evaluation[
            "matched_keywords"
        ],
        "missing_keywords": evaluation[
            "missing_keywords"
        ],
        "keyword_coverage": evaluation[
            "keyword_coverage"
        ],
        "expected_numbers": extract_important_numbers(
            expected_answer
        ),
        "matched_numbers": evaluation[
            "matched_numbers"
        ],
        "missing_numbers": evaluation[
            "missing_numbers"
        ],
    }


# =========================================================
# LOAD EXISTING RESULTS
# =========================================================

def load_existing_results():
    """
    Load the previously generated evaluation results.

    This is completely offline and does not call Gemini.
    """

    if not RESULTS_PATH.exists():
        return None

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TrialLens RAG evaluation"
        )
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Run Gemini again for all questions. "
            "Without this flag, existing "
            "evaluation_results.json is reused."
        ),
    )

    args = parser.parse_args()

    print("=" * 70)
    print("TRIALLENS RAG EVALUATION")
    print("=" * 70)

    # -----------------------------------------------------
    # LOAD GOLDEN DATASET
    # -----------------------------------------------------

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        dataset = json.load(f)

    total_questions = len(dataset)

    print(
        f"\nLoaded "
        f"{total_questions} evaluation questions."
    )

    # =====================================================
    # OFFLINE MODE
    # =====================================================

    if not args.fresh:

        existing_results = load_existing_results()

        if existing_results is None:

            print(
                "\nNo existing evaluation_results.json found."
            )

            print(
                "\nRun with --fresh to generate "
                "new Gemini responses."
            )

            return

        print(
            "\nOFFLINE EVALUATION MODE"
        )

        print(
            "Using existing RAG responses."
        )

        print(
            "No Gemini requests will be made."
        )

        print(
            "This saves Gemini quota."
        )

        # Map results by question ID.
        result_map = {
            result["id"]: result
            for result in existing_results
        }

        results = []

        for item in dataset:

            old_result = result_map.get(
                item["id"]
            )

            if old_result is None:

                print(
                    f"\n⚠ Missing result for "
                    f"{item['id']}"
                )

                results.append({
                    "id": item["id"],
                    "question": item["question"],
                    "answer_correct": False,
                    "source_correct": False,
                    "answer": "",
                    "sources": [],
                    "error": (
                        "No previous result "
                        "found for this question"
                    ),
                })

                continue

            evaluated = evaluate_existing_result(
                item,
                old_result,
            )

            results.append(evaluated)

    # =====================================================
    # FRESH GEMINI MODE
    # =====================================================

    else:

        print(
            "\n⚠ FRESH GEMINI EVALUATION MODE"
        )

        print(
            f"Gemini request delay: "
            f"{REQUEST_DELAY_SECONDS}s"
        )

        print(
            f"Retry delay: "
            f"{RATE_LIMIT_RETRY_SECONDS}s"
        )

        print(
            f"Maximum retries: "
            f"{MAX_RETRIES}"
        )

        pipeline = RAGPipeline()

        results = []

        for index, item in enumerate(dataset):

            print(
                f"\n\n"
                f"QUESTION "
                f"{index + 1}/"
                f"{total_questions}"
            )

            result = evaluate_question(
                pipeline,
                item,
            )

            results.append(result)

            if (
                index
                <
                total_questions - 1
            ):

                print(
                    f"\nWaiting "
                    f"{REQUEST_DELAY_SECONDS}s "
                    f"before next question..."
                )

                time.sleep(
                    REQUEST_DELAY_SECONDS
                )

    # =====================================================
    # SUMMARY
    # =====================================================

    total = len(results)

    successful_results = [
        result
        for result in results
        if not result.get("error")
    ]

    failed_results = [
        result
        for result in results
        if result.get("error")
    ]

    successful_total = len(
        successful_results
    )

    failed_total = len(
        failed_results
    )

    answer_passed = sum(
        result["answer_correct"]
        for result in successful_results
    )

    source_passed = sum(
        result["source_correct"]
        for result in successful_results
    )

    answer_accuracy = (
        answer_passed / successful_total
        if successful_total
        else 0
    )

    source_accuracy = (
        source_passed / successful_total
        if successful_total
        else 0
    )

    # =====================================================
    # SUMMARY OUTPUT
    # =====================================================

    print("\n\n")

    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Questions Tested : "
        f"{total}"
    )

    print(
        f"Successful       : "
        f"{successful_total}"
    )

    print(
        f"API Failures     : "
        f"{failed_total}"
    )

    print()

    print(
        f"Answer Accuracy  : "
        f"{answer_accuracy:.2%}"
    )

    print(
        f"Source Accuracy  : "
        f"{source_accuracy:.2%}"
    )

    print()

    print(
        f"Answer Passed    : "
        f"{answer_passed}/"
        f"{successful_total}"
    )

    print(
        f"Source Passed    : "
        f"{source_passed}/"
        f"{successful_total}"
    )

    # =====================================================
    # ANSWER FAILURES
    # =====================================================

    genuine_answer_failures = [
        result
        for result in successful_results
        if not result["answer_correct"]
    ]

    print("\n")
    print("=" * 70)
    print("ANSWER FAILURES")
    print("=" * 70)

    if genuine_answer_failures:

        for result in genuine_answer_failures:

            print(
                f"\n✗ "
                f"{result['id']}: "
                f"{result['question']}"
            )

            print(
                "Missing keywords: "
                f"{result.get('missing_keywords', [])}"
            )

            print(
                "Missing numbers: "
                f"{result.get('missing_numbers', [])}"
            )

            print(
                "Keyword coverage: "
                f"{result.get('keyword_coverage', 0):.2%}"
            )

    else:

        print(
            "None — all successfully generated "
            "answers passed the evaluator."
        )

    # =====================================================
    # SOURCE FAILURES
    # =====================================================

    genuine_source_failures = [
        result
        for result in successful_results
        if not result["source_correct"]
    ]

    print("\n")
    print("=" * 70)
    print("SOURCE FAILURES")
    print("=" * 70)

    if genuine_source_failures:

        for result in genuine_source_failures:

            print(
                f"\n✗ "
                f"{result['id']}: "
                f"{result['question']}"
            )

    else:

        print(
            "None — all successfully generated "
            "answers had the required source."
        )

    # =====================================================
    # API FAILURES
    # =====================================================

    print("\n")
    print("=" * 70)
    print("API / GEMINI FAILURES")
    print("=" * 70)

    if failed_results:

        for result in failed_results:

            print(
                f"\n⚠ "
                f"{result['id']}: "
                f"{result['question']}"
            )

            print(
                f"Error: "
                f"{result.get('error')}"
            )

    else:

        print(
            "None — all required results "
            "were available."
        )

    # =====================================================
    # SAVE RESULTS
    # =====================================================

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n")
    print("=" * 70)
    print("RESULTS SAVED")
    print("=" * 70)

    print(RESULTS_PATH)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()