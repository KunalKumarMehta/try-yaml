"""Base Agent class."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm import LLMClient


@dataclass
class Agent:
    """
    An agent that can execute tasks based on its role and goal.
    
    Attributes:
        id: Unique identifier for the agent
        role: Human-readable role description
        goal: The task or objective for this agent
        tools: List of tool names available to this agent
    """
    
    id: str
    role: str
    goal: str
    tools: list[str] = field(default_factory=list)
    _llm_client: "LLMClient | None" = field(default=None, repr=False)
    
    def set_llm_client(self, client: "LLMClient") -> None:
        """Set the LLM client for this agent."""
        self._llm_client = client
    
    def execute(self, context: dict[str, str] | None = None) -> str:
        """
        Execute the agent's task with the given context.
        
        Args:
            context: Dictionary mapping agent IDs to their outputs
            
        Returns:
            The agent's response string
        """
        if self._llm_client is None:
            raise RuntimeError(f"Agent '{self.id}' has no LLM client configured")
        
        prompt = self._build_prompt(context)
        return self._llm_client.generate(prompt)
    
    async def execute_async(self, context: dict[str, str] | None = None) -> str:
        """
        Execute the agent's task asynchronously.
        
        Args:
            context: Dictionary mapping agent IDs to their outputs
            
        Returns:
            The agent's response string
        """
        if self._llm_client is None:
            raise RuntimeError(f"Agent '{self.id}' has no LLM client configured")
        
        prompt = self._build_prompt(context)
        return await self._llm_client.generate_async(prompt)
    
    def _build_prompt(self, context: dict[str, str] | None = None) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            context: Dictionary mapping agent IDs to their outputs
            
        Returns:
            Formatted prompt string
        """
        parts = [
            f"You are a {self.role}.",
            f"Your goal: {self.goal}",
        ]
        
        if self.tools:
            parts.append(f"You have access to these tools: {', '.join(self.tools)}")
        
        if context:
            parts.append("\n--- Context from previous agents ---")
            for agent_id, output in context.items():
                parts.append(f"\n[{agent_id}]:\n{output}")
            parts.append("\n--- End of context ---\n")
        
        parts.append("\nPlease complete your task based on your goal and any provided context.")
        
        return "\n".join(parts)
