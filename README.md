# Linux Engraver

A desktop CNC 3D engraving design tool (initial scaffold) for Linux.

This early version provides:
- Set material properties (width, height, thickness)
- Draw simple shapes (rectangle, circle) on a 2D canvas
- Save/Open design as JSON

Planned next steps:
- Star and other shapes
- 3D height preview / toolpath preview
- G-code export
- Units support (mm/in)
- Layers and per-operation settings

## Quick start

Requirements: Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m linuxengraver.app
```

## Project structure

- `linuxengraver/app.py` – Entry point creating the main window.
- `linuxengraver/ui/main_window.py` – Main UI composition (toolbar, sidebar, canvas).
- `linuxengraver/view/canvas.py` – Custom canvas built on QGraphicsScene/View for drawing/editing shapes.
- `linuxengraver/model/material.py` – Material properties model.
- `linuxengraver/model/shapes.py` – Shape models and serialization helpers.
- `linuxengraver/model/document.py` – Design document model (material + shapes) with save/load.
- `linuxengraver/export/gcode.py` – Placeholder for G-code export.

## Notes
- This scaffold focuses on a clean foundation over features. We’ll iterate fast.
- If PySide6 fails to install on your distro, try system Qt deps or use PyQt6; code is easily adaptable.
