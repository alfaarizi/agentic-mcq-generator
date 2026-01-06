"""Tool for extracting quiz profile from topic descriptions."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..agent import Agent

from ..schemas import QuizProfile, Complexity, Style, TargetAudience


def extract_quiz_profile(
    topic_description: str,
    agent: "Agent",
    quiz_profile: Optional[QuizProfile] = None
) -> tuple[str, QuizProfile, int, int]:
    """Extract quiz profile, inferred topic name, suggested time limit, and question count from topic description.
    
    Args:
        topic_description: User-provided description of the topic.
        agent: Agent instance for LLM access.
        quiz_profile: Optional initial QuizProfile to refine. If None, creates a new profile.
    
    Returns:
        Tuple of (inferred_topic_name, QuizProfile, suggested_time_limit, suggested_question_count) where:
        - suggested_time_limit: in seconds (0 if quiz should not be timed)
        - suggested_question_count: 0 if not mentioned, otherwise the extracted or calculated count
    """
    
    system_prompt = \
f"""
You are an expert educational content analyst specializing in topic analysis, domain identification, language detection, and curriculum design. Your expertise includes extracting subject domains, detecting languages, validating educational characteristics, and refining learning profiles based on topic descriptions. You analyze educational content systematically to inform quiz generation strategies.
"""
    
    # Conditional initial profile
    initial_profile = f"""
**Initial Profile:**
- **Complexity:** {quiz_profile.complexity}
- **Style:** {quiz_profile.style}
- **Target Audience:** {quiz_profile.target_audience}
- **Language:** {quiz_profile.language}
- **Domain:** {quiz_profile.domain}
""" if quiz_profile else ""

    user_prompt = \
f"""
**Task:** Analyze the topic description to extract domain, language, and {'refine the quiz profile characteristics' if quiz_profile else 'determine quiz profile characteristics'}.

**Topic Description:**
{topic_description}

{initial_profile}

**Instructions:**
Analyze the topic description systematically and provide:

0. **Topic Name**: 
    - Infer a concise, professional topic name (3-8 words) that best represents the quiz subject. 
    - This will be used as the quiz title. 
    - The topic name MUST be in the detected language (see Language section below). 
    - Examples: "Python Basics", "Neural Networks Fundamentals", "World War II History", "Photosynthesis in Plants" (for English); "Fundamentos de Python", "Redes Neuronales Fundamentales" (for Spanish)

1. **Domain**: 
   - Identify the primary subject domain (e.g., "computer_science", "biology", "mathematics", "medicine", "engineering", "history", "literature", "general")
   - Be specific and use standard domain names
   - Consider the main subject area the topic belongs to

2. **Language**:
   - Detect the primary language from the description (use ISO language codes: 'en' for English, 'es' for Spanish, 'fr' for French, 'de' for German, 'hu' for Hungarian, 'zh' for Chinese, 'ja' for Japanese, etc.)
   - Default to 'en' if unclear or mixed

3. **Complexity** (one of: beginner, intermediate, advanced, expert). {'Refine only if the description clearly indicates a different level' if quiz_profile else ''}
   - Beginner: Basic concepts, minimal prerequisite knowledge, simple recall or comprehension
   - Intermediate: Moderate depth, some prerequisite knowledge expected, application of concepts
   - Advanced: Deep understanding required, significant prerequisite knowledge, analysis and synthesis
   - Expert: Specialized knowledge, complex reasoning, evaluation and creation of new understanding

4. **Style** (one of: academic, conversational, practical, concise). {'Refine only if the description clearly indicates a different level' if quiz_profile else ''}
   - Academic: Formal, precise, scholarly language, uses technical terminology, structured presentation, emphasizes theoretical understanding
   - Conversational: Friendly, explanatory, accessible tone, uses everyday language, includes context and background, encourages understanding through dialogue
   - Practical: Applied, scenario-based, real-world focus, emphasizes hands-on application, uses examples from actual use cases, connects theory to practice
   - Concise: Direct, minimal explanation, to-the-point, focuses on essential information, avoids elaboration, efficient and straightforward communication

