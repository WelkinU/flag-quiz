from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QLabel,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QFrame,
)

from flag_quiz.datasets import get_available_datasets
from flag_quiz.quiz_engine import QuizSettings

_RADIO_STYLE = (
    "QRadioButton { font-size: 14px; color: #cdd6f4; spacing: 8px; border: none; }"
    "QRadioButton::indicator { width: 16px; height: 16px; }"
)
_SPIN_STYLE = (
    "QSpinBox { background: #313244; color: #cdd6f4; border: 1px solid #585b70;"
    " border-radius: 6px; padding: 2px 8px; font-size: 14px; }"
    "QSpinBox::up-button, QSpinBox::down-button { width: 18px; }"
)
_MUTED_LABEL_STYLE = "font-size: 14px; color: #a6adc8; border: none;"


def _muted(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(_MUTED_LABEL_STYLE)
    return lbl


class StartScreen(QWidget):
    quiz_requested = pyqtSignal(QuizSettings)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._available_datasets = get_available_datasets()
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

        root.addSpacing(8)

        # ── Settings card ──────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("settingsCard")
        card.setStyleSheet(
            "QFrame#settingsCard { background-color: #1e1e2e; border: 1px solid #444466;"
            " border-radius: 12px; }"
        )
        cl = QVBoxLayout(card)
        cl.setSpacing(14)
        cl.setContentsMargins(32, 24, 32, 24)

        settings_lbl = QLabel("Settings")
        settings_lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #89b4fa; border: none;"
        )
        cl.addWidget(settings_lbl)

        # Dataset row
        ds_row = QHBoxLayout()
        ds_row.setSpacing(12)
        ds_lbl = _muted("Dataset:")
        ds_lbl.setFixedWidth(110)
        ds_row.addWidget(ds_lbl)

        self._dataset_combo = QComboBox()
        self._dataset_combo.setFixedHeight(36)
        self._dataset_combo.setStyleSheet(
            "QComboBox { background: #313244; color: #cdd6f4; border: 1px solid #585b70;"
            " border-radius: 6px; padding: 0 12px; font-size: 14px; }"
            "QComboBox::drop-down { width: 24px; }"
            "QComboBox QAbstractItemView { background: #313244; color: #cdd6f4;"
            " selection-background-color: #45475a; border: 1px solid #585b70; }"
        )
        if self._available_datasets:
            for ds in self._available_datasets:
                self._dataset_combo.addItem(ds.label, ds.id)
        else:
            self._dataset_combo.addItem("No datasets found — run setup.bat first", "")
            self._dataset_combo.setEnabled(False)
        self._dataset_combo.currentIndexChanged.connect(self._on_dataset_changed)
        ds_row.addWidget(self._dataset_combo)
        ds_row.addStretch()
        cl.addLayout(ds_row)

        # Answer mode row
        am_row = QHBoxLayout()
        am_row.setSpacing(20)
        am_lbl = _muted("Answer mode:")
        am_lbl.setFixedWidth(110)
        am_row.addWidget(am_lbl)

        self._rb_dropdown = QRadioButton("Dropdown")
        self._rb_dropdown.setStyleSheet(_RADIO_STYLE)
        self._rb_dropdown.setChecked(True)
        am_row.addWidget(self._rb_dropdown)

        self._rb_mc = QRadioButton("Multiple choice  (4 options)")
        self._rb_mc.setStyleSheet(_RADIO_STYLE)
        am_row.addWidget(self._rb_mc)
        am_row.addStretch()

        self._answer_mode_group = QButtonGroup(self)
        self._answer_mode_group.addButton(self._rb_dropdown, 0)
        self._answer_mode_group.addButton(self._rb_mc, 1)
        self._answer_mode_group.buttonToggled.connect(lambda *_: self._update_info())
        cl.addLayout(am_row)

        # Quiz mode section
        qm_lbl = _muted("Quiz mode:")
        cl.addWidget(qm_lbl)

        self._quiz_mode_group = QButtonGroup(self)

        # Finite row
        fin_row = QHBoxLayout()
        fin_row.setContentsMargins(20, 0, 0, 0)
        fin_row.setSpacing(10)
        self._rb_finite = QRadioButton("Finite")
        self._rb_finite.setStyleSheet(_RADIO_STYLE)
        self._rb_finite.setChecked(True)
        fin_row.addWidget(self._rb_finite)
        self._flags_spin = QSpinBox()
        self._flags_spin.setRange(1, 194)
        self._flags_spin.setValue(30)
        self._flags_spin.setFixedWidth(72)
        self._flags_spin.setStyleSheet(_SPIN_STYLE)
        self._flags_spin.valueChanged.connect(self._update_info)
        fin_row.addWidget(self._flags_spin)
        fin_row.addWidget(_muted("flags"))
        fin_row.addStretch()
        cl.addLayout(fin_row)

        # Infinite row
        inf_row = QHBoxLayout()
        inf_row.setContentsMargins(20, 0, 0, 0)
        self._rb_infinite = QRadioButton("Infinite  (cycle through all flags)")
        self._rb_infinite.setStyleSheet(_RADIO_STYLE)
        inf_row.addWidget(self._rb_infinite)
        inf_row.addStretch()
        cl.addLayout(inf_row)

        # Timed row
        tim_row = QHBoxLayout()
        tim_row.setContentsMargins(20, 0, 0, 0)
        tim_row.setSpacing(10)
        self._rb_timed = QRadioButton("Timed")
        self._rb_timed.setStyleSheet(_RADIO_STYLE)
        tim_row.addWidget(self._rb_timed)
        self._minutes_spin = QSpinBox()
        self._minutes_spin.setRange(1, 60)
        self._minutes_spin.setValue(2)
        self._minutes_spin.setFixedWidth(64)
        self._minutes_spin.setStyleSheet(_SPIN_STYLE)
        self._minutes_spin.setEnabled(False)
        self._minutes_spin.valueChanged.connect(self._update_info)
        tim_row.addWidget(self._minutes_spin)
        tim_row.addWidget(_muted("minutes"))
        tim_row.addStretch()
        cl.addLayout(tim_row)

        self._quiz_mode_group.addButton(self._rb_finite, 0)
        self._quiz_mode_group.addButton(self._rb_infinite, 1)
        self._quiz_mode_group.addButton(self._rb_timed, 2)
        self._quiz_mode_group.buttonToggled.connect(lambda *_: self._on_quiz_mode_changed())

        # Info blurb
        self._info = QLabel()
        self._info.setWordWrap(True)
        self._info.setStyleSheet("font-size: 13px; color: #6c7086; border: none;")
        cl.addWidget(self._info)

        self._update_info()

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
            "QPushButton:disabled { background-color: #313244; color: #585b70; }"
        )
        self._start_btn.setEnabled(bool(self._available_datasets))
        self._start_btn.clicked.connect(self._on_start)
        root.addWidget(self._start_btn)

        # Initialise flags_spin max from first dataset
        self._on_dataset_changed()

    def _on_dataset_changed(self):
        from flag_quiz.datasets import ALL_DATASETS

        dataset_id = self._dataset_combo.currentData()
        if dataset_id:
            dataset = ALL_DATASETS.get(dataset_id)
            if dataset:
                max_f = len(dataset.entries)
                self._flags_spin.setMaximum(max_f)
                if self._flags_spin.value() > max_f:
                    self._flags_spin.setValue(min(30, max_f))
        self._update_info()

    def _on_quiz_mode_changed(self):
        self._flags_spin.setEnabled(self._rb_finite.isChecked())
        self._minutes_spin.setEnabled(self._rb_timed.isChecked())
        self._update_info()

    def _update_info(self):
        mode_str = (
            "type the name" if self._rb_dropdown.isChecked() else "pick from 4 choices"
        )
        if self._rb_finite.isChecked():
            n = self._flags_spin.value()
            self._info.setText(
                f"<b>{n}</b> flag{'s' if n != 1 else ''} — {mode_str}."
            )
        elif self._rb_infinite.isChecked():
            self._info.setText(f"Cycle through all flags endlessly — {mode_str}.")
        else:
            mins = self._minutes_spin.value()
            self._info.setText(
                f"How many flags can you get in <b>{mins} minute{'s' if mins != 1 else ''}</b>?"
                f"  {mode_str}."
            )

    def _on_start(self):
        dataset_id = self._dataset_combo.currentData() or "countries"

        if self._rb_finite.isChecked():
            quiz_mode = "finite"
        elif self._rb_infinite.isChecked():
            quiz_mode = "infinite"
        else:
            quiz_mode = "timed"

        settings = QuizSettings(
            quiz_mode=quiz_mode,
            total_flags=self._flags_spin.value(),
            timer_seconds=self._minutes_spin.value() * 60,
            answer_mode="multiple_choice" if self._rb_mc.isChecked() else "dropdown",
            dataset_id=dataset_id,
        )
        self.quiz_requested.emit(settings)

