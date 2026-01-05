"""Tool for generating questions matching existing quiz style and complexity."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ...parser import parse_questions
from ..schemas import QuizAnalysis, CoverageAnalysis, QuizProfile


def generate_questions(
    topic: str,
    samples: List["Question"],
    count: int,
    quiz_analysis: QuizAnalysis,
    coverage_analysis: CoverageAnalysis,
    agent: "Agent"
) -> List["Question"]:
    """Generate questions matching existing quiz style and complexity.
    
    Args:
        topic: The quiz topic.
        samples: Sample questions to match style from.
        count: Number of questions to generate.
        quiz_analysis: Result from quiz_analyzer tool.
        coverage_analysis: Result from coverage_analyzer tool.
        agent: Agent instance for LLM access.
    
    Returns:
        List of generated Question objects.
    """
    
    system_prompt = \
f"""
You are a master educator and subject matter expert specializing in quiz design, question generation, and educational assessment. Your expertise includes creating questions that match existing styles, maintain consistency, test conceptual understanding, and address specific learning objectives. You excel at crafting questions with appropriate complexity, clear wording, and plausible distractors that reveal student misconceptions.
"""
    
    # Format sample questions
    sample_text = []
    for q in samples[:3]:
        lines = [f"Q: {q.text}"]
        for c in q.original_choices:
            prefix = ">" if c.is_correct else "-"
            lines.append(f"{prefix} {c.text}")
        sample_text.append("\n".join(lines))
    
    examples = "\n\n".join(sample_text)
    
    # Extract relevant context
    profile = quiz_analysis.profile
    covered_concepts = ", ".join(quiz_analysis.covered_concepts[:5]) or "Various topics"
    gaps = ", ".join(coverage_analysis.gaps[:5]) or "None specifically identified"
    suggested_concepts = ", ".join(coverage_analysis.suggested_concepts[:5]) or "Continue existing coverage patterns"
    
    user_prompt = \
f"""
**Task:** Generate exactly {count} new questions that match the existing quiz's style, complexity, and educational approach while addressing identified knowledge gaps.

**Topic:** {topic}

**Existing Quiz Profile:**
- **Style:** {profile.style}
- **Complexity:** {profile.complexity}
- **Target Audience:** {profile.target_audience}
- **Domain:** {profile.domain}
- **Language:** {profile.language}

**Content Context:**
- **Currently Covered Concepts:** {covered_concepts}
- **Identified Knowledge Gaps:** {gaps}
- **Suggested Concepts for New Questions:** {suggested_concepts}

**Example Questions (Study these carefully to match style and format):**
{examples}

**Question Generation Requirements:**

1. **Style Consistency:**
   - Match the writing tone, formality, and presentation approach of the examples exactly
   - Use the same level of explanation and detail
   - Maintain consistency in question structure and phrasing

2. **Complexity Matching:**
   - Ensure questions are at the {profile.complexity} level
   - Match the cognitive demand (recall, comprehension, application, analysis)
   - Use appropriate terminology for {profile.target_audience} level

3. **Content Focus:**
   - Prioritize questions that address identified gaps: {gaps}
   - Incorporate suggested concepts: {suggested_concepts}
   - Ensure each question tests a distinct concept (avoid redundancy)
   - Cover important aspects of {topic} comprehensively

4. **Question Quality:**
   - Test conceptual understanding, not trivial recall or memorization
   - Use clear, unambiguous language appropriate for {profile.language}
   - Create plausible distractors based on common misconceptions
   - Ensure correct answers are clearly correct and distractors are clearly incorrect
   - Avoid trick questions or ambiguous wording

5. **Format Requirements:**
   - Start each question with "Q: " followed by the question text
   - Use "-" prefix for incorrect answer choices
   - Use ">" prefix for correct answer choices
   - Include 2-6 choices per question (match the pattern from examples)
   - Multiple correct answers are allowed (use ">" for each correct choice)
   - Do NOT use "all of the above" or "none of the above" as choices

**Output Instructions:**
- Generate exactly {count} questions
- Output only the questions in the specified format
- Do not include any commentary, explanations, or additional text
- Ensure questions are numbered sequentially if examples show numbering

**Output Format:**
Q: [Question text]
- [Incorrect choice 1]
- [Incorrect choice 2]
> [Correct choice]
- [Incorrect choice 3]

[Repeat for all {count} questions]
"""
    
    response = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.7
    )
    
    return parse_questions(response)

