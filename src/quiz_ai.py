"""AI integration for question generation and evaluation using OpenRouter."""

from typing import List, Dict, Optional

from .models import Question, Choice, Quiz
from .agents.evaluator import EvaluatorAgent
from .agents.augmenter import AugmenterAgent
from .agents.schemas import LearningProfile, QuizContext


class QuizAI:
    """AI service for quiz operations using OpenRouter."""

    def __init__(self, model: str = "google/gemini-2.5-flash"):
        """Initialize QuizAI with model configuration.

        Args:
            model: Model identifier (e.g., "google/gemini-2.5-flash").
        """
        self.model = model
        self._evaluator = None  # Lazy initialization
        self._augmenter = None  # Lazy initialization

    @property
    def augmenter(self) -> AugmenterAgent:
        """Get or create AugmenterAgent instance."""
        if self._augmenter is None:
            self._augmenter = AugmenterAgent(model=self.model)
        return self._augmenter

    @property
    def evaluator(self) -> EvaluatorAgent:
        """Get or create EvaluatorAgent instance."""
        if self._evaluator is None:
            self._evaluator = EvaluatorAgent(model=self.model)
        return self._evaluator

    def generate_questions(
        self,
        topic: str,
        samples: List[Question],
        count: int = 3,
    ) -> List[Question]:
        """Generate new questions similar to samples using AugmenterAgent.

        Args:
            topic: The topic for questions.
            samples: Sample questions to learn from.
            count: Number of questions to generate.

        Returns:
            List of generated Question objects.
        """

        quiz = Quiz(topic=topic, questions=samples)
        
        return self.augmenter.augment(quiz, target_count=count)

    def evaluate_answer(
        self,
        question: Question,
        selected: List[Choice],
        topic: Optional[str] = None,
        learning_profile: Optional[LearningProfile] = None,
        quiz_context: Optional[QuizContext] = None
    ) -> Dict[str, any]:
        """Evaluate answer using EvaluatorAgent.

        Args:
            question: The question being answered.
            selected: User's selected choices.
            topic: Topic of the quiz (defaults to "general").
            learning_profile: Optional learning profile for personalized feedback.
            quiz_context: Optional quiz context (style, complexity, language, etc.) to adapt suggestions.

        Returns:
            Dictionary with evaluation result including structured feedback.
        """
        
        result = self.evaluator.evaluate(
            question=question,
            selected=selected,
            topic=topic or "general",
            learning_profile=learning_profile,
            quiz_context=quiz_context
        )
        
        # Convert to dict format for backward compatibility
        return result.to_dict()
