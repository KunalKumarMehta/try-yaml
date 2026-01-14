"""LLM client implementations."""

import os
from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response synchronously."""
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str) -> str:
        """Generate a response asynchronously."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            model: Model name to use
            api_key: API key (defaults to OPENAI_API_KEY env var)
            temperature: Sampling temperature
        """
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.temperature = temperature
        self._client = None
        self._async_client = None
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    def _get_client(self):
        """Lazy initialization of sync client."""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def _get_async_client(self):
        """Lazy initialization of async client."""
        if self._async_client is None:
            from openai import AsyncOpenAI
            self._async_client = AsyncOpenAI(api_key=self.api_key)
        return self._async_client
    
    def generate(self, prompt: str) -> str:
        """Generate a response using OpenAI API."""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""
    
    async def generate_async(self, prompt: str) -> str:
        """Generate a response asynchronously using OpenAI API."""
        client = self._get_async_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing without API calls.
    
    Returns deterministic responses based on the prompt content.
    """
    
    def __init__(self, responses: Optional[dict[str, str]] = None):
        """
        Initialize with optional custom responses.
        
        Args:
            responses: Dict mapping keywords to responses
        """
        self.responses = responses or {}
        self.call_history: list[str] = []
    
    def generate(self, prompt: str) -> str:
        """Generate a mock response."""
        self.call_history.append(prompt)
        
        # Check for custom responses
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        # Default mock response
        return self._default_response(prompt)
    
    async def generate_async(self, prompt: str) -> str:
        """Generate a mock response asynchronously."""
        return self.generate(prompt)
    
    def _default_response(self, prompt: str) -> str:
        """Generate a default response based on prompt patterns."""
        if "research" in prompt.lower():
            return (
                "## Research Findings\n\n"
                "Based on my analysis, here are the key insights:\n"
                "1. Electric vehicles are becoming increasingly popular\n"
                "2. Battery technology is improving rapidly\n"
                "3. Charging infrastructure is expanding globally"
            )
        elif "write" in prompt.lower() or "summary" in prompt.lower():
            return (
                "## Summary\n\n"
                "The electric vehicle industry is experiencing rapid growth. "
                "Advances in battery technology and expanding charging networks "
                "are making EVs more accessible to consumers worldwide."
            )
        elif "backend" in prompt.lower() or "api" in prompt.lower():
            return (
                "## API Design Proposal\n\n"
                "```\n"
                "POST /api/tasks - Create a new task\n"
                "GET /api/tasks - List all tasks\n"
                "PUT /api/tasks/:id - Update a task\n"
                "DELETE /api/tasks/:id - Delete a task\n"
                "```"
            )
        elif "frontend" in prompt.lower() or "ui" in prompt.lower():
            return (
                "## UI Layout Proposal\n\n"
                "- Header with navigation\n"
                "- Sidebar for task categories\n"
                "- Main area with task list and details\n"
                "- Footer with quick actions"
            )
        elif "review" in prompt.lower() or "consolidate" in prompt.lower():
            return (
                "## Consolidated Review\n\n"
                "Both proposals are well-structured. "
                "The API design aligns with RESTful best practices, "
                "and the UI layout provides good user experience. "
                "Recommendation: Proceed with implementation."
            )
        else:
            return f"[Mock response for prompt length: {len(prompt)} chars]"


def create_llm_client(
    provider: str = "openai",
    use_mock: bool = False,
    **kwargs
) -> LLMClient:
    """
    Factory function to create LLM clients.
    
    Args:
        provider: LLM provider name ("openai")
        use_mock: If True, use mock client for testing
        **kwargs: Additional arguments for the client
        
    Returns:
        LLMClient instance
    """
    if use_mock:
        return MockLLMClient(responses=kwargs.get("mock_responses"))
    
    if provider == "openai":
        return OpenAIClient(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
