from dataclasses import dataclass, asdict


@dataclass
class TrialDocument:
    nct_id: str
    title: str
    document_type: str
    source: str

    url: str | None = None
    doi: str | None = None
    pmid: str | None = None
    pmcid: str | None = None

    local_path: str | None = None

    def to_dict(self):
        return asdict(self)