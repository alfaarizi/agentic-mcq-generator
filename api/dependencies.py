"""Shared dependencies for API routes.

This module provides dependency injection functions for FastAPI routes.
"""

from functools import lru_cache
from typing import Dict, Any

from api.config import settings
from src.storage import QuizStorage
from src.quiz_ai import QuizAI

# In-memory session storage
_sessions: Dict[str, Any] = {}

# In-memory quiz context cache (keyed by slug)
_quiz_contexts: Dict[str, Any] = {}


@lru_cache()
def get_storage() -> QuizStorage:
    """Get cached quiz storage instance.
    
    Returns:
        QuizStorage: Singleton storage instance
    """
    return QuizStorage()


@lru_cache()
def get_ai() -> QuizAI:
    """Get cached AI service instance.
    
    Returns:
        QuizAI: Singleton AI service instance
    """
    return QuizAI()


def get_sessions() -> Dict[str, Any]:
    """Get in-memory sessions dictionary.
    
    Returns:
        Dict[str, Any]: Session storage dictionary
    """
    return _sessions


def get_quiz_contexts() -> Dict[str, Any]:
    """Get in-memory quiz contexts cache.
    
    Returns:
        Dict[str, Any]: Quiz context cache dictionary (keyed by slug)
    """
    return _quiz_contexts