"""Workflow executors for different execution patterns."""

import asyncio
from abc import ABC, abstractmethod
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ..agents.base import Agent
from ..config.schema import SequentialWorkflow, ParallelWorkflow
from .context import Context


console = Console()


class Executor(ABC):
    """Abstract base executor."""
    
    @abstractmethod
    def execute(
        self,
        agents: dict[str, Agent],
        context: Context,
    ) -> Context:
        """Execute the workflow and return updated context."""
        pass


class SequentialExecutor(Executor):
    """Executes agents in sequential order."""
    
    def __init__(self, workflow: SequentialWorkflow):
        """
        Initialize with workflow configuration.
        
        Args:
            workflow: Sequential workflow configuration
        """
        self.workflow = workflow
    
    def execute(
        self,
        agents: dict[str, Agent],
        context: Context,
    ) -> Context:
        """
        Execute agents sequentially, passing context forward.
        
        Args:
            agents: Dictionary of agent_id -> Agent
            context: Shared context object
            
        Returns:
            Updated context with all agent outputs
        """
        for i, step in enumerate(self.workflow.steps, 1):
            agent = agents[step.agent]
            
            console.print(f"\n[bold blue]Step {i}/{len(self.workflow.steps)}[/bold blue]")
            console.print(Panel(
                f"[bold]{agent.role}[/bold] ({agent.id})\n"
                f"[dim]Goal: {agent.goal}[/dim]",
                title="🤖 Agent Executing",
                border_style="blue"
            ))
            
            # Get context from previous agents
            agent_context = context.get_all() if context else None
            
            # Execute agent
            with console.status(f"[yellow]Thinking...[/yellow]"):
                output = agent.execute(agent_context)
            
            # Store result
            context.add_result(agent.id, output)
            
            # Display output
            console.print(Panel(
                Markdown(output),
                title=f"📝 Output from {agent.id}",
                border_style="green"
            ))
        
        return context


class ParallelExecutor(Executor):
    """Executes agents in parallel with optional aggregation."""
    
    def __init__(self, workflow: ParallelWorkflow):
        """
        Initialize with workflow configuration.
        
        Args:
            workflow: Parallel workflow configuration
        """
        self.workflow = workflow
    
    def execute(
        self,
        agents: dict[str, Agent],
        context: Context,
    ) -> Context:
        """
        Execute branch agents in parallel, then run aggregator.
        
        Args:
            agents: Dictionary of agent_id -> Agent
            context: Shared context object
            
        Returns:
            Updated context with all agent outputs
        """
        # Execute branches in parallel
        branch_agents = [agents[agent_id] for agent_id in self.workflow.branches]
        
        console.print(f"\n[bold blue]Parallel Execution[/bold blue]")
        console.print(f"Running {len(branch_agents)} agents concurrently...")
        
        for agent in branch_agents:
            console.print(Panel(
                f"[bold]{agent.role}[/bold] ({agent.id})\n"
                f"[dim]Goal: {agent.goal}[/dim]",
                title="🤖 Agent",
                border_style="blue"
            ))
        
        # Run branches in parallel using asyncio
        with console.status("[yellow]Executing parallel agents...[/yellow]"):
            results = asyncio.run(self._execute_parallel(branch_agents, context))
        
        # Store results
        for agent_id, output in results.items():
            context.add_result(agent_id, output)
            console.print(Panel(
                Markdown(output),
                title=f"📝 Output from {agent_id}",
                border_style="green"
            ))
        
        # Execute aggregator if specified
        if self.workflow.then:
            console.print(f"\n[bold blue]Aggregation Step[/bold blue]")
            
            aggregator = agents[self.workflow.then.agent]
            
            console.print(Panel(
                f"[bold]{aggregator.role}[/bold] ({aggregator.id})\n"
                f"[dim]Goal: {aggregator.goal}[/dim]",
                title="🤖 Aggregator Executing",
                border_style="magenta"
            ))
            
            # Aggregator receives outputs from all branches
            branch_context = context.get_subset(self.workflow.branches)
            
            with console.status("[yellow]Aggregating results...[/yellow]"):
                output = aggregator.execute(branch_context)
            
            context.add_result(aggregator.id, output)
            
            console.print(Panel(
                Markdown(output),
                title=f"📝 Output from {aggregator.id}",
                border_style="green"
            ))
        
        return context
    
    async def _execute_parallel(
        self,
        agents: list[Agent],
        context: Context,
    ) -> dict[str, str]:
        """
        Execute multiple agents in parallel.
        
        Args:
            agents: List of agents to execute
            context: Current context (passed to all agents)
            
        Returns:
            Dictionary of agent_id -> output
        """
        current_context = context.get_all() if context else None
        
        async def run_agent(agent: Agent) -> tuple[str, str]:
            output = await agent.execute_async(current_context)
            return agent.id, output
        
        tasks = [run_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        return dict(results)
