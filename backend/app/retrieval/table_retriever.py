from app.database.vector_store import VectorStore


class TableRetriever:

    def __init__(self):
        self.store = VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        trial_id: str | None = None,
    ):
        """
        Retrieve structured clinical-trial tables
        relevant to the user's question.
        """

        results = self.store.search_tables(
            query=query,
            top_k=top_k,
            trial_id=trial_id,
        )

        formatted = []

        for table in results:

            formatted.append(
                {
                    "source_type": "Clinical PDF Table",
                    "table_id": table["table_id"],
                    "document_id": table["document_id"],
                    "trial_id": table["trial_id"],
                    "title": table["title"],
                    "headers": table["headers"],
                    "rows": table["rows"],
                    "page": table["page"],
                    "metadata": table["metadata"],
                }
            )

        return formatted