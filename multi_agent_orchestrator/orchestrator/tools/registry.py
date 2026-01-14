"""Tool registry for managing available tools."""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for registration."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for agent context."""
        pass
    
    @abstractmethod
    def execute(self, input_data: str) -> str:
        """
        Execute the tool with given input.
        
        Args:
            input_data: Input string for the tool
            
        Returns:
            Tool output string
        """
        pass


class ToolRegistry:
    """Registry for managing tools available to agents."""
    
    _instance: "ToolRegistry | None" = None
    
    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> BaseTool | None:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())
    
    def get_tool_descriptions(self, tool_names: list[str]) -> str:
        """
        Get descriptions for specified tools.
        
        Args:
            tool_names: List of tool names
            
        Returns:
            Formatted string with tool descriptions
        """
        descriptions = []
        for name in tool_names:
            tool = self._tools.get(name)
            if tool:
                descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)


# Global registry instance
registry = ToolRegistry()
