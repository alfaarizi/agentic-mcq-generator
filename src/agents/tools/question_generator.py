"""Tool for generating questions matching existing quiz style and complexity."""

import re
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ...parser import parse_questions
from ..schemas import QuizContext, TopicCoverage, QuizProfile


def generate_questions(
    topic: str,
    samples: List["Question"],
    count: int,
    quiz_context: QuizContext,
    topic_coverage: TopicCoverage,
    agent: "Agent",
    suggested_time_limit: int = 0
) -> Tuple[List["Question"], int]:
    """Generate questions matching existing quiz style and complexity.
    
    Args:
        topic: The quiz topic.
        samples: Sample questions to match style from.
        count: Number of questions to generate.
        quiz_context: Result from quiz_context_extractor tool.
        topic_coverage: Result from topic_coverage_analyzer tool.
        agent: Agent instance for LLM access.
        suggested_time_limit: Suggested time limit in seconds from topic analysis.
            - 0: Quiz should not be timed
            - > 0: Suggested time limit to refine based on question complexity
            - -1: Preserve existing time limit (do not calculate new one)
    
    Returns:
        Tuple of (List of generated Question objects, time limit in seconds).
        Time limit is 0 if not timed, a calculated value if timed, or -1 if preserving existing.
    """
    
    system_prompt = \
f"""
You are a master educator and subject matter expert specializing in quiz design, question generation, and educational assessment. Your expertise includes creating questions that match existing styles, maintain consistency, test conceptual understanding, and address specific learning objectives. You excel at crafting questions with appropriate complexity, clear wording, and plausible distractors that reveal student misconceptions.
"""
    
    # Format sample questions
    sample_text = []
    for q in samples[:3]:
        lines = [q.text]
        for c in q.original_choices:
            prefix = ">" if c.is_correct else "-"
            lines.append(f"{prefix} {c.text}")
        sample_text.append("\n".join(lines))
    
    examples = "\n\n".join(sample_text)
    
    # Extract relevant context
    profile = quiz_context.profile
    covered_concepts = ", ".join(quiz_context.covered_concepts[:5]) or "Various topics"
    gaps = ", ".join(topic_coverage.gaps[:5]) or "None specifically identified"
    suggested_concepts = ", ".join(topic_coverage.suggested_concepts[:5]) or "Continue existing coverage patterns"
    
    # Time limit calculation section (if suggested_time_limit > 0, skip if -1)
    time_limit_section = f"""
6. **Time Limit Calculation:**
   - A suggested time limit of {suggested_time_limit // 60} minutes ({suggested_time_limit} seconds) was provided based on topic analysis
   - Refine this time limit based on the actual complexity of the questions you generate:
     * Question complexity ({profile.complexity} level)
     * Number of questions ({count} questions)
     * Cognitive demand (recall, comprehension, application, analysis)
     * Target audience ({profile.target_audience})
   - Time per question guidelines:
     * Beginner: ~1 minute per question
     * Intermediate: ~1-2 minutes per question
     * Advanced: ~2-3 minutes per question
     * Expert: ~3-4 minutes per question
   - Add a reasonable buffer (10-20%) for reading and thinking
   - Round to nearest 5 minutes for cleaner display
   - If questions are more complex than typical for the level, increase the suggested time
   - If questions are simpler, you may reduce the suggested time
""" if suggested_time_limit > 0 else ""

    user_prompt = \
f"""
**Task:** Generate exactly {count} new questions that match the existing quiz's style, complexity, and educational approach while addressing identified knowledge gaps.{' Additionally, refine the suggested time limit based on the actual question complexity.' if suggested_time_limit > 0 else ''}

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

**Quality Guidelines:**

**❌ Bad Example (Avoid - Too Verbose and Overly Complex):**
<Method Resolution Order and Descriptors>
Consider a complex multiple inheritance scenario where you have a base class that implements a custom descriptor protocol, and several derived classes that override various methods. When Python's interpreter needs to resolve which method to call when an attribute is accessed on an instance of a class that inherits from multiple parent classes, and considering that some of these parent classes might themselves have complex inheritance hierarchies, what specific algorithm does Python 3 use to determine the order in which base classes are searched to find the requested attribute, ensuring that each class appears only once in the resolution order and that subclasses always appear before their parent classes?
- Depth-First Search algorithm that traverses the inheritance tree from left to right as specified in the class definition
- Breadth-First Search algorithm similar to what was used in Python 2 for old-style classes
> C3 Linearization algorithm (also known as C3 superclass linearization or C3 MRO) which is a sophisticated topological sorting algorithm that ensures monotonicity and preserves the order of base classes as specified in the inheritance list while guaranteeing that each class appears exactly once in the method resolution order and that child classes always appear before their parent classes in the linearization
- A random selection mechanism that chooses based on the alphabetical order of class names
</Method Resolution Order and Descriptors>

**✅ Good Examples (Follow - Concise and Clear):**
<Method Resolution Order and Descriptors>
In Python 3, which algorithm is used to determine the Method Resolution Order in cases of multiple inheritance?
- Depth-First Search (DFS)
- Breadth-First Search (BFS)
> C3 Linearization (C3 superclass linearization)
- Random selection based on class definition order

Given the following class hierarchy, what will be the MRO for class D?
```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
```
> D → B → C → A → object
- D → B → A → C → object
- D → C → B → A → object
- D → B → C → object → A
</Method Resolution Order and Descriptors>

**Key Principles:**
- Write concise, direct questions that test the concept clearly
- Avoid unnecessarily complex wording or overly long question stems
- Keep questions focused and readable
- Test conceptual understanding, not the ability to parse complex sentences

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
   - Write concise, direct questions (see Quality Guidelines above)

5. **Format Requirements:**
   - Write the question text directly (NO prefix, NO numbering)
   - Questions MUST NOT be numbered (do not use "1.", "2.", "Q1:", etc.)
   - Use "-" prefix for incorrect answer choices
   - Use ">" prefix for correct answer choices
   - Include 2-6 choices per question (match the pattern from examples)
   - Multiple correct answers are allowed (use ">" for each correct choice)
   - Do NOT use "all of the above" or "none of the above" as choices

{time_limit_section}

**Output Instructions:**
- Generate exactly {count} questions
- Output only the questions in the specified format
- Do not include any commentary, explanations, or additional text
- Questions MUST NOT be numbered (no "1.", "2.", "Q1:", etc.)
{f'- After the questions, include a single line with: "TIME_LIMIT: [seconds]" where [seconds] is the refined time limit in seconds (e.g., "TIME_LIMIT: 1800" for 30 minutes)' if suggested_time_limit > 0 else ''}

**Output Format:**
[Question text]
- [Incorrect choice 1]
- [Incorrect choice 2]
> [Correct choice]
- [Incorrect choice 3]

[Repeat for all {count} questions]

{f'{chr(10)}TIME_LIMIT: [seconds]' if suggested_time_limit > 0 else ''}
"""
    
    response = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.7
    )
    
    # Extract time limit if present, otherwise use suggested or preserve existing (-1)
    time_limit = suggested_time_limit
    if suggested_time_limit > 0 and (match := re.search(r'^TIME_LIMIT:\s*(\d+)\s*$', response, re.MULTILINE | re.IGNORECASE)):
        time_limit = int(match.group(1))
        response = re.sub(r'^TIME_LIMIT:\s*\d+\s*$', '', response, flags=re.MULTILINE | re.IGNORECASE).rstrip()
    
    questions = parse_questions(response)
    
    return (questions, time_limit)

