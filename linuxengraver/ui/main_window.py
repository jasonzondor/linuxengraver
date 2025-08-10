from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QActionGroup
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QToolBar,
    QWidget,
    QFormLayout,
    QDoubleSpinBox,
    QDockWidget,
    QMessageBox,
)

from ..model.document import Document
from ..model.material import Material
from ..model.shapes import ShapeSpec
from ..view.canvas import CanvasView
from ..export.gcode import export_gcode


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Linux Engraver")

        # Document state
        self.document = Document(material=Material(width=100.0, height=100.0, thickness=10.0))
        self.current_file: Optional[Path] = None

        # Central canvas
        self.canvas = CanvasView(self)
        self.setCentralWidget(self.canvas)

        # Docks and menus
        self._create_material_dock()
        self._create_menus()
        self._create_shapes_toolbar()

        self._apply_material_to_canvas()
        self._update_window_title()

    # UI
    def _create_toolbar(self) -> None:
        tb = QToolBar("Tools", self)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(tb)

        # File actions
        act_new = QAction(QIcon.fromTheme("document-new"), "New", self)
        act_new.triggered.connect(self.action_new)
        tb.addAction(act_new)

        act_open = QAction(QIcon.fromTheme("document-open"), "Open", self)
        act_open.triggered.connect(self.action_open)
        tb.addAction(act_open)

        act_save = QAction(QIcon.fromTheme("document-save"), "Save", self)
        act_save.triggered.connect(self.action_save)
        tb.addAction(act_save)

        act_export = QAction("Export G-code", self)
        act_export.triggered.connect(self.action_export_gcode)
        tb.addAction(act_export)

        tb.addSeparator()

        # Draw actions
        act_rect = QAction("Rectangle", self)
        act_rect.triggered.connect(lambda: self.canvas.set_tool("rect"))
        tb.addAction(act_rect)

        act_circle = QAction("Circle", self)
        act_circle.triggered.connect(lambda: self.canvas.set_tool("circle"))
        tb.addAction(act_circle)

        tb.addSeparator()

        act_select = QAction("Select", self)
        act_select.triggered.connect(lambda: self.canvas.set_tool("select"))
        tb.addAction(act_select)

    def _create_material_dock(self) -> None:
        dock = QDockWidget("Material", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        w = QWidget(dock)
        form = QFormLayout(w)

        self.spin_width = QDoubleSpinBox(w)
        self.spin_width.setRange(1.0, 10000.0)
        self.spin_width.setSuffix(" mm")
        self.spin_width.setValue(self.document.material.width)
        self.spin_width.valueChanged.connect(self._material_changed)

        self.spin_height = QDoubleSpinBox(w)
        self.spin_height.setRange(1.0, 10000.0)
        self.spin_height.setSuffix(" mm")
        self.spin_height.setValue(self.document.material.height)
        self.spin_height.valueChanged.connect(self._material_changed)

        self.spin_thickness = QDoubleSpinBox(w)
        self.spin_thickness.setRange(0.1, 1000.0)
        self.spin_thickness.setSuffix(" mm")
        self.spin_thickness.setDecimals(3)
        self.spin_thickness.setValue(self.document.material.thickness)
        self.spin_thickness.valueChanged.connect(self._material_changed)

        form.addRow("Width", self.spin_width)
        form.addRow("Height", self.spin_height)
        form.addRow("Thickness", self.spin_thickness)

        w.setLayout(form)
        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.material_dock = dock
        # Start hidden; user can toggle from View menu
        self.material_dock.hide()

    def _create_shapes_toolbar(self) -> None:
        tb = QToolBar("Shapes", self)
        tb.setObjectName("ShapesToolbar")
        self.addToolBar(Qt.TopToolBarArea, tb)

        group = QActionGroup(self)
        group.setExclusive(True)

        act_select = QAction("Select", self)
        act_select.setCheckable(True)
        act_select.setChecked(True)
        act_select.triggered.connect(lambda: self.canvas.set_tool("select"))
        group.addAction(act_select)
        tb.addAction(act_select)

        act_rect = QAction("Rectangle", self)
        act_rect.setCheckable(True)
        act_rect.triggered.connect(lambda: self.canvas.set_tool("rect"))
        group.addAction(act_rect)
        tb.addAction(act_rect)

        act_circle = QAction("Circle", self)
        act_circle.setCheckable(True)
        act_circle.triggered.connect(lambda: self.canvas.set_tool("circle"))
        group.addAction(act_circle)
        tb.addAction(act_circle)

    def _create_menus(self) -> None:
        mb = self.menuBar()

        # File menu
        m_file = mb.addMenu("&File")
        act_new = QAction("&New", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self.action_new)
        m_file.addAction(act_new)

        act_open = QAction("&Open…", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self.action_open)
        m_file.addAction(act_open)

        act_save = QAction("&Save", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(self.action_save)
        m_file.addAction(act_save)

        act_save_as = QAction("Save &As…", self)
        act_save_as.setShortcut("Ctrl+Shift+S")
        act_save_as.triggered.connect(self.action_save_as)
        m_file.addAction(act_save_as)

        m_file.addSeparator()

        act_export = QAction("E&xport G-code…", self)
        act_export.setShortcut("Ctrl+E")
        act_export.triggered.connect(self.action_export_gcode)
        m_file.addAction(act_export)

        m_file.addSeparator()

        act_exit = QAction("E&xit", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        m_file.addAction(act_exit)

        # Edit menu
        m_edit = mb.addMenu("&Edit")
        act_select_all = QAction("Select &All", self)
        act_select_all.setShortcut("Ctrl+A")
        act_select_all.triggered.connect(self.canvas.select_all)
        m_edit.addAction(act_select_all)

        act_delete = QAction("&Delete Selection", self)
        act_delete.setShortcut("Del")
        act_delete.triggered.connect(self.canvas.delete_selection)
        m_edit.addAction(act_delete)

        # View menu
        m_view = mb.addMenu("&View")
        act_zoom_in = QAction("Zoom &In", self)
        act_zoom_in.setShortcut("Ctrl++")
        act_zoom_in.triggered.connect(self.canvas.zoom_in)
        m_view.addAction(act_zoom_in)

        act_zoom_out = QAction("Zoom &Out", self)
        act_zoom_out.setShortcut("Ctrl+-")
        act_zoom_out.triggered.connect(self.canvas.zoom_out)
        m_view.addAction(act_zoom_out)

        act_zoom_reset = QAction("Reset &Zoom", self)
        act_zoom_reset.setShortcut("Ctrl+0")
        act_zoom_reset.triggered.connect(self.canvas.reset_zoom)
        m_view.addAction(act_zoom_reset)

        if hasattr(self, "material_dock"):
            m_view.addSeparator()
            m_view.addAction(self.material_dock.toggleViewAction())

    # Material handling
    def _material_changed(self) -> None:
        self.document.material = Material(
            width=float(self.spin_width.value()),
            height=float(self.spin_height.value()),
            thickness=float(self.spin_thickness.value()),
        )
        self._apply_material_to_canvas()

    def _apply_material_to_canvas(self) -> None:
        self.canvas.set_workspace_size(self.document.material.width, self.document.material.height)

    def _update_window_title(self) -> None:
        name = str(self.current_file.name) if self.current_file else "Untitled"
        self.setWindowTitle(f"Linux Engraver - {name}")

    # File actions
    def action_new(self) -> None:
        self.document = Document(material=self.document.material.copy())
        self.canvas.clear_shapes()
        self.current_file = None
        # Fit the material in the view for a fresh document
        self._apply_material_to_canvas()
        self._update_window_title()

    def action_open(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(self, "Open Design", str(self.current_file or ""), "Design (*.json)")
        if not path_str:
            return
        path = Path(path_str)
        try:
            loaded = Document.load_json(path)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Open failed", f"Could not open file:\n{e}")
            return
        self.document = loaded
        self.current_file = path
        self._sync_canvas_from_document()
        self._update_window_title()

    def action_save(self) -> None:
        if not self.current_file:
            path_str, _ = QFileDialog.getSaveFileName(self, "Save Design", "design.json", "Design (*.json)")
            if not path_str:
                return
            self.current_file = Path(path_str)
        try:
            # Sync document from scene and save
            self._sync_document_from_canvas()
            self.document.save_json(self.current_file)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Save failed", f"Could not save file:\n{e}")
        else:
            self._update_window_title()

    def action_save_as(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(self, "Save Design As", str(self.current_file or "design.json"), "Design (*.json)")
        if not path_str:
            return
        self.current_file = Path(path_str)
        try:
            self._sync_document_from_canvas()
            self.document.save_json(self.current_file)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Save failed", f"Could not save file:\n{e}")
        else:
            self._update_window_title()

    def action_export_gcode(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(self, "Export G-code", "toolpath.gcode", "G-code (*.gcode)")
        if not path_str:
            return
        path = Path(path_str)
        try:
            # Ensure document reflects current canvas
            self._sync_document_from_canvas()
            export_gcode(self.document, path)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Export failed", f"Could not export G-code:\n{e}")
            return
        QMessageBox.information(self, "Export complete", f"G-code written to:\n{path}")

    # Sync helpers
    def _sync_canvas_from_document(self) -> None:
        self._apply_material_to_canvas()
        self.canvas.clear_shapes()
        for spec in self.document.shapes:
            self.canvas.add_shape_from_spec(spec)

    def _sync_document_from_canvas(self) -> None:
        self.document.shapes = [s for s in self.canvas.export_shape_specs()]
