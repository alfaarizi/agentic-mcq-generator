"""Tool for generating adaptive feedback based on error type and context."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question, Choice

from ..schemas import ErrorAnalysis, ErrorType, EvaluationContext, Feedback


def generate_feedback(
    question: "Question",
    selected: list["Choice"],
    error_analysis: ErrorAnalysis,
    eval_context: EvaluationContext,
    agent: "Agent"
) -> Feedback:
    """Generate adaptive feedback based on error type and context.
    
    Args:
        question: The question being answered.
        selected: User's selected choices.
        error_analysis: Error analysis result.
        eval_context: Context information.
        agent: Agent instance for LLM access.
    
    Returns:
        Structured Feedback object.
    """
    
    err_type = error_analysis.error_type
    
    system_prompt = \
f"""
You are an experienced educator and learning facilitator specializing in adaptive instruction and formative feedback. Your expertise includes explaining complex concepts clearly, addressing misconceptions constructively, and guiding students toward deeper understanding. You adapt your communication style based on error types to maximize learning outcomes.
"""
    
    correct_txt = ', '.join(c.text for c in question.correct_choices)
    selected_txt = ', '.join(c.text for c in selected)
    concepts = ', '.join(eval_context.related_concepts) if eval_context.related_concepts else "None identified"
    misconceptions = ', '.join(eval_context.common_misconceptions) if eval_context.common_misconceptions else "None identified"
    
    user_prompt = \
f"""
**Task:** Generate structured, personalized feedback that helps the student understand their answer and learn from it.

**Question Context:**
- **Question:** {question.text}
- **Correct Answer(s):** {correct_txt}
- **Student's Answer(s):** {selected_txt}

**Error Analysis:**
- **Error Type:** {err_type}
- **Analysis Reasoning:** {error_analysis.reasoning}

**Educational Context:**
- **Related Concepts:** {concepts}
- **Common Misconceptions:** {misconceptions}

**Instructions:**
Generate feedback with the following components:

1. **Concept** (1-2 sentences): State the fundamental principle, rule, or concept being tested. This should be the core idea the student needs to understand.

2. **Explanation** (1-2 sentences): Explain what went wrong (or right) in the student's answer. Be specific about their reasoning error or correct understanding. Use a supportive, constructive tone.

3. **Key Points** (2-4 items): Provide a bulleted list of critical distinctions, important facts, or key takeaways that will help the student understand the concept better. Each point should be concise (one sentence or phrase).

4. **Hints** (only if answer is incorrect, 1-2 items): Provide subtle guidance that helps the student think through the problem without giving away the answer. These should encourage self-discovery.

**Tone Guidelines:**
- Be encouraging and supportive
- Focus on learning, not just correctness
- Use clear, accessible language
- Avoid condescension or judgment

**Output Format (JSON):**
{{
  "concept": "The fundamental principle or concept (1-2 sentences)",
  "explanation": "What went wrong/right and why (1-2 sentences)",
  "key_points": ["Key point 1", "Key point 2", "Key point 3"],
  "hints": ["Hint 1", "Hint 2"]  // Include only if answer is incorrect, otherwise null
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {
        "concept": "",
        "explanation": "",
        "key_points": [],
        "hints": None
    })
    
    return Feedback(
        concept=parsed.get("concept", ""),
        explanation=parsed.get("explanation", ""),
        key_points=parsed.get("key_points", []),
        hints=parsed.get("hints")
    )

