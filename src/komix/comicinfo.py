from dataclasses import field

from pydantic.dataclasses import dataclass


@dataclass
class ComicInfo:
    title: str = ""
    id: str = ""
    author: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)
