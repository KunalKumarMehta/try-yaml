"""Pydantic models for YAML configuration validation."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    
    id: str = Field(..., description="Unique identifier for the agent")
    role: str = Field(..., description="Human-readable role description")
    goal: str = Field(..., description="The task or objective for this agent")
    tools: list[str] = Field(default_factory=list, description="Optional list of tools")


class WorkflowStep(BaseModel):
    """A single step in a sequential workflow."""
    
    agent: str = Field(..., description="Agent ID to execute")


class SequentialWorkflow(BaseModel):
    """Sequential workflow configuration."""
    
    type: Literal["sequential"]
    steps: list[WorkflowStep] = Field(..., min_length=1)


class ParallelWorkflow(BaseModel):
    """Parallel workflow configuration with optional aggregation."""
    
    type: Literal["parallel"]
    branches: list[str] = Field(..., min_length=1, description="Agent IDs to run in parallel")
    then: Optional[WorkflowStep] = Field(default=None, description="Optional aggregator agent")


# Union type for workflow
WorkflowConfig = SequentialWorkflow | ParallelWorkflow


class OrchestratorConfig(BaseModel):
    """Root configuration model."""
    
    agents: list[AgentConfig] = Field(..., min_length=1)
    workflow: SequentialWorkflow | ParallelWorkflow
    
    @model_validator(mode="after")
    def validate_agent_references(self) -> "OrchestratorConfig":
        """Ensure all referenced agent IDs exist."""
        agent_ids = {agent.id for agent in self.agents}
        
        # Check for duplicate agent IDs
        if len(agent_ids) != len(self.agents):
            raise ValueError("Duplicate agent IDs found")
        
        # Validate workflow references
        if isinstance(self.workflow, SequentialWorkflow):
            for step in self.workflow.steps:
                if step.agent not in agent_ids:
                    raise ValueError(f"Unknown agent ID in workflow: {step.agent}")
        elif isinstance(self.workflow, ParallelWorkflow):
            for branch in self.workflow.branches:
                if branch not in agent_ids:
                    raise ValueError(f"Unknown agent ID in branches: {branch}")
            if self.workflow.then and self.workflow.then.agent not in agent_ids:
                raise ValueError(f"Unknown agent ID in 'then': {self.workflow.then.agent}")
        
        return self
