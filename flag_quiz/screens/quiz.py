from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from flag_quiz.countries import ALL_NAMES

from flag_quiz.flag_label import FlagLabel
from flag_quiz.quiz_engine import (
    QuizSettings,
    QuizState,
    advance,
    create_quiz,
    submit_answer,
)

# Palette colours (Catppuccin Mocha-ish)
_BTN_DEFAULT = (
    "QPushButton { background-color: #313244; color: #cdd6f4; font-size: 15px;"
    " border: 2px solid #585b70; border-radius: 8px; padding: 10px 16px; text-align: left; }"
    "QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }"
)
_BTN_CORRECT = (
    "QPushButton { background-color: #a6e3a1; color: #1e1e2e; font-size: 15px;"
    " font-weight: bold; border: 2px solid #40a02b; border-radius: 8px;"
    " padding: 10px 16px; text-align: left; }"
)
_BTN_WRONG = (
    "QPushButton { background-color: #f38ba8; color: #1e1e2e; font-size: 15px;"
    " font-weight: bold; border: 2px solid #d20f39; border-radius: 8px;"
    " padding: 10px 16px; text-align: left; }"
)
_BTN_DIMMED = (
    "QPushButton { background-color: #1e1e2e; color: #585b70; font-size: 15px;"
    " border: 2px solid #313244; border-radius: 8px; padding: 10px 16px; text-align: left; }"
)


