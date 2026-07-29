from enum import Enum


class DocumentSource(str, Enum):
    CLINICALTRIALS = "clinicaltrials.gov"
    PUBMED = "pubmed"
    SPONSOR = "sponsor"
    NIH = "nih"
    FDA = "fda"