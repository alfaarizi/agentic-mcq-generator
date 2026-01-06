"""Tool for evaluating answer errors and classifying error types."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question, Choice

from ..schemas import ErrorEvaluation, ErrorType


def evaluate_error(
    question: "Question",
    selected: list["Choice"],
    agent: "Agent"
) -> ErrorEvaluation:
    """Analyze error type in student answers.
    
    Args:
        question: The question being answered.
        selected: User's selected choices.
        agent: Agent instance for LLM access.
    
    Returns:
        Dictionary with error_type, confidence, and reasoning.
    """
    correct = question.correct_choices
    if set(selected) == set(correct):
        return ErrorEvaluation(
            error_type=ErrorType.CORRECT,
            confidence=1.0,
            reasoning="Exact match"
        )
    
    system_prompt = \
f"""
You are an expert educational psychologist specializing in cognitive assessment and learning diagnostics. Your expertise includes identifying patterns in student errors, understanding misconceptions, and classifying different types of learning difficulties. You analyze student responses with precision and provide evidence-based classifications.
"""
    
    user_prompt = \
f"""
**Task:** Analyze the student's answer and classify the type of error they made.

**Question:** {question.text}

**Correct Answer(s):** {', '.join(c.text for c in correct)}

**Student's Selected Answer(s):** {', '.join(c.text for c in selected)}

**Classification Categories:**
1. **conceptual_misunderstanding** - Fundamental misunderstanding of core concepts
2. **partial_understanding** - Some correct knowledge but missing key elements
3. **terminology_confusion** - Confusion between similar terms or definitions
4. **application_error** - Understands concept but misapplies it
5. **careless_mistake** - Simple oversight or calculation error

**Instructions:**
- Analyze the discrepancy between the correct and selected answers
- Classify the error into ONE of the five categories above
- Provide a confidence score (0.0-1.0) based on how certain you are
- Write clear, concise reasoning (1-2 sentences) explaining your classification

**Output Format (JSON):**
{{
  "error_type": "one of the five categories",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of why this classification was chosen"
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result_dict = agent._parse_json(resp, {
        "error_type": "conceptual_misunderstanding",
        "confidence": 0.5,
        "reasoning": "Unable to parse"
    })
    return ErrorEvaluation.from_dict(result_dict)

