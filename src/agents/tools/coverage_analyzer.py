"""Tool for analyzing quiz coverage gaps and planning additional questions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Quiz

from ..schemas import QuizAnalysis, CoverageAnalysis, QuizProfile


def analyze_coverage(
    quiz: "Quiz",
    quiz_analysis: QuizAnalysis,
    agent: "Agent",
    target_count: int = 15
) -> CoverageAnalysis:
    """Analyze quiz coverage gaps and plan additional questions.
    
    Args:
        quiz: The existing quiz.
        quiz_analysis: Result from quiz_analyzer tool.
        agent: Agent instance for LLM access.
        target_count: Target number of additional questions to generate.
    
    Returns:
        CoverageAnalysis with gap analysis and question generation plan.
    """
    
    system_prompt = \
f"""
You are an expert curriculum designer and educational content strategist specializing in knowledge gap analysis and comprehensive learning coverage. Your expertise includes identifying missing concepts, planning question distribution, ensuring balanced topic coverage, and recommending specific learning objectives for assessment. You analyze existing content systematically to identify opportunities for educational enhancement.
"""
    
    covered_concepts = ", ".join(quiz_analysis.covered_concepts[:10])
    topic = quiz.topic
    existing_count = len(quiz.questions)
    profile = quiz_analysis.profile
    
    user_prompt = \
f"""
**Task:** Analyze knowledge gaps in the existing quiz and recommend specific concepts for additional question generation.

**Quiz Context:**
- **Topic:** {topic}
- **Existing Questions:** {existing_count}
- **Target Additional Questions:** {target_count}
- **Current Complexity Level:** {profile.complexity}
- **Domain:** {profile.domain}
- **Target Audience:** {profile.target_audience}

**Currently Covered Concepts:**
{covered_concepts or "None explicitly identified"}

**Instructions:**
Analyze the quiz systematically to identify gaps and opportunities:

1. **Identify Knowledge Gaps:**
   - Review the topic comprehensively and identify subtopics, concepts, or themes that are:
     * Not yet covered in existing questions
     * Under-represented (mentioned but not deeply tested)
     * Important for comprehensive understanding of the topic
   - Consider prerequisite concepts, foundational principles, and advanced applications
   - List 3-6 specific gaps that would benefit from additional questions

2. **Suggest Concepts for New Questions:**
   - Recommend 3-6 specific, actionable concepts or themes for new questions
   - These should:
     * Address identified gaps
     * Be appropriate for the complexity level ({profile.complexity})
     * Be suitable for the target audience ({profile.target_audience})
     * Fit within the domain ({profile.domain})
   - Be specific and use domain-appropriate terminology

**Guidelines:**
- Focus on concepts that would meaningfully enhance quiz coverage
- Prioritize gaps that are most important for comprehensive understanding
- Ensure suggested concepts are distinct from already-covered concepts
- Consider the educational progression and logical flow of topics
- Be specific rather than generic (e.g., "neural network backpropagation" not just "machine learning")

**Output Format (JSON):**
{{
  "gaps": ["specific gap 1", "specific gap 2", "specific gap 3"],
  "suggested_concepts": ["specific concept 1", "specific concept 2", "specific concept 3"]
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
    
    return CoverageAnalysis.from_dict(parsed)

