import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget

from flag_quiz.quiz_engine import QuizSettings, QuizState
from flag_quiz.screens.start import StartScreen
from flag_quiz.screens.quiz import QuizScreen
from flag_quiz.screens.results import ResultsScreen

_DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #181825;
    color: #cdd6f4;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
}
QScrollBar { background: #1e1e2e; }
"""

PAGE_START = 0
PAGE_QUIZ = 1
PAGE_RESULTS = 2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flag Quiz")
        self.setMinimumSize(680, 700)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._start_screen = StartScreen()
        self._quiz_screen = QuizScreen()
        self._results_screen = ResultsScreen()

        self._stack.addWidget(self._start_screen)   # PAGE_START = 0
        self._stack.addWidget(self._quiz_screen)    # PAGE_QUIZ  = 1
        self._stack.addWidget(self._results_screen) # PAGE_RESULTS = 2

        # Wire signals
        self._start_screen.quiz_requested.connect(self._on_quiz_requested)
        self._quiz_screen.finished.connect(self._on_quiz_finished)
        self._quiz_screen.restart_requested.connect(self._go_to_start)
        self._results_screen.play_again.connect(self._go_to_start)
        self._results_screen.quit_requested.connect(self.close)

        self._stack.setCurrentIndex(PAGE_START)

    def _on_quiz_requested(self, settings: QuizSettings):
        self._quiz_screen.start_quiz(settings)
        self._stack.setCurrentIndex(PAGE_QUIZ)

    def _on_quiz_finished(self, state: QuizState):
        self._results_screen.show_results(state)
        self._stack.setCurrentIndex(PAGE_RESULTS)

    def _go_to_start(self):
        self._stack.setCurrentIndex(PAGE_START)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(_DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