class QuizScreen(QWidget):
    finished = pyqtSignal(QuizState)   # emitted when quiz ends (finite mode)
    restart_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state: QuizState | None = None
        self._answered = False
        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_quiz(self, settings: QuizSettings) -> None:
        self._state = create_quiz(settings)
        self._answered = False
        self._load_question()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(32, 20, 32, 20)

        # Header row: score + restart
        header = QHBoxLayout()
        self._score_label = QLabel("Score: 0 / 0")
        self._score_label.setStyleSheet("font-size: 16px; color: #a6adc8;")
        header.addWidget(self._score_label)

        header.addStretch()

        self._question_label = QLabel("Question 1")
        self._question_label.setAlignment(Qt.AlignCenter)
        self._question_label.setStyleSheet("font-size: 14px; color: #6c7086;")
        header.addWidget(self._question_label)

        header.addStretch()

        restart_btn = QPushButton("↺  Restart")
        restart_btn.setFixedHeight(36)
        restart_btn.setStyleSheet(
            "QPushButton { background-color: #313244; color: #cdd6f4; font-size: 13px;"
            " border: 1px solid #585b70; border-radius: 6px; padding: 0 14px; }"
            "QPushButton:hover { background-color: #45475a; }"
        )
        restart_btn.clicked.connect(self.restart_requested)
        header.addWidget(restart_btn)

        root.addLayout(header)

        # Flag display
        flag_row = QHBoxLayout()
        flag_row.setAlignment(Qt.AlignCenter)
        self._flag_label = FlagLabel()
        flag_row.addWidget(self._flag_label)
        root.addLayout(flag_row)

        # Prompt
        self._prompt = QLabel("Which country does this flag belong to?")
        self._prompt.setAlignment(Qt.AlignCenter)
        self._prompt.setStyleSheet("font-size: 16px; color: #cdd6f4;")
        root.addWidget(self._prompt)

        # --- Answer area (stacked: page 0 = multiple choice, page 1 = dropdown) ---
        self._answer_stack = QStackedWidget()

        # -- Page 0: multiple choice buttons (2x2) --
        mc_widget = QWidget()
        mc_layout = QVBoxLayout(mc_widget)
        mc_layout.setSpacing(12)
        mc_layout.setContentsMargins(0, 0, 0, 0)

        self._choice_btns: list[QPushButton] = []
        grid_top = QHBoxLayout()
        grid_top.setSpacing(12)
        grid_bot = QHBoxLayout()
        grid_bot.setSpacing(12)

        for i in range(4):
            btn = QPushButton()
            btn.setMinimumHeight(56)
            btn.setStyleSheet(_BTN_DEFAULT)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self._on_choice_mc(idx))
            self._choice_btns.append(btn)
            (grid_top if i < 2 else grid_bot).addWidget(btn)

        mc_layout.addLayout(grid_top)
        mc_layout.addLayout(grid_bot)
        self._answer_stack.addWidget(mc_widget)  # index 0

        # -- Page 1: dropdown --
        dd_widget = QWidget()
        dd_layout = QVBoxLayout(dd_widget)
        dd_layout.setSpacing(12)
        dd_layout.setContentsMargins(0, 0, 0, 0)
        dd_layout.setAlignment(Qt.AlignCenter)

        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.setInsertPolicy(QComboBox.NoInsert)
        self._combo.setFixedHeight(44)
        self._combo.setStyleSheet(
            "QComboBox { background: #313244; color: #cdd6f4; border: 2px solid #585b70;"
            " border-radius: 8px; padding: 0 12px; font-size: 15px; }"
            "QComboBox:focus { border-color: #89b4fa; }"
            "QComboBox QAbstractItemView { background: #313244; color: #cdd6f4;"
            " selection-background-color: #45475a; border: 1px solid #585b70; }"
        )
        sorted_names = sorted(ALL_NAMES)
        self._combo.addItems(sorted_names)
        self._combo.lineEdit().setPlaceholderText("Type or search a country…")
        self._combo.setCurrentIndex(-1)
        # Enable auto-complete on the line edit
        from PyQt5.QtCore import Qt as _Qt
        self._combo.completer().setCompletionMode(
            self._combo.completer().PopupCompletion
        )
        self._combo.completer().setCaseSensitivity(_Qt.CaseInsensitive)
        dd_layout.addWidget(self._combo)

        self._submit_btn = QPushButton("Submit")
        self._submit_btn.setFixedHeight(48)
        self._submit_btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-size: 16px;"
            " font-weight: bold; border-radius: 8px; }"
            "QPushButton:hover { background-color: #b4d0fa; }"
            "QPushButton:disabled { background-color: #313244; color: #585b70; }"
        )
        self._submit_btn.clicked.connect(self._on_choice_dd)
        dd_layout.addWidget(self._submit_btn)

        # Feedback label (shown after answering in dropdown mode)
        self._dd_feedback = QLabel()
        self._dd_feedback.setAlignment(Qt.AlignCenter)
        self._dd_feedback.setWordWrap(True)
        self._dd_feedback.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        self._dd_feedback.hide()
        dd_layout.addWidget(self._dd_feedback)

        self._answer_stack.addWidget(dd_widget)   # index 1

        root.addWidget(self._answer_stack)

        # Next button (shared; hidden until answered wrong)
        self._next_btn = QPushButton("Next  →")
        self._next_btn.setFixedHeight(48)
        self._next_btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-size: 16px;"
            " font-weight: bold; border-radius: 8px; }"
            "QPushButton:hover { background-color: #b4d0fa; }"
        )
        self._next_btn.clicked.connect(self._on_next)
        self._next_btn.hide()
        root.addWidget(self._next_btn)

    # ------------------------------------------------------------------
    # Logic
    # ------------------------------------------------------------------

    def _load_question(self):
        if self._state is None:
            return

        self._answered = False
        self._next_btn.hide()

        q = self._state.current_question()
        if q is None:
            return

        # Header
        idx = self._state.current_index
        if self._state.settings.infinite:
            self._question_label.setText(f"Question {idx + 1}")
        else:
            total = self._state.settings.total_flags
            self._question_label.setText(f"Question {idx + 1} / {total}")

        self._update_score()

        # Flag
        self._flag_label.set_flag(q.country_code)

        # Answer widgets
        is_mc = self._state.settings.answer_mode == "multiple_choice"
        self._answer_stack.setCurrentIndex(0 if is_mc else 1)

        if is_mc:
            for i, btn in enumerate(self._choice_btns):
                btn.setText(f"  {chr(65 + i)}.  {q.choices[i]}")
                btn.setStyleSheet(_BTN_DEFAULT)
                btn.setEnabled(True)
        else:
            self._combo.setCurrentIndex(-1)
            self._combo.lineEdit().clear()
            self._combo.setEnabled(True)
            self._submit_btn.setEnabled(True)
            self._dd_feedback.hide()

    def _update_score(self):
        if self._state is None:
            return
        if self._state.settings.infinite:
            self._score_label.setText(
                f"Score: {self._state.correct} / {self._state.answered}"
            )
        else:
            self._score_label.setText(
                f"Score: {self._state.correct} / {self._state.answered}"
                f"  (of {self._state.settings.total_flags})"
            )

    def _on_choice_mc(self, idx: int):
        """Handle a multiple-choice button press."""
        if self._answered or self._state is None:
            return
        self._answered = True

        correct = submit_answer(self._state, idx)
        self._update_score()

        q = self._state.current_question()
        correct_idx = q.correct_index

        for i, btn in enumerate(self._choice_btns):
            btn.setEnabled(False)
            if i == correct_idx:
                btn.setStyleSheet(_BTN_CORRECT)
            elif i == idx and not correct:
                btn.setStyleSheet(_BTN_WRONG)
            else:
                btn.setStyleSheet(_BTN_DIMMED)

        if correct:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(600, self._on_next)
        else:
            self._next_btn.show()

    def _on_choice_dd(self):
        """Handle dropdown submit."""
        if self._answered or self._state is None:
            return
        selected = self._combo.currentText().strip()
        if not selected:
            return
        self._answered = True

        q = self._state.current_question()
        # Match case-insensitively
        is_correct = selected.lower() == q.country_name.lower()

        # Find the real index in choices so submit_answer works
        try:
            choice_idx = [c.lower() for c in q.choices].index(selected.lower())
        except ValueError:
            # Typed name not in choices list — treat as wrong with idx=-1
            choice_idx = -1

        # submit_answer needs a valid index; fake one if not in choices
        if choice_idx == -1:
            # Manually record result without going through submit_answer index check
            if is_correct:
                self._state.correct += 1
            self._state.answered += 1
        else:
            submit_answer(self._state, choice_idx)

        self._update_score()
        self._combo.setEnabled(False)
        self._submit_btn.setEnabled(False)

        if is_correct:
            self._dd_feedback.setText(f"✅  Correct! It's <b>{q.country_name}</b>.")
            self._dd_feedback.setStyleSheet("font-size: 14px; color: #a6e3a1;")
            self._dd_feedback.show()
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(800, self._on_next)
        else:
            self._dd_feedback.setText(
                f"❌  Wrong. The correct answer is <b>{q.country_name}</b>."
            )
            self._dd_feedback.setStyleSheet("font-size: 14px; color: #f38ba8;")
            self._dd_feedback.show()
            self._next_btn.show()

    def _on_next(self):
        if self._state is None:
            return

        advance(self._state)

        if self._state.is_finished:
            self.finished.emit(self._state)
            return

        self._load_question()
