"""Main orchestrator that ties everything together."""

from pathlib import Path
from typing import Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config.parser import parse_config, ConfigError
from ..config.schema import OrchestratorConfig, SequentialWorkflow, ParallelWorkflow
from ..agents.base import Agent
from ..agents.llm import LLMClient, create_llm_client
from .context import Context
from .executor import SequentialExecutor, ParallelExecutor


console = Console()


class Orchestrator:
    """
    Main orchestration engine.
    
    Parses YAML configuration, instantiates agents, and executes workflows.
    """
    
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        use_mock: bool = False,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            llm_client: Optional LLM client (created automatically if not provided)
            use_mock: If True, use mock LLM client for testing
        """
        self.use_mock = use_mock
        self._llm_client = llm_client
    
    @property
    def llm_client(self) -> LLMClient:
        """Get or create the LLM client."""
        if self._llm_client is None:
            self._llm_client = create_llm_client(use_mock=self.use_mock)
        return self._llm_client
    
    def run(self, config_path: Union[str, Path]) -> dict[str, str]:
        """
        Run a workflow from a YAML configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Dictionary of all agent outputs
        """
        # Parse configuration
        console.print(Panel(
            f"[bold]Loading configuration from:[/bold]\n{config_path}",
            title="📄 Configuration",
            border_style="cyan"
        ))
        
        try:
            config = parse_config(config_path)
        except ConfigError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise
        
        return self.run_config(config)
    
    def run_config(self, config: OrchestratorConfig) -> dict[str, str]:
        """
        Run a workflow from a parsed configuration.
        
        Args:
            config: Parsed orchestrator configuration
            
        Returns:
            Dictionary of all agent outputs
        """
        # Display workflow info
        self._display_workflow_info(config)
        
        # Create agents
        agents = self._create_agents(config)
        
        # Create context
        context = Context()
        
        # Create and run executor
        if isinstance(config.workflow, SequentialWorkflow):
            executor = SequentialExecutor(config.workflow)
        elif isinstance(config.workflow, ParallelWorkflow):
            executor = ParallelExecutor(config.workflow)
        else:
            raise ValueError(f"Unknown workflow type: {type(config.workflow)}")
        
        console.print("\n" + "=" * 60)
        console.print("[bold green]🚀 Starting Workflow Execution[/bold green]")
        console.print("=" * 60)
        
        # Execute
        context = executor.execute(agents, context)
        
        # Display final results
        console.print("\n" + "=" * 60)
        console.print("[bold green]✅ Workflow Completed[/bold green]")
        console.print("=" * 60)
        
        return context.get_all()
    
    def _create_agents(self, config: OrchestratorConfig) -> dict[str, Agent]:
        """
        Create Agent instances from configuration.
        
        Args:
            config: Parsed configuration
            
        Returns:
            Dictionary of agent_id -> Agent
        """
        agents = {}
        
        for agent_config in config.agents:
            agent = Agent(
                id=agent_config.id,
                role=agent_config.role,
                goal=agent_config.goal,
                tools=agent_config.tools,
            )
            agent.set_llm_client(self.llm_client)
            agents[agent.id] = agent
        
        return agents
    
    def _display_workflow_info(self, config: OrchestratorConfig) -> None:
        """Display information about the workflow."""
        # Agents table
        table = Table(title="Agents", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="bold")
        table.add_column("Role")
        table.add_column("Goal")
        table.add_column("Tools")
        
        for agent in config.agents:
            tools = ", ".join(agent.tools) if agent.tools else "-"
            table.add_row(agent.id, agent.role, agent.goal, tools)
        
        console.print(table)
        
        # Workflow info
        workflow = config.workflow
        if isinstance(workflow, SequentialWorkflow):
            steps = " → ".join(step.agent for step in workflow.steps)
            console.print(Panel(
                f"[bold]Type:[/bold] Sequential\n"
                f"[bold]Flow:[/bold] {steps}",
                title="📋 Workflow",
                border_style="yellow"
            ))
        elif isinstance(workflow, ParallelWorkflow):
            branches = " | ".join(workflow.branches)
            aggregator = workflow.then.agent if workflow.then else "None"
            console.print(Panel(
                f"[bold]Type:[/bold] Parallel\n"
                f"[bold]Branches:[/bold] {branches}\n"
                f"[bold]Aggregator:[/bold] {aggregator}",
                title="📋 Workflow",
                border_style="yellow"
            ))


def run_workflow(
    config_path: Union[str, Path],
    use_mock: bool = False,
) -> dict[str, str]:
    """
    Convenience function to run a workflow.
    
    Args:
        config_path: Path to YAML configuration
        use_mock: If True, use mock LLM
        
    Returns:
        Dictionary of agent outputs
    """
    orchestrator = Orchestrator(use_mock=use_mock)
    return orchestrator.run(config_path)
