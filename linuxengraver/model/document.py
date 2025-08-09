from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from .material import Material
from .shapes import ShapeSpec


class Document(BaseModel):
    material: Material = Field(...)
    shapes: List[ShapeSpec] = Field(default_factory=list)

    # Persistence
    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, data: str) -> "Document":
        return cls.model_validate_json(data)

    def save_json(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> "Document":
        return cls.from_json(path.read_text(encoding="utf-8"))
