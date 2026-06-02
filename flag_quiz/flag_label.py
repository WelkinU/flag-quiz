from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel


class FlagLabel(QLabel):
    """Displays a country flag scaled to fit, maintaining aspect ratio."""

    TARGET_W = 480
    TARGET_H = 320

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.TARGET_W, self.TARGET_H)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "background-color: #1e1e2e; border: 2px solid #444466; border-radius: 8px;"
        )
        # Default to world countries; updated by start_quiz per dataset
        self._flags_dir: Path = Path(__file__).parent.parent / "flags" / "countries"
        self._current_code: str | None = None

    def set_flags_dir(self, path: Path) -> None:
        self._flags_dir = path

    def set_flag(self, code: str) -> None:
        self._current_code = code
        path = self._flags_dir / f"{code}.png"
        if not path.exists():
            self.setText(f"[{code.upper()}]")
            return
        pixmap = QPixmap(str(path))
        scaled = pixmap.scaled(
            self.TARGET_W - 16,
            self.TARGET_H - 16,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def clear_flag(self) -> None:
        self._current_code = None
        self.clear()
        self.setStyleSheet(
            "background-color: #1e1e2e; border: 2px solid #444466; border-radius: 8px;"
        )
