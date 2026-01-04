"""Quiz storage and management."""

from pathlib import Path
from typing import List, Optional
from .models import Quiz, Question
from .parser import QuizParser


class QuizStorage:
    """Manage quiz storage."""
    
    def __init__(self, storage_dir: str = "quizzes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    # Read operations
    def get_quizzes(self) -> List[Quiz]:
        """Get all quizzes from markdown files."""
        return [quiz
            for file_path in self.storage_dir.glob("*.md") 
            for quiz in QuizParser.from_file(str(file_path))
        ]

    def get_topics(self) -> List[str]:
        """Get all topic names."""
        return [quiz.topic for quiz in self.get_quizzes()]

    def get_quiz(self, slug: str) -> Optional[Quiz]:
        """Get quiz by slug."""
        for quiz in self.get_quizzes():
            if quiz.slug == slug:
                return quiz
        return None

    # Write operations
    def create_quiz(self, topic: str, questions: List[Question]) -> Quiz:
        """Create and save new quiz."""
        quiz = Quiz(topic=topic, questions=questions)
        self.save_quiz(quiz)
        return quiz

    def add_questions(self, quiz: Quiz, questions: List[Question]) -> None:
        """Add questions to quiz and save."""
        quiz.questions.extend(questions)
        self.save_quiz(quiz)

    def save_quiz(self, quiz: Quiz) -> str:
        """Save quiz to markdown file."""
        filename = f"{quiz.topic.replace(' ', '_').lower()}.md"
        file_path = self.storage_dir / filename

        lines = [f"<{quiz.topic}>", ""]
        for question in quiz.questions:
            lines.append(question.text)
            for choice in question.original_choices:
                prefix = ">" if choice.is_correct else "-"
                lines.append(f"{prefix} {choice.text}")
            lines.append("")
        lines.append(f"</{quiz.topic}>")

        file_path.write_text("\n".join(lines), encoding='utf-8')
        return str(file_path)
