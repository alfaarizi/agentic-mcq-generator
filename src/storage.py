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


    def get_quiz(self, slug: str) -> Optional[Quiz]:
        """Get quiz by slug."""
        for quiz in self.get_quizzes():
            if quiz.slug == slug:
                return quiz
        return None


    # Write operations
    def save_quiz(self, quiz: Quiz) -> str:
        """Save quiz to markdown file."""
        filename = f"{quiz.topic.replace(' ', '_').lower()}.md"
        file_path = self.storage_dir / filename

        # Format opening tag: include time limit if present
        minutes = quiz.time_limit // 60 if quiz.time_limit > 0 else None
        opening_tag = f"<{quiz.topic}:{minutes}>" if minutes else f"<{quiz.topic}>"
        
        lines = [opening_tag, ""]
        for question in quiz.questions:
            lines.append(question.text)
            for choice in question.original_choices:
                prefix = ">" if choice.is_correct else "-"
                lines.append(f"{prefix} {choice.text}")
            lines.append("")
        lines.append(f"</{quiz.topic}>")

        file_path.write_text("\n".join(lines), encoding='utf-8')
        return str(file_path)


    def delete_quizzes(self) -> int:
        """Delete all quiz files except those in examples directory.
        
        Returns:
            int: Number of files deleted
        """
        deleted_count = 0
        for file_path in self.storage_dir.glob("*.md"):
            file_path.unlink()
            deleted_count += 1
        return deleted_count