5. **Target Audience** (one of: high_school, undergraduate, graduate, professional, general). {'Refine only if the description clearly indicates a different level' if quiz_profile else ''}
   - High School: Secondary education level, foundational knowledge, age-appropriate terminology
   - Undergraduate: College/university level, intermediate depth, assumes some prior coursework
   - Graduate: Advanced academic level, specialized knowledge, research-oriented expectations
   - Professional: Industry/workplace context, practical application, professional terminology
   - General: Broad public audience, accessible to non-specialists, minimal assumptions about prior knowledge

6. **Suggested Time Limit**: Determine if the quiz should be timed and suggest an initial time limit in seconds. Consider:
   - If the time is explicitly mentioned in the description (e.g., "5 minutes", "30 minutes", "1 hour", "90 seconds"), extract that exact value and convert it to seconds for the suggested_time_limit
   - Keywords: "exam", "test", "timed", "assessment", "evaluation", "certification"
   - Context: Formal assessments, professional certifications, academic exams
   - If timed but no explicit time mentioned, estimate based on complexity level (beginner: ~60s/question, intermediate: ~120s/question, advanced: ~180s/question, expert: ~240s/question)
   - Return 0 if description suggests self-paced learning, practice, or casual study
   - This is a preliminary estimate; the actual time limit will be refined based on generated questions (unless explicitly mentioned)

7. **Suggested Question Count**: Extract or calculate the number of questions. Consider:
   - If the number of questions is explicitly mentioned (e.g., "10 questions", "20 questions", "5 questions"), extract that exact number
   - If time limit is explicitly mentioned but question count is not, calculate question count from time limit:
     * Use time per question based on complexity: beginner (~60s), intermediate (~120s), advanced (~180s), expert (~240s)
     * Formula: question_count = (time_limit_seconds / time_per_question_seconds) rounded to nearest reasonable number
   - If neither time nor question count is mentioned, return 0 (will use default)

**Guidelines:**
- Extract domain and language from the actual content of the description
{f'- Be conservative with refinements - Only refine complexity, style, or target_audience if the description provides clear indicators' if quiz_profile else 'Determine complexity, style, and target_audience based on the description content'}
{f'- Preserve initial values when in doubt' if quiz_profile else ''}
- Maintain consistency with educational standards

**Output Format (JSON):**
{{
  "topic": "concise topic name (3-8 words)",
  "domain": "subject domain",
  "language": "language code (e.g., 'en', 'es', 'fr', 'de', 'hu')",
  "complexity": "beginner|intermediate|advanced|expert",
  "style": "academic|conversational|practical|concise",
  "target_audience": "high_school|undergraduate|graduate|professional|general",
  "suggested_time_limit": 0,
  "suggested_question_count": 0
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    # Default values based on whether profile exists
    default_topic = topic_description.strip()[:50] if topic_description.strip() else "Custom Quiz"
    default_domain = quiz_profile.domain if quiz_profile else "general"
    default_language = quiz_profile.language if quiz_profile else "en"
    default_complexity = quiz_profile.complexity.value if quiz_profile else "intermediate"
    default_style = quiz_profile.style.value if quiz_profile else "academic"
    default_audience = quiz_profile.target_audience.value if quiz_profile else "undergraduate"
    
    parsed = agent._parse_json(resp, {
        "topic": default_topic,
        "domain": default_domain,
        "language": default_language,
        "complexity": default_complexity,
        "style": default_style,
        "target_audience": default_audience,
        "suggested_time_limit": 0,
        "suggested_question_count": 0
    })
    
    # Create profile
    profile = QuizProfile(
        complexity=Complexity(parsed.get("complexity", default_complexity)),
        style=Style(parsed.get("style", default_style)),
        target_audience=TargetAudience(parsed.get("target_audience", default_audience)),
        language=parsed.get("language", default_language),
        domain=parsed.get("domain", default_domain)
    )
    
    suggested_time_limit = max(0, int(parsed.get("suggested_time_limit", 0)))
    suggested_question_count = max(0, int(parsed.get("suggested_question_count", 0)))
    
    return (
        parsed.get("topic", default_topic).strip(), 
        profile, 
        suggested_time_limit,
        suggested_question_count
    )

