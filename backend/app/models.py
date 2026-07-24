from dataclasses import dataclass, asdict
from typing import List, Optional, Any


@dataclass
class ClinicalTrial:
    nct_id: str
    brief_title: Optional[str]
    official_title: Optional[str]
    study_type: Optional[str]
    phase: Optional[List[str]]
    status: Optional[str]
    conditions: Optional[List[str]]
    summary: Optional[str]
    sponsor: Optional[str]
    enrollment: Optional[int]
    eligibility: Optional[str]
    interventions: Optional[List[Any]]
    primary_outcomes: Optional[List[Any]]
    locations: Optional[List[Any]]

    def to_dict(self):
        return asdict(self)