from __future__ import annotations

from typing import Iterable, List, Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView

from ..model.shapes import CircleSpec, RectSpec, ShapeSpec


class CanvasView(QGraphicsView):
    """Simple canvas built on QGraphicsView/Scene.

    Supports tools: select, rect, circle. Exports/imports basic shape specs.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._workspace_rect: Optional[QGraphicsRectItem] = None
        self._tool: str = "select"

        # Drawing state
        self._drag_start: Optional[QPointF] = None
        self._preview_item: Optional[QGraphicsItem] = None

        # Visuals
        self._pen_shape = QPen(Qt.black, 1)
        self._brush_shape = QBrush(Qt.transparent)
        self._pen_workspace = QPen(Qt.darkGray, 1, Qt.DashLine)

    # Workspace sizing
    def set_workspace_size(self, width_mm: float, height_mm: float) -> None:
        # Map 1 mm to 1 px for now; later we can scale with DPI/zoom
        rect = QRectF(0, 0, width_mm, height_mm)
        if self._workspace_rect is None:
            self._workspace_rect = QGraphicsRectItem(rect)
            self._workspace_rect.setPen(self._pen_workspace)
            self._workspace_rect.setBrush(QBrush(Qt.white))
            self._workspace_rect.setZValue(-100)
            self._workspace_rect.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self._workspace_rect.setFlag(QGraphicsItem.ItemIsMovable, False)
            self._scene.addItem(self._workspace_rect)
        else:
            self._workspace_rect.setRect(rect)
        self._scene.setSceneRect(rect.adjusted(-50, -50, 50, 50))
        self.fitInView(self._workspace_rect, Qt.KeepAspectRatio)

    # Tools
    def set_tool(self, tool: str) -> None:
        self._tool = tool
        self._clear_preview()
        if tool == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)

    # Scene ops
    def clear_shapes(self) -> None:
        for item in list(self._scene.items()):
            if item is self._workspace_rect:
                continue
            self._scene.removeItem(item)
        self._clear_preview()

    def add_shape_from_spec(self, spec: ShapeSpec) -> None:
        if isinstance(spec, RectSpec):
            item = QGraphicsRectItem(spec.x, spec.y, spec.w, spec.h)
        elif isinstance(spec, CircleSpec):
            # ellipse rect: top-left = center - r
            item = QGraphicsEllipseItem(spec.cx - spec.r, spec.cy - spec.r, 2 * spec.r, 2 * spec.r)
        else:
            return
        self._style_item(item)
        self._scene.addItem(item)

    def export_shape_specs(self) -> Iterable[ShapeSpec]:
        out: List[ShapeSpec] = []
        for item in self._scene.items():
            if item is self._workspace_rect:
                continue
            if isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                out.append(RectSpec(x=rect.x(), y=rect.y(), w=rect.width(), h=rect.height()))
            elif isinstance(item, QGraphicsEllipseItem):
                rect = item.rect()
                cx = rect.x() + rect.width() / 2
                cy = rect.y() + rect.height() / 2
                r = rect.width() / 2
                out.append(CircleSpec(cx=cx, cy=cy, r=r))
        return out

    # Mouse events for drawing tools
    def mousePressEvent(self, event):  # noqa: N802
        if self._tool in ("rect", "circle") and event.button() == Qt.LeftButton:
            self._drag_start = self.mapToScene(event.pos())
            if self._tool == "rect":
                self._preview_item = QGraphicsRectItem()
            else:
                self._preview_item = QGraphicsEllipseItem()
            self._style_item(self._preview_item)
            self._preview_item.setOpacity(0.7)
            self._scene.addItem(self._preview_item)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._drag_start is not None and self._preview_item is not None:
            pos = self.mapToScene(event.pos())
            rect = QRectF(self._drag_start, pos).normalized()
            if isinstance(self._preview_item, QGraphicsRectItem):
                self._preview_item.setRect(rect)
            elif isinstance(self._preview_item, QGraphicsEllipseItem):
                # make it a circle with radius=min half of w/h
                s = min(rect.width(), rect.height())
                circle_rect = QRectF(rect.topLeft(), rect.topLeft() + QPointF(s, s)).normalized()
                self._preview_item.setRect(circle_rect)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        if self._drag_start is not None and self._preview_item is not None and event.button() == Qt.LeftButton:
            # finalize preview as normal item
            self._preview_item.setOpacity(1.0)
            self._preview_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self._preview_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            self._preview_item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self._preview_item = None
            self._drag_start = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # Helpers
    def _style_item(self, item: QGraphicsItem) -> None:
        if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
            item.setPen(self._pen_shape)
            item.setBrush(self._brush_shape)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setFlag(QGraphicsItem.ItemIsMovable, True)

    def _clear_preview(self) -> None:
        if self._preview_item is not None:
            self._scene.removeItem(self._preview_item)
            self._preview_item = None
            self._drag_start = None
