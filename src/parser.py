"""Parser for markdown quiz files."""

import re
from typing import List, Optional, Tuple
from .models import Quiz, Question, Choice


class QuizParser:
    """Parse quizzes from markdown string."""

    # ============================================
    # Helper Functions
    # ============================================

    @staticmethod
    def _parse_topic(opening_tag_content: str) -> Optional[Tuple[str, Optional[int]]]:
        """Parse opening tag to extract topic and optional time limit.

        Args:
            opening_tag_content: Content inside opening tag (e.g., "Topic:5" or "Math")
        
        Returns:
            (topic, minutes) or None if invalid
        """        
        # Pattern: topic name, optional colon+number, optional whitespace
        # Matches: "Topic", "Topic:5", "Topic : 5", "Topic:  5", "Topic 5" (non-timed), etc.
        # Rejects: "Topic:a" (non-numeric time), invalid formats
        match = re.match(r'^([^:>]+?)(?::\s*(\d+))?\s*$', opening_tag_content.strip(), re.IGNORECASE)
        if not match:
            return None
        
        topic = match.group(1).strip()
        time_str = match.group(2)
        
        # If colon present, number must exist (regex ensures this)
        minutes = int(time_str) if time_str else None
        return (topic, minutes)
    

    @staticmethod
    def _find_opening_tag(content: str, start_pos: int) -> Optional[re.Match]:
        """Find the next opening tag.
        
        Args:
            content: Full markdown content to search
            start_pos: Character position to start searching from
        """
        pattern = r'<\s*([^>]+?)\s*>'
        return re.search(pattern, content[start_pos:], re.IGNORECASE)


    @staticmethod
    def _find_closing_tag(content: str, start_pos: int, topic: str, is_timed: bool) -> Optional[re.Match]:
        """Find matching closing tag
        
        Args:
            content: Full markdown content to search
            start_pos: Character position to start searching from
            topic: Topic name (e.g., "Topic" or "Topic 5")
            is_timed: Whether the quiz is timed
        """
        pattern = r'<\s*/\s*([^>]+?)\s*>'
        norm_topic = topic.strip().lower()
        
        for match in re.finditer(pattern, content[start_pos:], re.IGNORECASE):
            closing = match.group(1).strip()
            if not (parsed := QuizParser._parse_topic(closing)):
                continue
            
            closing_topic, closing_minutes = parsed
            norm_closing_topic = closing_topic.strip().lower()
            
            # Non-timed quizzes: exact match
            if not is_timed and norm_closing_topic == norm_topic:
                return match
            
            # Timed quizzes: closing must have topic and no time
            if norm_closing_topic == norm_topic and closing_minutes is None:
                return match

        return None


    @staticmethod
    def _parse_quiz(content: str, start_pos: int, source_file: str = "") -> Optional[Tuple[Optional[Quiz], int]]:
        """Process a single quiz tag to extract quiz
        
        Args:
            content: Full markdown content to parse
            start_pos: Character position to start searching from
            source_file: Source file path for the quiz (optional)

        Returns:
            (Quiz, next_position) if valid quiz found
            (None, next_position) if tag found but invalid
            None if no opening tag found
        """
        # Step 1: Find the next opening tag from current position
        if not (opening_match := QuizParser._find_opening_tag(content, start_pos)):
            return None  # No more opening tags found, stop parsing
        
        opening_tag_end = start_pos + opening_match.end()
        opening_tag_content = opening_match.group(1)
        
        # Step 2: Parse and validate the opening tag
        if not (parsed := QuizParser._parse_topic(opening_tag_content)):
            return (None, opening_tag_end) # Invalid tag format, continue parsing
        
        topic, minutes = parsed
        is_timed = minutes is not None
        
        # Step 3: Find the matching closing tag
        if not (closing_match := QuizParser._find_closing_tag(content, opening_tag_end, topic, is_timed)):
            return (None, opening_tag_end) # No matching closing tag, continue parsing
        
        # Step 4: Extract and parse quiz content (between opening and closing tags)
        quiz_content = content[opening_tag_end:opening_tag_end + closing_match.start()].strip()
        questions: List[Question] = parse_questions(quiz_content)
        
        if not questions:
            return (None, opening_tag_end + closing_match.end()) # No questions found, skip continue parsing
        
        # Step 5: Return Quiz and position after closing tag
        quiz = Quiz(
            topic=topic,
            questions=questions, 
            time_limit=minutes * 60 if minutes is not None else 0, 
            file_path=source_file
        )
        return (quiz, opening_tag_end + closing_match.end())


    # ============================================
    # Parser Functions
    # ============================================

    @staticmethod
    def from_file(file_path: str) -> List[Quiz]:
        """Parse quizzes from file path."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return QuizParser.from_string(f.read(), source_file=file_path)


    @staticmethod
    def from_string(content: str, source_file: str = "") -> List[Quiz]:
        """Parse quizzes from markdown string."""
        quizzes: List[Quiz] = []
        
        pos = 0
        while pos < len(content):
            result = QuizParser._parse_quiz(content, pos, source_file)
            if not result:
                break  # No more opening tags found
            
            quiz, next_pos = result
            if quiz:
                quizzes.append(quiz)
            pos = next_pos

        return quizzes


def parse_questions(content: str) -> List[Question]:
    """Parse questions from string content.
    
    Args:
        content: Markdown string containing quiz definitions
    """
    questions = []
    current_question = None
    current_choices = []

    for line in content.split('\n'):
        line = line.strip()
        if not line: # Ignore blank lines - don't finalize questions on blank lines
            continue

        # Question Choices
        if line.startswith(('-', '>')):
            is_correct = line.startswith('>')
            choice_text = line[1:].strip()
            if current_question:
                current_choices.append(Choice(choice_text, is_correct))
        else:
            # Question text - finalize previous question if exists
            if current_question and current_choices:
                questions.append(Question(current_question, current_choices))
                current_choices = []
            current_question = line

    # Finalize last question if exists
    if current_question and current_choices:
        questions.append(Question(current_question, current_choices))

    return questions
