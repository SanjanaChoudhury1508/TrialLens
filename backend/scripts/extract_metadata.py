import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.models import ClinicalTrial

RAW_FILE = Path("data/raw/studies_page1.json")
OUTPUT_FILE = Path("data/metadata/studies_metadata.json")


with RAW_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

metadata = []

for study in data.get("studies", []):

    protocol = study.get("protocolSection", {})

    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    description = protocol.get("descriptionModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    interventions = protocol.get("armsInterventionsModule", {})
    outcomes = protocol.get("outcomesModule", {})
    locations = protocol.get("contactsLocationsModule", {})

    trial = ClinicalTrial(
        nct_id=identification.get("nctId"),
        brief_title=identification.get("briefTitle"),
        official_title=identification.get("officialTitle"),
        study_type=design.get("studyType"),
        phase=design.get("phases"),
        status=status.get("overallStatus"),
        conditions=conditions.get("conditions"),
        summary=description.get("briefSummary"),
        sponsor=sponsor.get("leadSponsor", {}).get("name"),
        enrollment=design.get("enrollmentInfo", {}).get("count"),
        eligibility=eligibility.get("eligibilityCriteria"),
        interventions=interventions.get("interventions"),
        primary_outcomes=outcomes.get("primaryOutcomes"),
        locations=locations.get("locations"),
    )

    metadata.append(trial.to_dict())

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"Extracted {len(metadata)} studies.")
print(f"Saved metadata to {OUTPUT_FILE}")