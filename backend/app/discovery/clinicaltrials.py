from app.document_models import TrialDocument
from app.document_sources import DocumentSource


def discover_documents(study: dict) -> list[TrialDocument]:
    """
    Discover document URLs available directly
    from the ClinicalTrials.gov study JSON.

    Returns an empty list if none are present.
    """

    documents = []

    # Placeholder implementation.
    # We'll inspect the API response and support every
    # document location exposed by ClinicalTrials.gov.

    return documents