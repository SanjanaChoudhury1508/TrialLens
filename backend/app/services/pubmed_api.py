import requests
from app.document_models import TrialDocument
from app.document_sources import DocumentSource

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

DETAILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def search_by_nct_id(nct_id: str):
    params = {
        "db": "pubmed",
        "term": nct_id,
        "retmode": "json",
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

def fetch_article_details(pubmed_ids):
    if not pubmed_ids:
        return None

    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "json",
    }

    response = requests.get(DETAILS_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

def parse_articles(nct_id: str, details: dict) -> list[TrialDocument]:
    documents = []

    result = details["result"]

    for uid in result["uids"]:

        article = result[uid]

        doi = None
        pmcid = None

        for identifier in article.get("articleids", []):

            if identifier["idtype"] == "doi":
                doi = identifier["value"]

            elif identifier["idtype"] == "pmc":
                pmcid = identifier["value"]

        documents.append(
            TrialDocument(
                nct_id=nct_id,
                title=article["title"],
                document_type="Publication",
                source=DocumentSource.PUBMED.value,
                doi=doi,
                pmid=uid,
                pmcid=pmcid,
            )
        )

    return documents