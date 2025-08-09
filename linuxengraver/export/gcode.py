from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..model.document import Document
from ..model.shapes import CircleSpec, RectSpec, ShapeSpec


def export_gcode(doc: Document, path: Path) -> None:
    """Very early placeholder: emit simple contour moves at Z=0.

    NOTE: Real toolpathing requires CAM logic (tool diameter, stepover, depth per pass, 
    lead-ins/outs, safe Z, spindle control, units, etc). This stub just proves plumbing.
    """
    lines: list[str] = []
    lines.extend(_preamble())
    for s in doc.shapes:
        lines.extend(_shape_to_gcode(s))
    lines.extend(_postamble())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _preamble() -> list[str]:
    return [
        "; Linux Engraver stub G-code",
        "G90 ; absolute positioning",
        "G21 ; units in mm",
        "G0 Z5.0 ; safe height",
    ]


def _postamble() -> list[str]:
    return [
        "G0 Z5.0",
        "M5 ; spindle stop",
        "M2 ; program end",
    ]


def _shape_to_gcode(s: ShapeSpec) -> Iterable[str]:
    if isinstance(s, RectSpec):
        x, y, w, h = s.x, s.y, s.w, s.h
        return [
            f"G0 X{x:.3f} Y{y:.3f}",
            "G1 Z0.000 F300.0",
            f"G1 X{x + w:.3f} Y{y:.3f} F600.0",
            f"G1 X{x + w:.3f} Y{y + h:.3f}",
            f"G1 X{x:.3f} Y{y + h:.3f}",
            f"G1 X{x:.3f} Y{y:.3f}",
            "G0 Z5.000",
        ]
    if isinstance(s, CircleSpec):
        # Approximate with 36-segment polygon
        cx, cy, r = s.cx, s.cy, s.r
        import math

        pts = [
            (cx + r * math.cos(2 * math.pi * i / 36), cy + r * math.sin(2 * math.pi * i / 36))
            for i in range(37)
        ]
        lines: list[str] = [f"G0 X{pts[0][0]:.3f} Y{pts[0][1]:.3f}", "G1 Z0.000 F300.0"]
        for x, y in pts[1:]:
            lines.append(f"G1 X{x:.3f} Y{y:.3f} F600.0")
        lines.append("G0 Z5.000")
        return lines
    return []
