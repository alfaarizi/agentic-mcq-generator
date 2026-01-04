"""AI integration for question generation and evaluation."""

import os
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai
from .models import Question, Choice
from .parser import parse_questions

load_dotenv()


class QuizAI:
    """AI for quiz operations."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    def generate_questions(
        self, topic: str, samples: List[Question], count: int = 3
    ) -> List[Question]:
        """Generate new questions similar to samples."""
        # Format samples for prompt
        sample_text = []
        for q in samples[:3]:
            lines = [f"Q: {q.text}"]
            for c in q.original_choices:
                lines.append(f"{'>' if c.is_correct else '-'} {c.text}")
            sample_text.append("\n".join(lines))

        prompt = f"""Generate {count} multiple choice questions about "{topic}".

Examples:
{chr(10).join(sample_text)}

Create {count} new questions in the same format. Output only questions, no extra text."""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7),
        )

        return parse_questions(response.text)

    def evaluate_answer(
        self, 
        question: Question, 
        selected: List[Choice]
    ) -> Dict[str, str]:
        """Evaluate answer and provide explanation."""
        correct = [c.text for c in question.correct_choices]
        chosen = [c.text for c in selected]

        prompt = f"""Question: {question.text}

Correct: {', '.join(correct)}
User chose: {', '.join(chosen)}

In 2-3 sentences, explain:
1. Why correct answer(s) are right
2. What the user got wrong (if applicable)
3. Key concept

Be concise and educational."""

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3),
        )

        is_correct = set(correct) == set(chosen)

        return {
            "result": "correct" if is_correct else "incorrect",
            "explanation": response.text,
        }
