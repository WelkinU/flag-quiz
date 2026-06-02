from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QLabel,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QFrame,
)

from flag_quiz.quiz_engine import QuizSettings


class StartScreen(QWidget):
    quiz_requested = pyqtSignal(QuizSettings)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(24)
        root.setContentsMargins(60, 40, 60, 40)

        # Title
        title = QLabel("🌍  Flag Quiz")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 42px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(title)

        subtitle = QLabel("How well do you know the world's flags?")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #a6adc8;")
        root.addWidget(subtitle)

        root.addSpacing(16)

        # Settings card
        card = QFrame()
        card.setObjectName("settingsCard")
        card.setStyleSheet(
            "QFrame#settingsCard { background-color: #1e1e2e; border: 1px solid #444466;"
            " border-radius: 12px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 24, 32, 24)

        settings_label = QLabel("Settings")
        settings_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #89b4fa; border: none;"
        )
        card_layout.addWidget(settings_label)

        # Answer mode row — label + radios on one line
        mode_row = QHBoxLayout()
        mode_row.setSpacing(20)

        mode_label = QLabel("Answer mode:")
        mode_label.setStyleSheet("font-size: 14px; color: #a6adc8; border: none;")
        mode_row.addWidget(mode_label)

        _radio_style = (
            "QRadioButton { font-size: 14px; color: #cdd6f4; spacing: 8px; border: none; }"
            "QRadioButton::indicator { width: 16px; height: 16px; }"
        )

        self._rb_dropdown = QRadioButton("Dropdown")
        self._rb_dropdown.setStyleSheet(_radio_style)
        self._rb_dropdown.setChecked(True)
        mode_row.addWidget(self._rb_dropdown)

        self._rb_mc = QRadioButton("Multiple choice  (4 options)")
        self._rb_mc.setStyleSheet(_radio_style)
        mode_row.addWidget(self._rb_mc)

        mode_row.addStretch()

        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self._rb_dropdown, 0)
        self._mode_group.addButton(self._rb_mc, 1)
        self._mode_group.buttonToggled.connect(lambda *_: self._update_info())

        card_layout.addLayout(mode_row)

        # Number of flags row
        flags_row = QHBoxLayout()
        flags_row.setSpacing(12)

        num_label = QLabel("Number of flags:")
        num_label.setStyleSheet("font-size: 14px; color: #cdd6f4;")
        flags_row.addWidget(num_label)

        self._spin = QSpinBox()
        self._spin.setRange(1, 195)
        self._spin.setValue(30)
        self._spin.setFixedWidth(80)
        self._spin.setStyleSheet(
            "QSpinBox { background: #313244; color: #cdd6f4; border: 1px solid #585b70;"
            " border-radius: 6px; padding: 4px 8px; font-size: 14px; }"
            "QSpinBox::up-button, QSpinBox::down-button { width: 20px; }"
        )
        flags_row.addWidget(self._spin)

        flags_row.addStretch()

        self._infinite_cb = QCheckBox("Infinite mode")
        self._infinite_cb.setStyleSheet(
            "QCheckBox { font-size: 14px; color: #cdd6f4; spacing: 8px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; }"
        )
        self._infinite_cb.toggled.connect(self._on_infinite_toggled)
        flags_row.addWidget(self._infinite_cb)

        card_layout.addLayout(flags_row)

        # Info blurb
        self._info = QLabel("You will be shown <b>30</b> flags. You type the country name.")
        self._info.setWordWrap(True)
        self._info.setStyleSheet("font-size: 13px; color: #6c7086; border: none;")
        card_layout.addWidget(self._info)

        self._spin.valueChanged.connect(self._update_info)

        root.addWidget(card)
        root.addSpacing(8)

        # Start button
        self._start_btn = QPushButton("Start Quiz")
        self._start_btn.setFixedHeight(52)
        self._start_btn.setStyleSheet(
            "QPushButton { background-color: #89b4fa; color: #1e1e2e; font-size: 18px;"
            " font-weight: bold; border-radius: 10px; }"
            "QPushButton:hover { background-color: #b4d0fa; }"
            "QPushButton:pressed { background-color: #74a8e8; }"
        )
        self._start_btn.clicked.connect(self._on_start)
        root.addWidget(self._start_btn)

    def _on_infinite_toggled(self, checked: bool):
        self._spin.setEnabled(not checked)
        self._update_info()

    def _update_info(self):
        mode_str = "type the country name" if self._rb_dropdown.isChecked() else "pick from 4 choices"
        if self._infinite_cb.isChecked():
            self._info.setText(
                f"Infinite mode: cycle through <b>all flags</b>, reshuffling when exhausted. You {mode_str}."
            )
        else:
            n = self._spin.value()
            self._info.setText(
                f"You will be shown <b>{n}</b> flag{'s' if n != 1 else ''}."
                f" You {mode_str}."
            )

    def _on_start(self):
        settings = QuizSettings(
            infinite=self._infinite_cb.isChecked(),
            total_flags=self._spin.value(),
            answer_mode="multiple_choice" if self._rb_mc.isChecked() else "dropdown",
        )
        self.quiz_requested.emit(settings)
