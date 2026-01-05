"""EvaluatorAgent for autonomous answer evaluation and feedback generation."""

from typing import Dict, Any, List, Optional, Callable, Union

from ..models import Question, Choice
from .agent import Agent
from .schemas import (
    ErrorAnalysis, EvaluationContext, Feedback, 
    LearningHistory, LearningSuggestion, EvaluationResult
)
from .tools import analyze_error, gather_context, generate_feedback, generate_suggestions


class EvaluatorAgent(Agent):
    """Autonomous agent for evaluating quiz answers and generating adaptive feedback."""
    
    def __init__(
        self,
        model: str = "google/gemini-2.5-flash",
        tools: Optional[List[Callable]] = None
    ) -> None:
        default_tools = [analyze_error, gather_context, generate_feedback, generate_suggestions]
        super().__init__(model, tools=tools or default_tools)
    
    
    def evaluate(
        self,
        question: Question,
        selected: List[Choice],
        topic: str = "general",
        learning_history: Optional[Union[LearningHistory, Dict[str, Any]]] = None
    ) -> EvaluationResult:
        """Evaluate answer and generate adaptive feedback."""
        if learning_history is None:
            learning_history = LearningHistory()
        elif isinstance(learning_history, dict):
            learning_history = LearningHistory.from_dict(learning_history)
        
        error_analysis: ErrorAnalysis = analyze_error(question, selected, agent=self)
        
        eval_context: EvaluationContext = gather_context(question, error_analysis, topic, learning_history, agent=self)
        
        feedback: Feedback = generate_feedback(question, selected, error_analysis, eval_context, agent=self)
        
        suggestions: List[LearningSuggestion] = generate_suggestions(question, error_analysis, topic, learning_history, eval_context, agent=self)
        
        return EvaluationResult(
            feedback=feedback,
            error_analysis=error_analysis,
            learning_history=learning_history,
            suggestions=suggestions if suggestions else None
        )
    
