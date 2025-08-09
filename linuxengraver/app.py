from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Linux Engraver")

    win = MainWindow()
    win.resize(1200, 800)
    win.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
