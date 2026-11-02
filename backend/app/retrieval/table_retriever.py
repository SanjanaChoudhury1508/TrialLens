from app.config import settings


class TableRetriever:

    def __init__(self):
        if settings.DEPLOYMENT_MODE == "cloud":
            from app.database.cloud_vector_store import CloudVectorStore
            self.store = CloudVectorStore()
        else:
            from app.database.vector_store import VectorStore
            self.store = VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        trial_id: str | None = None,
    ):
        results = self.store.search_tables(
            query=query,
            top_k=top_k,
            trial_id=trial_id,
        )

        formatted = []

        for table in results:
            formatted.append({
                "source_type": "Clinical PDF Table",
                "table_id": table["table_id"],
                "document_id": table["document_id"],
                "trial_id": table["trial_id"],
                "title": table["title"],
                "headers": table["headers"],
                "rows": table["rows"],
                "page": table["page"],
                "metadata": table["metadata"],
            })

        return formatted
