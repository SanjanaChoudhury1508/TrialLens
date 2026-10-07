from dataclasses import dataclass, field, asdict


@dataclass
class DocumentSection:
    title: str
    level: int
    text: str
    page: int | None = None


@dataclass
class DocumentTable:
    table_id: str
    document_id: str
    title: str | None = None
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    page: int | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class ParsedDocument:
    document_id: str
    title: str
    sections: list[DocumentSection] = field(default_factory=list)
    tables: list[DocumentTable] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)