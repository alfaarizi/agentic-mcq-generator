"""Tool for generating adaptive feedback based on error type and context."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question, Choice

from ..schemas import ErrorEvaluation, ErrorType, PedagogicalContext, Feedback, QuizContext


def generate_feedback(
    question: "Question",
    selected: list["Choice"],
    error_analysis: ErrorEvaluation,
    eval_context: PedagogicalContext,
    agent: "Agent",
    quiz_context: Optional["QuizContext"] = None
) -> Feedback:
    """Generate adaptive feedback based on error type and context.
    
    Args:
        question: The question being answered.
        selected: User's selected choices.
        error_analysis: Error analysis result.
        eval_context: Context information.
        agent: Agent instance for LLM access.
        quiz_context: Optional quiz context (language, style, etc.) to adapt feedback.
    
    Returns:
        Structured Feedback object.
    """
    
    err_type = error_analysis.error_type
    
    # Build language requirement section if quiz_context is provided
    language_requirement = f"""
**Language Requirement:**
- Generate ALL feedback components (concept, explanation, key points, and hints) in {quiz_context.profile.language} language
- Write naturally and idiomatically in {quiz_context.profile.language}
- Do not mix languages or translate terms unnecessarily
- Ensure grammatical correctness and appropriate tone for {quiz_context.profile.language}
""" if quiz_context else ""
    
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

{language_requirement}

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

**Formatting Guidelines:**
Use markdown formatting to enhance readability and emphasize important information:
- **Bold** (`**text**`): Use for key terms, important concepts, or critical information that students should remember
- *Italic* (`*text*`): Use for emphasis, definitions, or subtle highlights
- `Inline code` (`` `code` ``): Use for technical terms, function names, variables, or short code snippets
- Code blocks (```` ```language\ncode\n```` ```): Use for longer code examples or multi-line snippets when demonstrating concepts. Example: `` ```python\ndef example():\n    pass\n``` ``
- **Spacing**: Single line breaks are preserved. For additional spacing, use HTML: `<br>` for line breaks, `&nbsp;` for extra spaces, or multiple line breaks for paragraph spacing.
- Use formatting judiciously—only when it adds clarity or emphasis, not excessively

Examples:
- "The **agent** in agentic AI refers to an autonomous entity that *perceives and acts* in its environment."
- "In Python, the `__init__` method is called when creating a new instance."
- "Remember that **autonomy** is the key characteristic, not just *intelligence*."
- For code examples: Use code blocks when showing implementation patterns or longer snippets

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

