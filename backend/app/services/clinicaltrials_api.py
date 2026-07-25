import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_studies(
    query: str = "lung cancer",
    page_size: int = 100,
    page_token: str | None = None,
):
    params = {
        "query.term": query,
        "pageSize": page_size,
    }

    if page_token:
        params["pageToken"] = page_token

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()