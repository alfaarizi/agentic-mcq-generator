"""Tool for extracting context from existing quiz structure, style, and characteristics."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Quiz

from ..schemas import QuizContext


def extract_quiz_context(
    quiz: "Quiz",
    agent: "Agent"
) -> QuizContext:
    """Extract context from existing quiz to determine style, complexity, and characteristics.
    
    Args:
        quiz: The existing quiz to extract context from.
        agent: Agent instance for LLM access.
    
    Returns:
        QuizContext with style, complexity, language, and other characteristics.
    """
    system_prompt = \
f"""You are an expert educational assessment analyst specializing in quiz design, content analysis, and curriculum evaluation. Your expertise includes identifying question styles, complexity levels, language patterns, educational characteristics, and learning objectives. You analyze educational content with precision and provide comprehensive assessments that inform content generation strategies.
"""
    
    # Format sample questions for analysis
    sample_questions = []
    for q in quiz.questions[:5]:  # Analyze up to 5 questions
        choices_text = ", ".join([c.text for c in q.original_choices[:3]])
        sample_questions.append(f"{q.text[:100]}... | Choices: {choices_text[:50]}...")
    
    questions_text = "\n".join(sample_questions)
    
    user_prompt = \
f"""
**Task:** Analyze the existing quiz to extract its core characteristics, style, and educational profile.

**Quiz Context:**
- **Topic:** {quiz.topic}
- **Number of Questions:** {len(quiz.questions)}

**Sample Questions:**
{questions_text}

**Instructions:**
Analyze the quiz systematically and provide the following characteristics:

1. **Style** (one of: academic, conversational, practical, concise): Determine the question presentation approach based on writing tone, formality, and explanation style. Consider:
   - Academic: Formal, precise, scholarly language, uses technical terminology, structured presentation, emphasizes theoretical understanding
   - Conversational: Friendly, explanatory, accessible tone, uses everyday language, includes context and background, encourages understanding through dialogue
   - Practical: Applied, scenario-based, real-world focus, emphasizes hands-on application, uses examples from actual use cases, connects theory to practice
   - Concise: Direct, minimal explanation, to-the-point, focuses on essential information, avoids elaboration, efficient and straightforward communication

2. **Complexity** (one of: beginner, intermediate, advanced, expert). Assess the difficulty and depth of questions based on:
   - Beginner: Basic concepts, minimal prerequisite knowledge, simple recall or comprehension
   - Intermediate: Moderate depth, some prerequisite knowledge expected, application of concepts
   - Advanced: Deep understanding required, significant prerequisite knowledge, analysis and synthesis
   - Expert: Specialized knowledge, complex reasoning, evaluation and creation of new understanding

3. **Language**: Identify the primary language used (use ISO language codes: 'en' for English, 'hu' for Hungarian, etc.)

4. **Domain**: Identify the subject domain (e.g., "computer science", "medicine", "engineering", "mathematics", "biology", "general")

5. **Covered Concepts**: Extract 3-8 main concepts, topics, or themes covered in the existing questions. Be specific and use domain-appropriate terminology. The concepts MUST be expressed in the detected language (see Language section above).

6. **Target Audience** (one of: high_school, undergraduate, graduate, professional, general). Infer the educational or professional level based on:
   - High School: Secondary education level, foundational knowledge, age-appropriate terminology
   - Undergraduate: College/university level, intermediate depth, assumes some prior coursework
   - Graduate: Advanced academic level, specialized knowledge, research-oriented expectations
   - Professional: Industry/workplace context, practical application, professional terminology
   - General: Broad public audience, accessible to non-specialists, minimal assumptions about prior knowledge

**Guidelines:**
- Base your analysis on the actual content and style of the sample questions
- Be specific and precise in your classifications
- Use the exact enum values for style, complexity, and target_audience
- Extract concepts that are directly observable in the questions

**Output Format (JSON):**
{{
  "style": "academic|conversational|practical|concise",
  "complexity": "beginner|intermediate|advanced|expert",
  "language": "language code (e.g., 'en', 'hu')",
  "domain": "subject domain",
  "covered_concepts": ["specific concept 1", "specific concept 2", "specific concept 3"],
  "target_audience": "high_school|undergraduate|graduate|professional|general"
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {
        "style": "academic",
        "complexity": "intermediate",
        "language": "en",
        "domain": "general",
        "covered_concepts": [],
        "target_audience": "undergraduate"
    })
    
    return QuizContext.from_dict(parsed)

