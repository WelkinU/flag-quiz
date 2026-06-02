from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from flag_quiz.quiz_engine import QuizState


def _grade(pct: float) -> tuple[str, str]:
    """Return (emoji, label) based on percentage."""
    if pct >= 90:
        return "🏆", "Outstanding!"
    if pct >= 70:
        return "🎉", "Great job!"
    if pct >= 50:
        return "👍", "Not bad!"
    if pct >= 30:
        return "📚", "Keep practising!"
    return "🌍", "Time to study the atlas…"


class ResultsScreen(QWidget):
    play_again = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(24)
        root.setContentsMargins(60, 40, 60, 40)

        self._emoji_label = QLabel("🏆")
        self._emoji_label.setAlignment(Qt.AlignCenter)
        self._emoji_label.setStyleSheet("font-size: 64px;")
        root.addWidget(self._emoji_label)

        self._grade_label = QLabel("Outstanding!")
        self._grade_label.setAlignment(Qt.AlignCenter)
        self._grade_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(self._grade_label)

        self._mode_label = QLabel()
        self._mode_label.setAlignment(Qt.AlignCenter)
        self._mode_label.setStyleSheet("font-size: 15px; color: #a6adc8;")
        self._mode_label.hide()
        root.addWidget(self._mode_label)

        # Score card
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #1e1e2e; border: 1px solid #444466; border-radius: 12px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(40, 28, 40, 28)

        self._score_big = QLabel("18 / 30")
        self._score_big.setAlignment(Qt.AlignCenter)
        self._score_big.setStyleSheet(
            "font-size: 52px; font-weight: bold; color: #89b4fa;"
        )
        card_layout.addWidget(self._score_big)

        self._pct_label = QLabel("60%")
        self._pct_label.setAlignment(Qt.AlignCenter)
        self._pct_label.setStyleSheet("font-size: 22px; color: #a6adc8;")
        card_layout.addWidget(self._pct_label)

        root.addWidget(card)
        root.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        play_btn = QPushButton("Play Again")
        play_btn.setFixedHeight(52)
        play_btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-size: 16px;"
            " font-weight: bold; border-radius: 10px; }"
            "QPushButton:hover { background-color: #b4d0fa; }"
        )
        play_btn.clicked.connect(self.play_again)
        btn_row.addWidget(play_btn)

        quit_btn = QPushButton("Quit")
        quit_btn.setFixedHeight(52)
        quit_btn.setStyleSheet(
            "QPushButton { background-color: #313244; color: #cdd6f4; font-size: 16px;"
            " border: 1px solid #585b70; border-radius: 10px; }"
            "QPushButton:hover { background-color: #45475a; }"
        )
        quit_btn.clicked.connect(self.quit_requested)
        btn_row.addWidget(quit_btn)

        root.addLayout(btn_row)

    def show_results(self, state: QuizState) -> None:
        correct = state.correct
        total = state.answered
        pct = (correct / total * 100) if total > 0 else 0

        emoji, grade = _grade(pct)
        self._emoji_label.setText(emoji)
        self._grade_label.setText(grade)
        self._score_big.setText(f"{correct} / {total}")
        self._pct_label.setText(f"{pct:.0f}%")

        if state.settings.quiz_mode == "timed":
            secs = state.settings.timer_seconds
            mins, rem = divmod(secs, 60)
            time_str = f"{mins}m {rem}s" if rem else f"{mins} minute{'s' if mins != 1 else ''}"
            self._mode_label.setText(f"\u23f1  {time_str} timed challenge")
            self._mode_label.show()
        else:
            self._mode_label.hide()
