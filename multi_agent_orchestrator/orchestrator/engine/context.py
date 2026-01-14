"""Context management for agent communication."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class Context:
    """
    Manages shared context between agents during workflow execution.
    
    Stores agent outputs and provides context retrieval for downstream agents.
    """
    
    _results: dict[str, str] = field(default_factory=dict)
    _execution_order: list[str] = field(default_factory=list)
    
    def add_result(self, agent_id: str, output: str) -> None:
        """
        Add an agent's output to the context.
        
        Args:
            agent_id: The ID of the agent
            output: The agent's output string
        """
        self._results[agent_id] = output
        if agent_id not in self._execution_order:
            self._execution_order.append(agent_id)
    
    def get_result(self, agent_id: str) -> str | None:
        """
        Get a specific agent's output.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The agent's output, or None if not found
        """
        return self._results.get(agent_id)
    
    def get_context_for(self, agent_id: str) -> dict[str, str]:
        """
        Get all context available for a specific agent.
        
        Returns all outputs from agents that executed before this one.
        
        Args:
            agent_id: The ID of the agent requesting context
            
        Returns:
            Dictionary of agent_id -> output for all previous agents
        """
        context = {}
        for prev_id in self._execution_order:
            if prev_id == agent_id:
                break
            context[prev_id] = self._results[prev_id]
        return context
    
    def get_all(self) -> dict[str, str]:
        """
        Get all stored results.
        
        Returns:
            Dictionary of all agent_id -> output pairs
        """
        return dict(self._results)
    
    def get_subset(self, agent_ids: list[str]) -> dict[str, str]:
        """
        Get results for a specific subset of agents.
        
        Args:
            agent_ids: List of agent IDs to include
            
        Returns:
            Dictionary of agent_id -> output for specified agents
        """
        return {
            agent_id: self._results[agent_id]
            for agent_id in agent_ids
            if agent_id in self._results
        }
    
    def clear(self) -> None:
        """Clear all stored context."""
        self._results.clear()
        self._execution_order.clear()
    
    def __iter__(self) -> Iterator[tuple[str, str]]:
        """Iterate over results in execution order."""
        for agent_id in self._execution_order:
            yield agent_id, self._results[agent_id]
    
    def __len__(self) -> int:
        """Return number of stored results."""
        return len(self._results)
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if an agent's result is stored."""
        return agent_id in self._results
