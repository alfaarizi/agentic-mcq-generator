"""AugmenterAgent for autonomous quiz augmentation with additional questions."""

from typing import Dict, Any, List, Optional, Callable


from ..models import Quiz, Question
from .agent import Agent
from .schemas import (
    QuizContext, TopicCoverage
)
from .tools import extract_quiz_context, analyze_topic_coverage, generate_questions, validate_questions


class AugmenterAgent(Agent):
    """Autonomous agent for augmenting existing quizzes with additional questions."""
    
    def __init__(
        self,
        model: str = "google/gemini-2.5-flash",
        tools: Optional[List[Callable]] = None
    ) -> None:
        default_tools = [extract_quiz_context, analyze_topic_coverage, generate_questions, validate_questions]
        super().__init__(model, tools=tools or default_tools)
    
    
    def augment(
        self,
        quiz: Quiz,
        target_count: int = 15
    ) -> List[Question]:
        """Augment quiz with additional questions matching existing style."""
        
        quiz_context: QuizContext = extract_quiz_context(quiz, agent=self)
        
        topic_coverage: TopicCoverage = analyze_topic_coverage(quiz, quiz_context, agent=self, target_count=target_count)
        
        new_questions, _ = generate_questions(
            topic=quiz.topic,
            samples=quiz.questions[:5], # Use first 5 as samples
            count=target_count,
            quiz_context=quiz_context,
            topic_coverage=topic_coverage,
            agent=self,
            suggested_time_limit=-1 # Preserve existing time limit
        )
        
        validated_questions: List[Question] = validate_questions(
            new_questions=new_questions,
            existing_questions=quiz.questions,
            quiz_context=quiz_context,
            agent=self
        )
        
        return validated_questions

