"""Tool for generating AI-powered learning suggestions and tracking progress."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ..schemas import ErrorEvaluation, ErrorType, PedagogicalContext, LearningProfile, LearningSuggestion, TopicProficiency


def generate_suggestions(
    question: "Question",
    error_analysis: ErrorEvaluation,
    topic: str,
    learning_profile: LearningProfile,
    eval_context: PedagogicalContext,
    agent: "Agent"
) -> List[LearningSuggestion]:
    """Generate AI-powered learning suggestions and update learning profile.
    
    Args:
        question: The question answered.
        error_analysis: Error analysis result.
        topic: Topic of the quiz.
        learning_profile: Current user learning profile (modified in place).
        eval_context: Context information.
        agent: Agent instance for LLM access.
    
    Returns:
        List of AI-generated learning suggestions. Profile is updated in place.
    """
    err_type = error_analysis.error_type
    
    # Update learning profile
    topic_entry = next((tp for tp in learning_profile.topic_proficiencies if tp.topic == topic), None)
    if topic_entry is None:
        topic_entry = TopicProficiency(topic=topic)
        learning_profile.topic_proficiencies.append(topic_entry)
    topic_entry.error_counts[err_type] = topic_entry.error_counts.get(err_type, 0) + 1
    
    # Generate suggestions
    if err_type == ErrorType.CORRECT:
        system_prompt = \
f"""
You are an encouraging learning coach and academic advisor specializing in student motivation and continued learning. Your expertise includes recognizing achievement, providing positive reinforcement, and guiding students toward advanced learning opportunities. You help students build on their successes and maintain momentum.
"""
        
        user_prompt = \
f"""
**Task:** Generate encouraging, forward-looking learning suggestions for a student who answered correctly.

**Context:**
- **Topic:** {topic}
- **Question:** {question.text}
- **Performance:** Student answered correctly

**Instructions:**
Generate 1-2 brief, encouraging suggestions that:
- Acknowledge their success positively
- Suggest next steps for continued learning
- Recommend resources or activities to deepen understanding
- Maintain motivation and engagement

**Guidelines:**
- Be specific and actionable
- Focus on building on their success
- Suggest resources that are relevant and accessible
- Keep tone positive and encouraging

**Output Format (JSON):**
{{
  "suggestions": [
    {{
      "title": "Brief, actionable title (5-8 words)",
      "explanation": "What to learn next and why it's valuable (2-3 sentences)",
      "resources": ["resource name or URL 1", "resource name or URL 2"]
    }}
  ]
}}
"""
    else:
        struggling_topics_str = ", ".join(list(learning_profile.struggling_topics.keys())[:3]) if learning_profile.struggling_topics else "None identified"
        mistake_count = sum(tp.get_error_count(err_type) for tp in learning_profile.topic_proficiencies)
        related_concepts_str = ", ".join(eval_context.related_concepts[:3]) if eval_context.related_concepts else "None identified"
        
        system_prompt = \
f"""
You are an expert learning advisor and educational consultant specializing in personalized learning pathways and adaptive instruction. Your expertise includes diagnosing learning gaps, recommending targeted resources, and creating individualized study plans. You provide actionable, evidence-based recommendations that address specific learning needs.
"""
        
        user_prompt = \
f"""
**Task:** Generate personalized, actionable learning suggestions to help the student improve their understanding.

**Learning Context:**
- **Topic:** {topic}
- **Question:** {question.text}
- **Error Type:** {err_type}
- **Error Analysis:** {error_analysis.reasoning}

**Student Performance Data:**
- **Related Concepts:** {related_concepts_str}
- **Struggling Topics:** {struggling_topics_str}
- **Frequency of This Error Type:** {mistake_count} time(s) across all topics

**Instructions:**
Generate 2-3 personalized learning suggestions that:
- Address the specific error type and reasoning
- Consider the student's struggling topics and error patterns
- Provide concrete, actionable steps
- Include specific, relevant learning resources

**For Each Suggestion, Include:**
1. **Title:** Brief, actionable title (5-8 words) that clearly states what to do
2. **Explanation:** What to learn, why it matters, and how it addresses their specific error (2-3 sentences)
3. **Resources:** 1-2 specific learning resources (prefer real URLs to articles, tutorials, videos, or practice materials; if URLs aren't available, use descriptive resource names)

**Guidelines:**
- Prioritize suggestions that directly address the error type
- Consider the student's learning history and patterns
- Be specific and actionable (avoid vague advice)
- Focus on resources that are accessible and appropriate for the topic
- Maintain a supportive, encouraging tone

**Output Format (JSON):**
{{
  "suggestions": [
    {{
      "title": "Specific, actionable title",
      "explanation": "What to learn, why it helps, and how it addresses their error (2-3 sentences)",
      "resources": ["resource URL or name 1", "resource URL or name 2"]
    }},
    {{
      "title": "Another specific suggestion",
      "explanation": "Another learning opportunity (2-3 sentences)",
      "resources": ["resource URL or name"]
    }}
  ]
}}
"""
    
    resp = agent._generate(
        system_prompt,
        user_prompt,
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    parsed = agent._parse_json(resp, {"suggestions": []})
    suggestions_data = parsed.get("suggestions", [])
    
    if not suggestions_data:
        if err_type == ErrorType.CORRECT:
            return [
                LearningSuggestion(
                    title="Great work!",
                    explanation="You're making excellent progress. Keep practicing to reinforce your understanding.",
                    resources=[]
                )
            ]
        else:
            return [
                LearningSuggestion(
                    title="Continue Learning",
                    explanation=f"Review the concepts related to {topic} and practice similar questions.",
                    resources=[]
                )
            ]
    
    suggestions = []
    for item in suggestions_data[:3]:
        suggestions.append(LearningSuggestion(
            title=item.get("title", "Learning suggestion"),
            explanation=item.get("explanation", ""),
            resources=item.get("resources", [])
        ))
    
    return suggestions

