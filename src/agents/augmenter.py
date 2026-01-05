"""AugmenterAgent for autonomous quiz augmentation with additional questions."""

from typing import Dict, Any, List, Optional, Callable


from ..models import Quiz, Question
from .agent import Agent
from .schemas import (
    QuizAnalysis, CoverageAnalysis, QuestionValidation
)
from .tools import analyze_quiz, analyze_coverage, generate_questions, validate_questions


class AugmenterAgent(Agent):
    """Autonomous agent for augmenting existing quizzes with additional questions."""
    
    def __init__(
        self,
        model: str = "google/gemini-2.5-flash",
        tools: Optional[List[Callable]] = None
    ) -> None:
        default_tools = [analyze_quiz, analyze_coverage, generate_questions, validate_questions]
        super().__init__(model, tools=tools or default_tools)
    
    
    def augment(
        self,
        quiz: Quiz,
        target_count: int = 15
    ) -> List[Question]:
        """Augment quiz with additional questions matching existing style."""
        
        quiz_analysis: QuizAnalysis = analyze_quiz(quiz, agent=self)
        
        coverage_analysis: CoverageAnalysis = analyze_coverage(quiz, quiz_analysis, agent=self, target_count=target_count)
        
        new_questions: List[Question] = generate_questions(
            topic=quiz.topic,
            samples=quiz.questions[:5], # Use first 5 as samples
            count=target_count,
            quiz_analysis=quiz_analysis,
            coverage_analysis=coverage_analysis,
            agent=self
        )
        
        question_validation: QuestionValidation = validate_questions(
            new_questions=new_questions,
            existing_questions=quiz.questions,
            quiz_analysis=quiz_analysis,
            agent=self
        )
        
        return question_validation.valid_questions

