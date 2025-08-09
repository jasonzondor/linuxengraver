from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class _BaseShape(BaseModel):
    pass


class RectSpec(_BaseShape):
    type: Literal["rect"] = "rect"
    x: float
    y: float
    w: float
    h: float


class CircleSpec(_BaseShape):
    type: Literal["circle"] = "circle"
    cx: float
    cy: float
    r: float


# Discriminated union for shape specs
ShapeSpec = Annotated[Union[RectSpec, CircleSpec], Field(discriminator="type")]
