import re
import requests

from app.agents.state import TrialLensState


CLINICALTRIALS_URL = "https://clinicaltrials.gov/api/v2/studies"


class StructuredDataAgent:

    def __init__(self):
        self.url = CLINICALTRIALS_URL

    def _extract_nct_id(self, question: str):
        match = re.search(r"\bNCT\d{8}\b", question, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def _extract_search_term(self, question: str):
        """
        Extract a useful search term when the user asks for
        structured trial information but does not provide an NCT ID.
        """

        q = question.lower()

        # Common disease / drug terms from the question.
        stop_words = {
            "what", "which", "where", "when", "how", "many",
            "is", "are", "was", "were", "the", "a", "an",
            "in", "of", "for", "with", "on", "and", "or",
            "trial", "trials", "study", "studies",
            "currently", "status", "recruiting",
            "recruitment", "phase", "location"
        }

        words = re.findall(r"[a-zA-Z0-9\-]+", q)

        useful = [
            word for word in words
            if word not in stop_words and len(word) > 2
        ]

        return " ".join(useful[:6])

    def _fetch_trial(self, nct_id: str):
        response = requests.get(
            f"{self.url}/{nct_id}",
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def _search_trials(self, search_term: str):
        params = {
            "query.term": search_term,
            "pageSize": 10,
            "format": "json",
        }

        response = requests.get(
            self.url,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        return response.json()

    def _parse_study(self, study):
        protocol = study.get("protocolSection", {})

        identification = protocol.get(
            "identificationModule", {}
        )

        status = protocol.get(
            "statusModule", {}
        )

        design = protocol.get(
            "designModule", {}
        )

        description = protocol.get(
            "descriptionModule", {}
        )

        sponsor = protocol.get(
            "sponsorCollaboratorsModule", {}
        )

        locations_module = protocol.get(
            "contactsLocationsModule", {}
        )

        locations = locations_module.get("locations", [])

        return {
            "nct_id": identification.get("nctId"),
            "title": identification.get("briefTitle"),
            "official_title": identification.get("officialTitle"),
            "overall_status": status.get("overallStatus"),
            "phase": design.get("phases", []),
            "study_type": design.get("studyType"),
            "start_date": status.get("startDateStruct", {}).get("date"),
            "completion_date": status.get(
                "completionDateStruct", {}
            ).get("date"),
            "enrollment": design.get(
                "enrollmentInfo", {}
            ).get("count"),
            "enrollment_type": design.get(
                "enrollmentInfo", {}
            ).get("type"),
            "brief_summary": description.get("briefSummary"),
            "sponsor": sponsor.get(
                "leadSponsor", {}
            ).get("name"),
            "locations": [
                {
                    "city": loc.get("city"),
                    "state": loc.get("state"),
                    "country": loc.get("country"),
                }
                for loc in locations[:20]
            ],
        }

    def run(self, state: TrialLensState) -> TrialLensState:

        question = state["question"]

        try:

            nct_id = self._extract_nct_id(question)

            # Direct lookup when an NCT number is present.
            if nct_id:

                study = self._fetch_trial(nct_id)

                parsed = self._parse_study(study)

                result = {
                    "source": "ClinicalTrials.gov",
                    "query_type": "direct_trial_lookup",
                    "data": parsed,
                }

                return {
                    "structured_results": [result],
                    "execution_trace": ["structured_agent"],
                }

            # Otherwise perform a structured search.
            search_term = self._extract_search_term(question)

            if not search_term:
                return {
                    "structured_results": [],
                    "execution_trace": [
                        "structured_agent:no_query"
                    ],
                }

            data = self._search_trials(search_term)

            studies = data.get("studies", [])

            parsed_studies = [
                self._parse_study(study)
                for study in studies
            ]

            result = {
                "source": "ClinicalTrials.gov",
                "query_type": "trial_search",
                "search_term": search_term,
                "count": len(parsed_studies),
                "studies": parsed_studies,
            }

            return {
                "structured_results": [result],
                "execution_trace": ["structured_agent"],
            }

        except requests.RequestException as exc:

            return {
                "structured_results": [],
                "errors": [
                    f"ClinicalTrials.gov API error: {exc}"
                ],
                "execution_trace": [
                    "structured_agent:error"
                ],
            }

        except Exception as exc:

            return {
                "structured_results": [],
                "errors": [
                    f"Structured agent error: {exc}"
                ],
                "execution_trace": [
                    "structured_agent:error"
                ],
            }


structured_agent = StructuredDataAgent()