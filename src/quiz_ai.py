"""AI integration for question generation and evaluation using OpenRouter."""

import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

from .models import Question, Choice
from .parser import parse_questions

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

    def evaluate_answer(
        self,
        question: Question,
        selected: List[Choice],
    ) -> Dict[str, str]:
        """Evaluate answer with expert feedback using role-based prompting.

        Args:
            question: The question being answered.
            selected: User's selected choices.

        Returns:
            Dictionary with 'result' and 'explanation' keys.
        """
        correct = [c.text for c in question.correct_choices]
        chosen = [c.text for c in selected]
        is_correct = set(correct) == set(chosen)

        # Extract topic from question context (you may pass this explicitly if available)
        # For now, we'll use generic expertise

        # System prompt: Senior technical educator role
        system_prompt = \
f"""
Act as a seasoned AI Engineer and Senior Software Engineer with 15+ years of experience in technical education, mentorship, and building production systems. Your expertise spans:

**Technical Depth:**
- Deep understanding of computer science fundamentals, software architecture, and AI/ML systems
- Practical experience debugging misconceptions and explaining complex concepts clearly
- Ability to distill technical nuances into digestible explanations

**Teaching Philosophy:**
- Precision over vagueness - use concrete examples and technical accuracy
- Focus on *why* concepts work, not just *what* they are
- Identify the root cause of misconceptions with surgical precision
- Provide structured, scannable explanations using markdown formatting

**Communication Style:**
- Direct, professional technical writing
- Avoid second-person pronouns (no "you/your/you've")
- Use third-person or passive voice: "The selected answer...", "This choice reflects...", "The correct approach..."
- Employ bullet points, numbered lists, and clear structure
- Keep explanations concise: 3-4 sentences maximum
"""

        # User prompt: Specific evaluation task
        correct_str = ", ".join(correct) if correct else "None"
        chosen_str = ", ".join(chosen) if chosen else "None"

        user_prompt = \
f"""
**Task:**
Evaluate the selected answer based on the question and correct answer provided below.
- Question: {question.text}
- Correct answer: {correct_str}
- Selected answer: {chosen_str}

**Requirements:**
Use third-person voice, separate paragraphs with blank lines, maintain technical precision.

**Output Format:**
Paragraph 1: Begin with <mark>, state the fundamental principle or concept being tested (1-2 sentences), then close with </mark>.
Paragraph 2: Analyze the selected answer—explain the specific misconception or reasoning error if incorrect, or affirm the reasoning if correct (1-2 sentences).
Paragraph 3: Provide the heading "<u>Key Distinctions:</u>" followed by a bulleted list with 2-3 critical points distinguishing the correct answer from incorrect options.

Output exactly in the specified format only, no commentary.
"""

        explanation = self._generate(system_prompt, user_prompt, temperature=0.3)

        return {
            "result": "correct" if is_correct else "incorrect",
            "explanation": explanation.strip(),
        }
