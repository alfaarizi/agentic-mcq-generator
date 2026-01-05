"""AI integration for question generation and evaluation using OpenRouter."""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

from .models import Question, Choice
from .parser import parse_questions
from .agents.evaluator import EvaluatorAgent
from .agents.schemas import LearningHistory

load_dotenv()


class QuizAI:
    """AI service for quiz operations using OpenRouter."""

    def __init__(self, model: str = "google/gemini-2.5-flash"):
        """Initialize QuizAI with OpenRouter.

        Args:
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet").

        Raises:
            ValueError: If OPENROUTER_API_KEY is not set.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model
        self._evaluator = None  # Lazy initialization

    def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using OpenRouter API with system and user prompts.

        Args:
            system_prompt: System message defining AI role and behavior.
            user_prompt: User message with the actual request.
            temperature: Sampling temperature (0.0-2.0).

        Returns:
            Generated text response.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def generate_questions(
        self,
        topic: str,
        samples: List[Question],
        count: int = 3,
    ) -> List[Question]:
        """Generate new questions similar to samples using expert-level prompting.

        Args:
            topic: The topic for questions.
            samples: Sample questions to learn from.
            count: Number of questions to generate.

        Returns:
            List of generated Question objects.
        """
        # Format sample questions with all their nuances
        sample_text = []
        for q in samples[:3]:
            lines = [f"Q: {q.text}"]
            for c in q.original_choices:
                prefix = ">" if c.is_correct else "-"
                lines.append(f"{prefix} {c.text}")
            sample_text.append("\n".join(lines))

        examples = "\n\n".join(sample_text)

        # System prompt: Define expert role and context
        system_prompt = \
f"""
Act as a Master educator and subject matter expert in {topic} with 15+ years in curriculum design and assessment development.

Expertise:
- Comprehensive knowledge of {topic} from fundamentals to advanced concepts
- Identifying common misconceptions and knowledge gaps
- Crafting questions that test understanding over memorization
- Creating plausible distractors based on realistic errors

Question requirements:
- Match difficulty and style of provided examples
- Clear, precise language without ambiguity or trick elements
- Distractors reveal specific misconceptions
- Each question tests a distinct concept
"""
        # User prompt: Specific task with examples and format
        user_prompt = \
f"""
**Task:**
Generate {count} questions about "{topic}" matching these examples in style, difficulty, and format.

**Examples:**
{examples}

**Requirements:**
- Test conceptual understanding, not trivial recall
- Distractors based on plausible errors or misconceptions
- Clear, unambiguous question text
- Match domain terminology from examples
- Avoid "all of the above" or "none of the above"

**Output Format:**
- Start with "Q: " followed by question text
- Use "-" for incorrect answers, ">" for correct answers
- Include 2-6+ choices per question
- Multiple correct answers allowed (use ">" for each)

Output exactly {count} questions in the specified format only, no commentary.
"""
        response = self._generate(system_prompt, user_prompt, temperature=0.7)
        return parse_questions(response)

    @property
    def evaluator(self) -> EvaluatorAgent:
        """Get or create EvaluatorAgent instance."""
        if self._evaluator is None:
            self._evaluator = EvaluatorAgent(model=self.model)
        return self._evaluator

    def evaluate_answer(
        self,
        question: Question,
        selected: List[Choice],
        topic: Optional[str] = None,
        learning_history: Optional[LearningHistory] = None,
    ) -> Dict[str, any]:
        """Evaluate answer using EvaluatorAgent.

        Args:
            question: The question being answered.
            selected: User's selected choices.
            topic: Topic of the quiz (defaults to "general").
            learning_history: Optional learning history for personalized feedback.

        Returns:
            Dictionary with evaluation result including structured feedback.
        """
        if topic is None:
            topic = "general"
        
        result = self.evaluator.evaluate(
            question=question,
            selected=selected,
            topic=topic,
            learning_history=learning_history
        )
        
        # Convert to dict format for backward compatibility
        return result.to_dict()
