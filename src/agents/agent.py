"""Base agent class with common functionality for all agents."""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Constants
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7


class Agent(ABC):
    """Base class for all autonomous agents.
    
    Provides LLM client initialization, text generation, and tool management.
    """
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        tools: Optional[List[Callable]] = None
    ) -> None:
        """Initialize agent with LLM client and tools.
        
        Args:
            model: OpenRouter model identifier.
            tools: Optional list of callable tools.
        
        Raises:
            ValueError: If OPENROUTER_API_KEY is not set.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Set it in your .env file or environment."
            )
        
        self.client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        self.model = model
        self.tools: List[Callable] = tools or []
    
    def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = DEFAULT_TEMPERATURE,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text using OpenRouter API.
        
        Args:
            system_prompt: System message defining agent role and behavior.
            user_prompt: User message with the actual request.
            temperature: Sampling temperature (0.0-2.0).
            response_format: Optional format spec (e.g., {"type": "json_object"}).
        
        Returns:
            Generated text response.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if response_format:
            params["response_format"] = response_format
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content or ""
    
    def _parse_json(self, text: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON with fallback to default value.
        
        Args:
            text: JSON string to parse.
            default: Default value if parsing fails.
        
        Returns:
            Parsed JSON dictionary or default value.
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return default
    
    def _plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan strategy for autonomous decision making.
        
        Optional method for agents that need planning logic. Default implementation
        returns empty dict. Override in subclasses if planning is needed.
        
        Args:
            context: Context information for planning.
        
        Returns:
            Dictionary with planning decisions and strategy parameters.
        """
        return {}

