"""Parser for markdown quiz files."""

import re
from typing import List
from .models import Quiz, Question, Choice


class QuizParser:
    """Parse markdown quiz files."""

    @staticmethod
    def from_file(file_path: str) -> List[Quiz]:
        """Parse quizzes from file path."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return QuizParser.from_string(f.read(), source=file_path)

    @staticmethod
    def from_upload(uploaded_file) -> List[Quiz]:
        """Parse quizzes from Streamlit upload."""
        content = uploaded_file.getvalue().decode('utf-8')
        return QuizParser.from_string(content, source=uploaded_file.name)

    @staticmethod
    def from_string(content: str, source: str = "") -> List[Quiz]:
        """Parse quizzes from markdown string."""
        quizzes = []
        pattern = r'<([^>]+)>(.*?)</\1>'

        for match in re.finditer(pattern, content, re.DOTALL):
            topic = match.group(1).strip()
            questions = parse_questions(match.group(2).strip())

            if questions:
                quiz = Quiz(topic=topic, questions=questions, file_path=source)
                quizzes.append(quiz)

        return quizzes


def parse_questions(content: str) -> List[Question]:
    """Parse questions from string content. Reusable across quiz and AI parsing."""
    questions = []
    current_question = None
    current_choices = []

    for line in content.split('\n'):
        line = line.strip()

        if not line:
            if current_question and current_choices:
                questions.append(Question(current_question, current_choices))
                current_question = None
                current_choices = []
            continue

        if line.startswith(('-', '>')):
            is_correct = line.startswith('>')
            choice_text = line[1:].strip()
            if current_question:
                current_choices.append(Choice(choice_text, is_correct))
        elif line.startswith('Q:'):
            # Handle "Q: question" format from AI
            if current_question and current_choices:
                questions.append(Question(current_question, current_choices))
                current_choices = []
            current_question = line[2:].strip()
        else:
            # Regular question format
            if current_question and current_choices:
                questions.append(Question(current_question, current_choices))
                current_choices = []
            current_question = line

    if current_question and current_choices:
        questions.append(Question(current_question, current_choices))

    return questions
