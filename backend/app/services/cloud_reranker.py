import re


class CloudReranker:
    """
    Lightweight lexical reranker for cloud deployment.

    Replaces the local CrossEncoder only in cloud mode.
    """

    STOPWORDS = {
        "the", "and", "for", "with", "that", "this",
        "from", "were", "was", "are", "what", "which",
        "who", "how", "when", "where", "does", "did",
        "has", "have", "had", "into", "their", "they",
        "them", "about", "than", "then", "also",
    }

    def rerank(
        self,
        question: str,
        results: list[dict],
        top_k: int = 5,
    ) -> list[dict]:

        if not results:
            return []

        query_terms = {
            token
            for token in re.findall(
                r"\b[a-zA-Z0-9-]+\b",
                question.lower(),
            )
            if len(token) >= 3
            and token not in self.STOPWORDS
        }

        ranked = []

        for result in results:
            content = (
                f"{result.get('section', '')} "
                f"{result.get('content', '')}"
            ).lower()

            content_terms = set(
                re.findall(r"\b[a-zA-Z0-9-]+\b", content)
            )

            overlap = query_terms.intersection(content_terms)

            lexical_score = (
                len(overlap) / len(query_terms)
                if query_terms else 0.0
            )

            keyword_score = float(
                result.get("keyword_score") or 0.0
            )

            item = dict(result)
            item["rerank_score"] = (
                lexical_score + 0.1 * keyword_score
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked[:top_k]