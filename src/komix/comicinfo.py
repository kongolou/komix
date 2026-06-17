from dataclasses import field

from pydantic.dataclasses import dataclass


@dataclass
class ComicInfo:
    title: str = ""
    id: str = ""
    authors: list[str] = field(default_factory=list)
    summary: str = ""
    tags: list[str] = field(default_factory=list)
