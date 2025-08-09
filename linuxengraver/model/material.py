from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Material(BaseModel):
    """Workpiece material properties in mm.

    width, height: planar dimensions of the stock (XY)
    thickness: Z thickness
    """

    width: float = Field(gt=0, description="Material width (mm)")
    height: float = Field(gt=0, description="Material height (mm)")
    thickness: float = Field(gt=0, description="Material thickness (mm)")

    @field_validator("width", "height", "thickness")
    @classmethod
    def _finite(cls, v: float) -> float:  # noqa: D401
        """Ensure finite positive floats."""
        if not (v > 0):
            raise ValueError("Must be > 0")
        return float(v)

    def copy(self) -> "Material":  # type: ignore[override]
        return Material(width=self.width, height=self.height, thickness=self.thickness)
