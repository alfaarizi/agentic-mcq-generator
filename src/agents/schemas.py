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
class ErrorEvaluation:
    """Error evaluation result from error_evaluator tool.
    
    Attributes:
        error_type: Classification of the error type.
        confidence: Confidence score (0.0-1.0).
        reasoning: Explanation of the classification.
    """
    error_type: ErrorType
    confidence: float
    reasoning: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorEvaluation":
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
class PedagogicalContext:
    """Pedagogical context information for feedback generation."""
    topic: str
    related_concepts: List[str] = field(default_factory=list)
    common_misconceptions: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PedagogicalContext":
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


@dataclass
class ResponseEvaluation:
    """Result from evaluate method."""
    feedback: "Feedback"
    error_evaluation: ErrorEvaluation
    learning_profile: "LearningProfile"
    suggestions: Optional[List["LearningSuggestion"]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "feedback": self.feedback.to_dict(),
            "error_evaluation": self.error_evaluation.to_dict(),
            "learning_profile": self.learning_profile.to_dict(),
            "suggestions": [s.to_dict() for s in self.suggestions] if self.suggestions else None
        }
        return data


# ==============================
# LEARNING
# ==============================


@dataclass
class TopicProficiency:
    """Proficiency statistics for a single topic."""
    topic: str
    error_counts: Dict[ErrorType, int] = field(default_factory=dict)
    
    @property
    def total_answers(self) -> int:
        """Total answers for this topic."""
        return sum(self.error_counts.values())
    
    @property
    def correct_answers(self) -> int:
        """Number of correct answers."""
        return self.error_counts.get(ErrorType.CORRECT, 0)
    
    @property
    def accuracy(self) -> float:
        """Accuracy ratio (0.0-1.0)."""
        return self.correct_answers / self.total_answers if self.total_answers > 0 else 0.0
    
    def get_error_count(self, error_type: ErrorType) -> int:
        """Get count for a specific error type."""
        return self.error_counts.get(error_type, 0)


@dataclass
class LearningProfile:
    """User learning performance profile."""
    topic_proficiencies: List[TopicProficiency] = field(default_factory=list)
    
    @property
    def total_answers(self) -> int:
        """Total answers across all topics."""
        return sum(tp.total_answers for tp in self.topic_proficiencies)
    
    @property
    def struggling_topics(self) -> Dict[str, float]:
        """Topics with accuracy < 0.5."""
        return {tp.topic: tp.accuracy for tp in self.topic_proficiencies if tp.accuracy < 0.5}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningProfile":
        """Create from dictionary."""
        topic_proficiencies = []
        topic_proficiencies_data = data.get("topic_proficiencies", {})
        for topic, stats in topic_proficiencies_data.items():
            topic_proficiencies.append(TopicProficiency(
                topic=topic,
                error_counts={ErrorType(k): v for k, v in stats.items()}
            ))
        return cls(topic_proficiencies=topic_proficiencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        topic_proficiencies = {
            tp.topic: {k.value: v for k, v in tp.error_counts.items()}
            for tp in self.topic_proficiencies
        }
        return {"topic_proficiencies": topic_proficiencies}


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
class QuizContext:
    """Context extracted from quiz_context_extractor tool."""
    profile: QuizProfile
    covered_concepts: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizContext":
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
class TopicCoverage:
    """Topic coverage analysis result from topic_coverage_analyzer tool."""
    gaps: List[str] = field(default_factory=list)
    suggested_concepts: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopicCoverage":
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
