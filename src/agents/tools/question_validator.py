"""Tool for validating new questions against existing ones for quality and consistency."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ..schemas import QuizContext, QuizProfile


def validate_questions(
    new_questions: List["Question"],
    existing_questions: List["Question"],
    quiz_context: QuizContext,
    agent: "Agent"
) -> List["Question"]:
    """Validate new questions for quality, consistency, and uniqueness.
    
    Args:
        new_questions: Newly generated questions to validate.
        existing_questions: Existing questions to compare against.
        quiz_context: Result from quiz_context_extractor tool.
        agent: Agent instance for LLM access.
    
    Returns:
        List of validated Question objects.
    """
    
    system_prompt = \
f"""
You are a quality assurance expert specializing in educational content validation, assessment design, and pedagogical consistency. Your expertise includes identifying duplicate concepts, style inconsistencies, complexity mismatches, language issues, and quality problems in quiz questions. You evaluate questions systematically against established criteria to ensure educational value and consistency.
"""
    
    # Format questions for comparison
    existing_text = []
    for i, q in enumerate(existing_questions[:5], 1):
        existing_text.append(f"{i}. {q.text[:200]}")
    
    new_text = []
    for i, q in enumerate(new_questions, 0):
        new_text.append(f"Index {i}: {q.text[:200]}")
    
    profile = quiz_context.profile
    
    user_prompt = \
f"""
**Task:** Validate each new question for quality, consistency, uniqueness, and alignment with the existing quiz standards.

**Existing Questions (Reference Sample):**
{chr(10).join(existing_text) if existing_text else "None provided"}

**New Questions to Validate:**
{chr(10).join(new_text) if new_text else "None provided"}

**Quiz Quality Standards:**
- **Style:** {profile.style}
- **Complexity:** {profile.complexity}
- **Language:** {profile.language}
- **Target Audience:** {profile.target_audience}

**Validation Criteria:**

For each new question, evaluate against these criteria:

1. **Concept Uniqueness:**
   - Does this question test a distinct concept that is not already covered by existing questions?
   - Is the core learning objective different from other questions?
   - Mark as invalid if it duplicates an existing question's concept

2. **Style Consistency:**
   - Does the writing tone match the {profile.style} style of existing questions?
   - Is the level of formality, explanation, and presentation consistent?
   - Does it use similar sentence structure and phrasing patterns?

3. **Complexity Alignment:**
   - Is the cognitive demand appropriate for {profile.complexity} level?
   - Does it match the depth and sophistication of existing questions?
   - Is the prerequisite knowledge requirement consistent?

4. **Language Consistency:**
   - Is the question written in {profile.language}?
   - Is the language quality and clarity consistent with existing questions?
   - Are there any translation issues or language errors?

5. **Quality Issues:**
   - Is the question clear and unambiguous?
   - Are there any grammatical errors, typos, or unclear wording?
   - Are the answer choices well-formed and appropriate?
   - Is the question free from trick elements or misleading phrasing?

**Validation Instructions:**
- Review each new question (indexed 0 to {len(new_questions)-1}) against all criteria above
- Mark a question as INVALID if it fails any of the criteria
- Mark a question as VALID only if it passes all criteria
- Be strict but fair in your evaluation

**Output Format (JSON):**
{{
  "valid_questions": [0, 1, 3, 4]
}}

Provide the indices (0-based) of valid questions only.
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {
        "valid_questions": list(range(len(new_questions)))
    })
    
    # Filter questions based on validation
    valid_indices = parsed.get("valid_questions", [])
    
    valid_questions = [
        new_questions[i] for i in valid_indices
        if 0 <= i < len(new_questions)
    ]
    
    return valid_questions

