import requests


OPENFDA_URL = "https://api.fda.gov/drug/event.json"


class FAERSService:

    def search_drug(self, drug_name: str, limit: int = 10):

        params = {
            "search": f'patient.drug.medicinalproduct:"{drug_name}"',
            "limit": limit,
        }

        response = requests.get(
            OPENFDA_URL,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def summarize_events(self, data):

        results = data.get("results", [])

        events = []

        for record in results:

            patient = record.get("patient", {})

            drugs = patient.get("drug", [])
            reactions = patient.get("reaction", [])

            event = {
                "received_date": record.get(
                    "receivedate"
                ),
                "serious": record.get(
                    "serious"
                ),
                "seriousness": {
                    "death": record.get("seriousnessdeath"),
                    "hospitalization": record.get(
                        "seriousnesshospitalization"
                    ),
                    "life_threatening": record.get(
                        "seriousnesslifethreatening"
                    ),
                    "disability": record.get(
                        "seriousnessdisabling"
                    ),
                    "congenital_anomaly": record.get(
                        "seriousnesscongenitalanomali"
                    ),
                    "other": record.get(
                        "seriousnessother"
                    ),
                },
                "drugs": [
                    drug.get("medicinalproduct")
                    for drug in drugs
                    if drug.get("medicinalproduct")
                ],
                "reactions": [
                    reaction.get("reactionmeddrapt")
                    for reaction in reactions
                    if reaction.get("reactionmeddrapt")
                ],
            }

            events.append(event)

        return events