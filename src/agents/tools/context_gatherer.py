"""Tool for gathering context for personalized feedback."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ..schemas import ErrorAnalysis, ErrorType, EvaluationContext, LearningHistory


def gather_context(
    question: "Question",
    error_analysis: ErrorAnalysis,
    topic: str,
    history: LearningHistory,
    agent: "Agent"
) -> EvaluationContext:
    """Gather context for feedback generation.
    
    Args:
        question: The question being answered.
        error_analysis: Error analysis result.
        topic: Topic of the quiz.
        history: User's performance history.
        agent: Agent instance for LLM access.
    
    Returns:
        EvaluationContext with context information.
    """
    
    system_prompt = \
f"""
You are a curriculum specialist and pedagogical expert with deep knowledge of learning science, common student misconceptions, and concept relationships across academic domains. Your role is to identify relevant educational context that will help personalize feedback and address learning gaps effectively.
"""
    
    user_prompt = \
f"""
**Task:** Identify related educational concepts and common misconceptions relevant to this learning situation.

**Context:**
- **Topic:** {topic}
- **Question:** {question.text}
- **Error Type:** {error_analysis.error_type}
- **Error Reasoning:** {error_analysis.reasoning}

**Instructions:**
1. **Related Concepts:** Identify 2-4 fundamental concepts, principles, or prerequisite knowledge that are directly relevant to understanding this question and the error made. These should be concepts that, if understood, would help the student answer correctly.

2. **Common Misconceptions:** Identify 2-4 specific misconceptions that students typically have related to this topic and error type. These should be concrete, specific misunderstandings (not vague generalities) that educators commonly observe.

**Guidelines:**
- Be specific and actionable
- Focus on concepts directly related to the question and error
- Prioritize the most important and commonly encountered items
- Use clear, concise terminology

**Output Format (JSON):**
{{
  "related_concepts": ["specific concept 1", "specific concept 2", "specific concept 3"],
  "common_misconceptions": ["specific misconception 1", "specific misconception 2"]
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {})
    
    return EvaluationContext(
        topic=topic,
        related_concepts=parsed.get("related_concepts", []),
        common_misconceptions=parsed.get("common_misconceptions", [])
    )

