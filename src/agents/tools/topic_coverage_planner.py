"""Tool for planning topic coverage and identifying concepts for new quiz generation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent

from ..schemas import QuizContext, TopicCoverage, QuizProfile


def plan_topic_coverage(
    topic_description: str,
    quiz_context: QuizContext,
    question_count: int,
    agent: "Agent"
) -> TopicCoverage:
    """Plan topic coverage and identify concepts to cover for a new quiz.
    
    Args:
        topic_description: User-provided description of the topic.
        quiz_context: QuizContext with profile and characteristics.
        question_count: Target number of questions to generate.
        agent: Agent instance for LLM access.
    
    Returns:
        TopicCoverage with identified gaps and suggested concepts for question generation.
    """
    
    system_prompt = \
f"""
You are an expert curriculum designer and educational content strategist specializing in knowledge planning, comprehensive topic coverage, and learning objective design. Your expertise includes identifying key concepts, planning question distribution, ensuring balanced coverage, and recommending specific learning objectives for new assessments. You analyze topics systematically to create comprehensive educational coverage plans.
"""
    
    profile = quiz_context.profile
    topic = topic_description.strip() or "Custom Topic"
    
    user_prompt = \
f"""
**Task:** Analyze the topic description and plan comprehensive coverage for a new quiz, identifying key concepts and learning objectives.

**Topic Description:**
{topic}

**Quiz Profile:**
- **Complexity:** {profile.complexity}
- **Style:** {profile.style}
- **Target Audience:** {profile.target_audience}
- **Domain:** {profile.domain}
- **Language:** {profile.language}

**Target Question Count:** {question_count}

**Instructions:**
Analyze the topic comprehensively and provide:

1. **Knowledge Gaps (for planning):**
   - Since this is a new quiz, identify important subtopics, concepts, or themes that should be covered
   - Consider:
     * Foundational concepts that are essential for understanding
     * Core principles and key theories
     * Important applications and practical aspects
     * Common misconceptions or challenging areas
   - List 3-8 specific areas that should be addressed in the quiz
   - These represent "gaps" in the sense that they need to be covered

2. **Suggested Concepts for Questions:**
   - Recommend 5-10 specific, actionable concepts or learning objectives for question generation
   - These should:
     * Cover the essential aspects of the topic
     * Be appropriate for the complexity level ({profile.complexity})
     * Be suitable for the target audience ({profile.target_audience})
     * Match the style ({profile.style})
     * Be expressed in the {profile.language} language
     * Fit within the domain ({profile.domain})
     * Be distributed across foundational, intermediate, and advanced aspects (if applicable)
   - Be specific and use domain-appropriate terminology
   - Ensure concepts are distinct and non-redundant

**Guidelines:**
- Focus on concepts that provide comprehensive coverage of the topic
- Prioritize concepts that are most important for understanding
- Consider the educational progression and logical flow of topics
- Ensure concepts are appropriate for the specified complexity and audience
- Be specific rather than generic (e.g., "neural network backpropagation" not just "machine learning")
- Distribute concepts to cover different aspects: theory, application, analysis, etc.

**Output Format (JSON):**
{{
  "gaps": ["important concept to cover 1", "important concept to cover 2", "important concept to cover 3"],
  "suggested_concepts": ["specific concept 1", "specific concept 2", "specific concept 3", "specific concept 4", "specific concept 5"]
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.5,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {
        "gaps": [],
        "suggested_concepts": []
    })
    
    return TopicCoverage.from_dict(parsed)

