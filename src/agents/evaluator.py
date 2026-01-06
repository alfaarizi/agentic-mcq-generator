"""EvaluatorAgent for autonomous answer evaluation and feedback generation."""

from typing import Dict, Any, List, Optional, Callable, Union

from ..models import Question, Choice
from .agent import Agent
from .schemas import (
    ErrorEvaluation, PedagogicalContext, Feedback, 
    LearningProfile, LearningSuggestion, ResponseEvaluation, QuizContext
)
from .tools import evaluate_error, extract_pedagogical_context, generate_feedback, generate_suggestions


class EvaluatorAgent(Agent):
    """Autonomous agent for evaluating quiz answers and generating adaptive feedback."""
    
    def __init__(
        self,
        model: str = "google/gemini-2.5-flash",
        tools: Optional[List[Callable]] = None
    ) -> None:
        default_tools = [evaluate_error, extract_pedagogical_context, generate_feedback, generate_suggestions]
        super().__init__(model, tools=tools or default_tools)
    
    
    def evaluate(
        self,
        question: Question,
        selected: List[Choice],
        topic: str = "general",
        learning_profile: Optional[Union[LearningProfile, Dict[str, Any]]] = None,
        quiz_context: Optional[QuizContext] = None
    ) -> ResponseEvaluation:
        """Evaluate answer and generate adaptive feedback.
        
        Args:
            question: The question being answered.
            selected: User's selected choices.
            topic: Topic of the quiz.
            learning_profile: Optional learning profile for personalized feedback.
            quiz_context: Optional quiz context (style, complexity, language, etc.) to adapt suggestions.
        
        Returns:
            ResponseEvaluation with feedback, error evaluation, and suggestions.
        """
        if learning_profile is None:
            learning_profile = LearningProfile()
        elif isinstance(learning_profile, dict):
            learning_profile = LearningProfile.from_dict(learning_profile)
        
        error_evaluation: ErrorEvaluation = evaluate_error(question, selected, agent=self)
        
        pedagogical_context: PedagogicalContext = extract_pedagogical_context(question, error_evaluation, topic, learning_profile, agent=self)
        
        feedback: Feedback = generate_feedback(question, selected, error_evaluation, pedagogical_context, agent=self)
        
        suggestions: List[LearningSuggestion] = generate_suggestions(
            question, error_evaluation, topic, learning_profile, pedagogical_context, agent=self, quiz_context=quiz_context
        )
        
        return ResponseEvaluation(
            feedback=feedback,
            error_evaluation=error_evaluation,
            learning_profile=learning_profile,
            suggestions=suggestions if suggestions else None
        )
    
