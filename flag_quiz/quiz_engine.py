import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Question:
    country_code: str
    country_name: str
    choices: list[str]      # 4 names (used by multiple-choice mode)
    correct_index: int      # index into choices of the correct answer


@dataclass
class QuizSettings:
    quiz_mode: str = "finite"       # "finite" | "infinite" | "timed"
    total_flags: int = 30           # finite mode only
    timer_seconds: int = 120        # timed mode only
    answer_mode: str = "dropdown"   # "multiple_choice" | "dropdown"
    dataset_id: str = "countries"


@dataclass
class QuizState:
    settings: QuizSettings
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    correct: int = 0
    answered: int = 0

    _deck: list[dict] = field(default_factory=list)
    _used_codes: set[str] = field(default_factory=set)

    @property
    def is_endless(self) -> bool:
        return self.settings.quiz_mode in ("infinite", "timed")

    @property
    def is_finished(self) -> bool:
        if self.is_endless:
            return False
        return self.current_index >= self.settings.total_flags

    def current_question(self) -> Optional[Question]:
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None


def _make_deck(entries: list[dict]) -> list[dict]:
    deck = list(entries)
    random.shuffle(deck)
    return deck


def _build_question(country: dict, all_names: list[str]) -> Question:
    wrong_pool = [n for n in all_names if n != country["name"]]
    wrong = random.sample(wrong_pool, min(3, len(wrong_pool)))
    choices = wrong + [country["name"]]
    random.shuffle(choices)
    correct_index = choices.index(country["name"])
    return Question(
        country_code=country["code"],
        country_name=country["name"],
        choices=choices,
        correct_index=correct_index,
    )


def create_quiz(settings: QuizSettings) -> QuizState:
    from flag_quiz.datasets import ALL_DATASETS, get_available_datasets

    dataset = ALL_DATASETS.get(settings.dataset_id)
    if dataset is None or not dataset.is_available():
        available = get_available_datasets()
        if not available:
            raise RuntimeError("No flag datasets available. Run the download script first.")
        dataset = available[0]

    entries = dataset.entries
    all_names = dataset.names

    state = QuizState(settings=settings)
    deck = _make_deck(entries)

    if settings.quiz_mode == "finite":
        count = min(settings.total_flags, len(entries))
    else:
        count = len(entries)  # pre-generate one full cycle for endless modes

    for i in range(count):
        country = deck[i]
        state.questions.append(_build_question(country, all_names))
        state._used_codes.add(country["code"])

    state._deck = []
    return state


def ensure_next_question(state: QuizState) -> None:
    """Generate the next question on demand (endless modes only)."""
    if not state.is_endless:
        return
    if state.current_index < len(state.questions):
        return

    from flag_quiz.datasets import ALL_DATASETS

    dataset = ALL_DATASETS.get(state.settings.dataset_id)
    if dataset is None:
        return

    if not state._deck:
        state._deck = _make_deck(dataset.entries)
        state._used_codes.clear()

    country = state._deck.pop(0)
    state.questions.append(_build_question(country, dataset.names))
    state._used_codes.add(country["code"])


def submit_answer(state: QuizState, choice_index: int) -> bool:
    """Record a multiple-choice answer. Returns True if correct."""
    q = state.current_question()
    if q is None:
        return False
    correct = choice_index == q.correct_index
    if correct:
        state.correct += 1
    state.answered += 1
    return correct


def advance(state: QuizState) -> None:
    """Move to the next question, generating it first in endless modes."""
    state.current_index += 1
    ensure_next_question(state)


def advance(state: QuizState) -> None:
    """Move to the next question, generating it first in infinite mode."""
    state.current_index += 1
    ensure_next_question(state)
