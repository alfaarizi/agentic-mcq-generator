"""Tool for generating AI-powered learning suggestions and tracking progress."""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..agent import Agent
    from ...models import Question

from ..schemas import ErrorEvaluation, ErrorType, PedagogicalContext, LearningProfile, LearningSuggestion, TopicProficiency, QuizContext


def generate_suggestions(
    question: "Question",
    error_analysis: ErrorEvaluation,
    topic: str,
    learning_profile: LearningProfile,
    pedagogical_context: PedagogicalContext,
    agent: "Agent",
    quiz_context: Optional["QuizContext"] = None
) -> List[LearningSuggestion]:
    """Generate AI-powered learning suggestions and update learning profile.
    
    Args:
        question: The question answered.
        error_analysis: Error evaluation result.
        topic: Topic of the quiz.
        learning_profile: Current user learning profile (modified in place).
        eval_context: Pedagogical context information.
        agent: Agent instance for LLM access.
        quiz_context: Optional quiz context (style, complexity, language, etc.) to adapt suggestions.
    
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
    
    # Style description
    style_descriptions = {
        "academic": "formal, precise, scholarly language",
        "conversational": "friendly, explanatory, accessible tone",
        "practical": "applied, scenario-based, real-world focus",
        "concise": "direct, minimal explanation, to-the-point"
    }

    # Build adaptation requirements section if quiz_context is provided
    adaptation_requirements = ""
    if quiz_context:
        style_desc = style_descriptions.get(quiz_context.profile.style, "clear, accessible language")
        adaptation_requirements = f"""
**Adaptation Requirements:**
- Match the quiz's communication style ({quiz_context.profile.style}) - use {style_desc}
- Recommend resources appropriate for {quiz_context.profile.complexity} level
- Tailor suggestions for {quiz_context.profile.target_audience} level
- Provide resources in {quiz_context.profile.language} language
- Focus on {quiz_context.profile.domain} domain when relevant
"""

    # Generate suggestions
    if err_type == ErrorType.CORRECT:
        system_prompt = \
f"""
You are an encouraging learning coach and academic advisor specializing in student motivation and continued learning. Your expertise includes recognizing achievement, providing positive reinforcement, and guiding students toward advanced learning opportunities.
"""
        
        user_prompt = \
f"""
**Task:** Generate encouraging, forward-looking learning suggestions for a student who answered correctly.

**Learning Situation:**
- **Topic:** {topic}
- **Question:** {question.text}
- **Performance:** Student answered correctly

**Instructions:**
Generate 1-2 brief, encouraging suggestions that:
- Acknowledge their success positively
- Suggest next steps for continued learning
- Recommend resources or activities to deepen understanding
- Maintain motivation and engagement

{adaptation_requirements}

**Guidelines:**
- Be specific and actionable
- Focus on building on their success
- Suggest resources that are relevant and accessible
- Keep tone positive and encouraging

**Formatting Guidelines:**
Use markdown formatting to enhance readability and emphasize important information:
- **Bold** (`**text**`): Use for key learning objectives, important concepts, or action items
- *Italic* (`*text*`): Use for emphasis or subtle highlights
- `Inline code` (`` `code` ``): Use for technical terms, function names, or short code snippets
- Code blocks (```` ```language\ncode\n```` ```): Use for longer code examples or multi-line snippets when demonstrating concepts. Example: `` ```python\ndef example():\n    pass\n``` ``
- **Spacing**: Single line breaks are preserved. For additional spacing, use HTML: `<br>` for line breaks, `&nbsp;` for extra spaces, or multiple line breaks for paragraph spacing.
- Use formatting judiciously—only when it adds clarity or emphasis

Examples:
- "Master **recursive algorithms** to understand how functions call themselves."
- "Practice implementing `data structures` like stacks and queues."
- "Focus on *understanding the underlying principles* rather than memorizing syntax."

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
        related_concepts_str = ", ".join(pedagogical_context.related_concepts[:3]) if pedagogical_context.related_concepts else "None identified"
        
        system_prompt = \
f"""
You are an expert learning advisor and educational consultant specializing in personalized learning pathways and adaptive instruction. Your expertise includes diagnosing learning gaps, recommending targeted resources, and creating individualized study plans. You provide actionable, evidence-based recommendations that address specific learning needs.
"""
        
        user_prompt = \
f"""
**Task:** Generate personalized, actionable learning suggestions to help the student improve their understanding.

**Learning Situation:**
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

{adaptation_requirements}

**For Each Suggestion, Include:**
1. **Title:** Brief, actionable title (5-8 words) that clearly states what to do, using language appropriate for the quiz's style
2. **Explanation:** What to learn, why it matters, and how it addresses their specific error (2-3 sentences), written in a tone matching the quiz's style
3. **Resources:** 1-2 specific learning resources (prefer real URLs to articles, tutorials, videos, or practice materials; if URLs aren't available, use descriptive resource names) that match the complexity level and language

**Guidelines:**
- Prioritize suggestions that directly address the error type
- Consider the student's learning history and patterns
- Be specific and actionable (avoid vague advice)
- Focus on resources that are accessible and appropriate for the topic
- Maintain a supportive, encouraging tone

**Formatting Guidelines:**
Use markdown formatting to enhance readability and emphasize important information:
- **Bold** (`**text**`): Use for key learning objectives, important concepts, critical terms, or action items
- *Italic* (`*text*`): Use for emphasis, definitions, or subtle highlights
- `Inline code` (`` `code` ``): Use for technical terms, function names, variables, or short code snippets
- Code blocks (```` ```language\ncode\n```` ```): Use for longer code examples or multi-line snippets when demonstrating concepts. Example: `` ```python\ndef example():\n    pass\n``` ``
- **Spacing**: Single line breaks are preserved. For additional spacing, use HTML: `<br>` for line breaks, `&nbsp;` for extra spaces, or multiple line breaks for paragraph spacing.
- Use formatting judiciously—only when it adds clarity or emphasis, not excessively

Examples:
- "Focus on understanding **method resolution order** in Python inheritance."
- "Practice implementing `recursive functions` to solve tree traversal problems."
- "Review the *fundamental principles* before moving to advanced topics."
- For code examples: Use code blocks when showing implementation patterns or longer snippets

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

