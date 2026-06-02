import random
from dataclasses import dataclass, field
from typing import Optional

from flag_quiz.countries import COUNTRIES


@dataclass
class Question:
    country_code: str
    country_name: str
    choices: list[str]          # 4 country names
    correct_index: int          # index into choices of the right answer


@dataclass
class QuizSettings:
    infinite: bool = False
    total_flags: int = 30       # ignored when infinite=True
    answer_mode: str = "dropdown"  # "multiple_choice" or "dropdown"


@dataclass
class QuizState:
    settings: QuizSettings
    questions: list[Question] = field(default_factory=list)
    current_index: int = 0
    correct: int = 0
    answered: int = 0           # questions the user has submitted an answer for

    # For infinite cycling — tracks which deck we're on
    _deck: list[dict] = field(default_factory=list)
    _used_codes: set[str] = field(default_factory=set)

    @property
    def total(self) -> int:
        if self.settings.infinite:
            return self.answered  # grows as we go
        return self.settings.total_flags

    @property
    def is_finished(self) -> bool:
        if self.settings.infinite:
            return False
        return self.current_index >= self.settings.total_flags

    def current_question(self) -> Optional[Question]:
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None


def _make_deck(exclude_codes: set[str] | None = None) -> list[dict]:
    """Return all countries shuffled, optionally excluding codes."""
    pool = [c for c in COUNTRIES if exclude_codes is None or c["code"] not in exclude_codes]
    random.shuffle(pool)
    return pool


def _build_question(country: dict, all_names: list[str]) -> Question:
    wrong_pool = [n for n in all_names if n != country["name"]]
    wrong = random.sample(wrong_pool, 3)
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
    from flag_quiz.countries import ALL_NAMES

    state = QuizState(settings=settings)
    deck = _make_deck()
    state._deck = deck

    count = len(COUNTRIES) if settings.infinite else min(settings.total_flags, len(COUNTRIES))
    for i in range(count):
        country = deck[i % len(deck)]
        state.questions.append(_build_question(country, ALL_NAMES))
        state._used_codes.add(country["code"])

    return state


def ensure_next_question(state: QuizState) -> None:
    """In infinite mode, generate the next question on demand if needed."""
    if not state.settings.infinite:
        return
    if state.current_index < len(state.questions):
        return

    from flag_quiz.countries import ALL_NAMES

    # Refill deck if exhausted
    if not state._deck:
        state._deck = _make_deck()
        state._used_codes.clear()

    country = state._deck.pop(0)
    state.questions.append(_build_question(country, ALL_NAMES))
    state._used_codes.add(country["code"])


def submit_answer(state: QuizState, choice_index: int) -> bool:
    """Record an answer. Returns True if correct."""
    q = state.current_question()
    if q is None:
        return False
    correct = choice_index == q.correct_index
    if correct:
        state.correct += 1
    state.answered += 1
    return correct


def advance(state: QuizState) -> None:
    """Move to the next question, generating it first in infinite mode."""
    state.current_index += 1
    ensure_next_question(state)
