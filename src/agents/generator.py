"""GeneratorAgent for autonomous quiz creation from topic descriptions."""

from typing import List, Optional, Callable

from ..models import Quiz, Question
from .agent import Agent
from .schemas import (
    QuizProfile,
    QuizContext,
    TopicCoverage,
)
from .tools import (
    extract_quiz_profile,
    plan_topic_coverage,
    generate_questions,
    validate_questions
)


class GeneratorAgent(Agent):
    """Autonomous agent for generating new quizzes from topic descriptions."""

    def __init__(
        self,
        model: str = "google/gemini-2.5-flash",
        tools: Optional[List[Callable]] = None,
    ) -> None:
        default_tools = [extract_quiz_profile, plan_topic_coverage, generate_questions, validate_questions]
        super().__init__(model, tools=tools or default_tools)

    def generate_quiz(
        self,
        topic_description: str,
        profile: QuizProfile,
        question_count: int = 15,
    ) -> Quiz:
        """Generate a new quiz from a high-level topic description."""

        quiz_topic, quiz_profile, suggested_time_limit = extract_quiz_profile(
            topic_description=topic_description,
            agent=self,
            quiz_profile=profile
        )
        
        quiz_context: QuizContext = QuizContext(
            profile=quiz_profile,
            covered_concepts=[]  # Empty for new quiz
        )
        
        topic_coverage: TopicCoverage = plan_topic_coverage(
            topic_description=topic_description,
            quiz_context=quiz_context,
            question_count=question_count,
            agent=self
        )
        
        new_questions, time_limit = generate_questions(
            topic=quiz_topic,
            samples=[], # No existing samples for new quiz
            count=question_count,
            quiz_context=quiz_context,
            topic_coverage=topic_coverage,
            agent=self,
            suggested_time_limit=suggested_time_limit
        )
        
        validated_questions: List[Question] = validate_questions(
            new_questions=new_questions,
            existing_questions=[],  # No existing questions for new quiz
            quiz_context=quiz_context,
            agent=self
        )
                
        return Quiz(
            topic=quiz_topic,
            questions=validated_questions or new_questions,
            time_limit=time_limit
        )


