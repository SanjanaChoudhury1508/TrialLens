from dataclasses import dataclass, field


@dataclass
class DocumentSection:
    title: str
    level: int
    text: str
    page: int | None = None


@dataclass
class DocumentTable:
    title: str | None = None
    rows: list[list[str]] = field(default_factory=list)
    page: int | None = None


@dataclass
class ParsedDocument:
    document_id: str

    title: str

    sections: list[DocumentSection] = field(default_factory=list)

    tables: list[DocumentTable] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
    