from pathlib import Path
import requests
from bs4 import BeautifulSoup

OA_SERVICE = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"


def get_pdf_url(pmcid: str):

    response = requests.get(
        OA_SERVICE,
        params={"id": pmcid},
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")

    for link in soup.find_all("link"):

        if link.get("format") == "pdf":

            href = link.get("href")

            if href.startswith("ftp://"):
                href = href.replace(
                    "ftp://ftp.ncbi.nlm.nih.gov",
                    "https://ftp.ncbi.nlm.nih.gov",
                )

            return href

    return None


def download_pmc_pdf(
    pmcid: str,
    output_dir: Path,
):

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = output_dir / f"{pmcid}.pdf"

    if pdf_path.exists():
        return pdf_path

    pdf_url = get_pdf_url(pmcid)

    if pdf_url is None:
        return None

    try:

        response = requests.get(
            pdf_url,
            timeout=60,
        )

        if response.status_code != 200:
            print(f"PDF download failed ({response.status_code})")
            return None

        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path

    except requests.RequestException as e:

        print(f"Download error: {e}")

        return None