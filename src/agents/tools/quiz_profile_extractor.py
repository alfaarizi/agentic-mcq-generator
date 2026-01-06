"""Tool for extracting quiz profile from topic descriptions."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..agent import Agent

from ..schemas import QuizProfile, Complexity, Style, TargetAudience


def extract_quiz_profile(
    topic_description: str,
    agent: "Agent",
    quiz_profile: Optional[QuizProfile] = None
) -> QuizProfile:
    """Extract quiz profile from topic description, optionally refining an existing profile.
    
    Args:
        topic_description: User-provided description of the topic.
        agent: Agent instance for LLM access.
        quiz_profile: Optional initial QuizProfile to refine. If None, creates a new profile.
    
    Returns:
        QuizProfile with extracted domain, language, and characteristics.
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

**Guidelines:**
- Extract domain and language from the actual content of the description
{f'- Be conservative with refinements - Only refine complexity, style, or target_audience if the description provides clear indicators' if quiz_profile else 'Determine complexity, style, and target_audience based on the description content'}
{f'- Preserve initial values when in doubt' if quiz_profile else ''}
- Maintain consistency with educational standards

**Output Format (JSON):**
{{
  "domain": "subject domain",
  "language": "language code (e.g., 'en', 'es', 'fr', 'de', 'hu')",
  "complexity": "beginner|intermediate|advanced|expert",
  "style": "academic|conversational|practical|concise",
  "target_audience": "high_school|undergraduate|graduate|professional|general"
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    # Default values based on whether profile exists
    default_domain = quiz_profile.domain if quiz_profile else "general"
    default_language = quiz_profile.language if quiz_profile else "en"
    default_complexity = quiz_profile.complexity.value if quiz_profile else "intermediate"
    default_style = quiz_profile.style.value if quiz_profile else "academic"
    default_audience = quiz_profile.target_audience.value if quiz_profile else "undergraduate"
    
    parsed = agent._parse_json(resp, {
        "domain": default_domain,
        "language": default_language,
        "complexity": default_complexity,
        "style": default_style,
        "target_audience": default_audience
    })
    
    # Create profile
    return QuizProfile(
        complexity=Complexity(parsed.get("complexity", default_complexity)),
        style=Style(parsed.get("style", default_style)),
        target_audience=TargetAudience(parsed.get("target_audience", default_audience)),
        language=parsed.get("language", default_language),
        domain=parsed.get("domain", default_domain)
    )

