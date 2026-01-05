"""Data schemas for agent operations.

Defines clear data structures for parameters and return types.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import StrEnum

from ..models import Question, Choice


# ==============================
# ERROR
# ==============================

class ErrorType(StrEnum):
    """Error type classification."""
    CORRECT = "correct"
    CONCEPTUAL_MISUNDERSTANDING = "conceptual_misunderstanding"
    PARTIAL_UNDERSTANDING = "partial_understanding"
    TERMINOLOGY_CONFUSION = "terminology_confusion"
    APPLICATION_ERROR = "application_error"
    CARELESS_MISTAKE = "careless_mistake"
    
    @classmethod
    def _missing_(cls, value: object) -> "ErrorType":
        """Handle unknown values by defaulting to CONCEPTUAL_MISUNDERSTANDING."""
        return cls.CONCEPTUAL_MISUNDERSTANDING

@dataclass
class ErrorAnalysis:
    """Error analysis result from error_analyzer tool.
    
    Attributes:
        error_type: Classification of the error type.
        confidence: Confidence score (0.0-1.0).
        reasoning: Explanation of the classification.
    """
    error_type: ErrorType
    confidence: float
    reasoning: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorAnalysis":
        """Create from dictionary."""
        return cls(
            error_type=ErrorType(data.get("error_type", "conceptual_misunderstanding")),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


# ==============================
# EVALUATION
# ==============================

@dataclass
class EvaluationContext:
    """Context information for feedback generation."""
    topic: str
    related_concepts: List[str] = field(default_factory=list)
    common_misconceptions: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationContext":
        """Create from dictionary."""
        return cls(
            topic=data.get("topic", ""),
            related_concepts=data.get("related_concepts", []),
            common_misconceptions=data.get("common_misconceptions", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "related_concepts": self.related_concepts,
            "common_misconceptions": self.common_misconceptions
        }


@dataclass
class Feedback:
    """Structured feedback for an answer."""
    concept: str
    explanation: str
    key_points: List[str] = field(default_factory=list)
    hints: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "concept": self.concept,
            "explanation": self.explanation,
            "key_points": self.key_points,
            "hints": self.hints
        }
    
    def to_string(self) -> str:
        """Convert to formatted string for backward compatibility."""
        parts = [
            f"<mark>{self.concept}</mark>",
            self.explanation
        ]
        if self.key_points:
            points = "\n".join(f"• {p}" for p in self.key_points)
            parts.append(f"<u>Key Points:</u>\n{points}")
        if self.hints:
            hints_text = "\n".join(f"💡 {h}" for h in self.hints)
            parts.append(f"<u>Hints:</u>\n{hints_text}")
        return "\n\n".join(parts)


@dataclass
class EvaluationResult:
    """Result from evaluate method."""
    feedback: "Feedback"
    error_analysis: ErrorAnalysis
    learning_history: "LearningHistory"
    suggestions: Optional[List["LearningSuggestion"]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "explanation": self.feedback.to_string(),  # For backward compatibility
            "feedback": self.feedback.to_dict(),
            "error_analysis": self.error_analysis.to_dict(),
            "learning_history": self.learning_history.to_dict(),
            "suggestions": [s.to_dict() for s in self.suggestions] if self.suggestions else None
        }
        return data


# ==============================
# LEARNING
# ==============================


@dataclass
class TopicStats:
    """Statistics for a single topic."""
    topic: str
    stats: Dict[ErrorType, int] = field(default_factory=dict)
    
    @property
    def total_questions(self) -> int:
        """Total questions answered for this topic."""
        return sum(self.stats.values())
    
    @property
    def correct_answers(self) -> int:
        """Number of correct answers."""
        return self.stats.get(ErrorType.CORRECT, 0)
    
    @property
    def accuracy(self) -> float:
        """Accuracy ratio (0.0-1.0)."""
        return self.correct_answers / self.total_questions if self.total_questions > 0 else 0.0
    
    def get_count(self, error_type: ErrorType) -> int:
        """Get count for a specific error type."""
        return self.stats.get(error_type, 0)


@dataclass
class LearningHistory:
    """User learning performance history."""
    topics: List[TopicStats] = field(default_factory=list)
    
    @property
    def total_questions(self) -> int:
        """Total questions answered across all topics."""
        return sum(ts.total_questions for ts in self.topics)
    
    @property
    def struggling_topics(self) -> Dict[str, float]:
        """Topics with accuracy < 0.5."""
        return {ts.topic: ts.accuracy for ts in self.topics if ts.accuracy < 0.5}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningHistory":
        """Create from dictionary."""
        topics = []
        topic_stats = data.get("topic_stats", {})
        for topic, stats in topic_stats.items():
            topics.append(TopicStats(
                topic=topic,
                stats={ErrorType(k): v for k, v in stats.items()}
            ))
        return cls(topics=topics)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        topic_stats = {
            ts.topic: {k.value: v for k, v in ts.stats.items()}
            for ts in self.topics
        }
        return {"topic_stats": topic_stats}


@dataclass
class LearningSuggestion:
    """AI-generated learning suggestion."""
    title: str
    explanation: str
    resources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "explanation": self.explanation,
            "resources": self.resources
        }


# ==============================
# AUGMENTATION
# ==============================

class Complexity(StrEnum):
    """Question difficulty and depth."""
    BEGINNER = "beginner"               # Basic concepts, minimal prerequisite knowledge, simple recall or comprehension
    INTERMEDIATE = "intermediate"       # Moderate depth, some prerequisite knowledge expected, application of concepts
    ADVANCED = "advanced"               # Deep understanding required, significant prerequisite knowledge, analysis and synthesis
    EXPERT = "expert"                   # Specialized knowledge, complex reasoning, evaluation and creation of new understanding
    
    @classmethod
    def _missing_(cls, value: object) -> "Complexity":
        """Handle unknown values by defaulting to INTERMEDIATE."""
        return cls.INTERMEDIATE


class Style(StrEnum):
    """Question presentation approach."""
    ACADEMIC = "academic"               # Formal, precise, scholarly language, uses technical terminology, structured presentation, emphasizes theoretical understanding
    CONVERSATIONAL = "conversational"   # Friendly, explanatory, accessible tone, uses everyday language, includes context and background, encourages understanding through dialogue
    PRACTICAL = "practical"             # Applied, scenario-based, real-world focus, emphasizes hands-on application, uses examples from actual use cases, connects theory to practice
    CONCISE = "concise"                 # Direct, minimal explanation, to-the-point, focuses on essential information, avoids elaboration, efficient and straightforward communication
    
    @classmethod
    def _missing_(cls, value: object) -> "Style":
        """Handle unknown values by defaulting to ACADEMIC."""
        return cls.ACADEMIC


class TargetAudience(StrEnum):
    """Educational/professional level."""
    HIGH_SCHOOL = "high_school"         # Secondary education level, foundational knowledge, age-appropriate terminology
    UNDERGRADUATE = "undergraduate"     # College/university level, intermediate depth, assumes some prior coursework
    GRADUATE = "graduate"               # Advanced academic level, specialized knowledge, research-oriented expectations
    PROFESSIONAL = "professional"       # Industry/workplace context, practical application, professional terminology
    GENERAL = "general"                 # Broad public audience, accessible to non-specialists, minimal assumptions about prior knowledge
    
    @classmethod
    def _missing_(cls, value: object) -> "TargetAudience":
        """Handle unknown values by defaulting to UNDERGRADUATE."""
        return cls.UNDERGRADUATE


@dataclass
class QuizProfile:
    """Core characteristics of a quiz/topic shared across workflows."""
    complexity: Complexity = Complexity.INTERMEDIATE
    language: str = "en"
    domain: str = "general"
    style: Style = Style.ACADEMIC
    target_audience: TargetAudience = TargetAudience.UNDERGRADUATE
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizProfile":
        """Create from dictionary."""
        return cls(
            complexity=Complexity(data.get("complexity", "intermediate")),
            language=data.get("language", "en"),
            domain=data.get("domain", "general"),
            style=Style(data.get("style", "academic")),
            target_audience=TargetAudience(data.get("target_audience", "undergraduate"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "complexity": self.complexity,
            "language": self.language,
            "domain": self.domain,
            "style": self.style,
            "target_audience": self.target_audience
        }


@dataclass
class QuizAnalysis:
    """Analysis result from quiz_analyzer tool."""
    profile: QuizProfile
    covered_concepts: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizAnalysis":
        """Create from dictionary."""
        return cls(
            profile=QuizProfile.from_dict(data),
            covered_concepts=data.get("covered_concepts", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = self.profile.to_dict()
        result.update({
            "covered_concepts": self.covered_concepts
        })
        return result


@dataclass
class CoverageAnalysis:
    """Coverage gap analysis result from coverage_analyzer tool."""
    gaps: List[str] = field(default_factory=list)
    suggested_concepts: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoverageAnalysis":
        """Create from dictionary."""
        return cls(
            gaps=data.get("gaps", []),
            suggested_concepts=data.get("suggested_concepts", [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gaps": self.gaps,
            "suggested_concepts": self.suggested_concepts
        }


@dataclass
class QuestionValidation:
    """Validation result from question_validator tool."""
    valid_questions: List[Question] = field(default_factory=list)
    invalid_questions: List[Question] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Note: Serializes questions as text only for API responses.
        Full Question objects are preserved in the dataclass.
        """
        return {
            "valid_questions": [q.text for q in self.valid_questions],
            "invalid_questions": [q.text for q in self.invalid_questions]
        }
