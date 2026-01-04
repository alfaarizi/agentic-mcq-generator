"""Data models for quiz questions and topics."""

from dataclasses import dataclass, field
from typing import List
import random
import re


@dataclass
class Choice:
    """Represents a single answer choice."""

    text: str
    is_correct: bool

    def __hash__(self):
        return hash((self.text, self.is_correct))


@dataclass
class Question:
    """Represents a single quiz question."""

    text: str
    choices: List[Choice]
    original_choices: List[Choice] = field(default_factory=list)

    def __post_init__(self):
        """Store original order and shuffle choices."""
        if not self.original_choices:
            self.original_choices = self.choices.copy()
        random.shuffle(self.choices)

    @property
    def correct_choices(self) -> List[Choice]:
        """Get all correct choices."""
        return [c for c in self.original_choices if c.is_correct]


@dataclass
class Quiz:
    """Represents a quiz topic with multiple questions."""

    topic: str
    questions: List[Question]
    time_limit: int = 0  # seconds, 0 = no limit
    file_path: str = ""

    @property
    def slug(self) -> str:
        """Generate URL-friendly slug from topic."""
        return re.sub(r'[^\w-]+', '-', self.topic.lower()).strip('-')

    def shuffle_questions(self):
        """Shuffle the order of questions."""
        random.shuffle(self.questions)

    @property
    def total_questions(self) -> int:
        """Get total number of questions."""
        return len(self.questions)
