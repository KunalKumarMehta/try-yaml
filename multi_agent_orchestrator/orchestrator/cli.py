"""Command-line interface for the orchestrator."""

import click
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from .config.parser import parse_config, ConfigError
from .config.schema import SequentialWorkflow, ParallelWorkflow
from .engine.orchestrator import Orchestrator


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """YAML-driven Multi-Agent Orchestration Engine.
    
    Define agent workflows in YAML and let the engine handle orchestration.
    """
    pass


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--mock", is_flag=True, help="Use mock LLM for testing (no API key required)")
def run(config_path: str, mock: bool):
    """Run a workflow from a YAML configuration file.
    
    CONFIG_PATH: Path to the YAML workflow configuration file.
    """
    console.print(Panel(
        "[bold cyan]🚀 Multi-Agent Orchestrator[/bold cyan]\n"
        "YAML-driven agent workflow execution",
        border_style="cyan"
    ))
    
    try:
        orchestrator = Orchestrator(use_mock=mock)
        results = orchestrator.run(config_path)
        
        console.print("\n[bold green]✅ Workflow completed successfully![/bold green]")
        console.print(f"[dim]Agents executed: {len(results)}[/dim]")
        
    except ConfigError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
def validate(config_path: str):
    """Validate a YAML configuration file.
    
    CONFIG_PATH: Path to the YAML workflow configuration file.
    """
    try:
        config = parse_config(config_path)
        console.print("[bold green]✓ Configuration is valid![/bold green]")
        
        # Show summary
        console.print(f"\n[dim]Agents: {len(config.agents)}[/dim]")
        workflow_type = "sequential" if isinstance(config.workflow, SequentialWorkflow) else "parallel"
        console.print(f"[dim]Workflow type: {workflow_type}[/dim]")
        
    except ConfigError as e:
        console.print(f"[bold red]✗ Validation failed:[/bold red]\n{e}")
        raise SystemExit(1)


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
def show(config_path: str):
    """Display the structure of a workflow configuration.
    
    CONFIG_PATH: Path to the YAML workflow configuration file.
    """
    try:
        config = parse_config(config_path)
    except ConfigError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)
    
    # Agents table
    table = Table(title="📋 Agents", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="bold yellow")
    table.add_column("Role", style="green")
    table.add_column("Goal")
    table.add_column("Tools", style="dim")
    
    for agent in config.agents:
        tools = ", ".join(agent.tools) if agent.tools else "-"
        table.add_row(agent.id, agent.role, agent.goal, tools)
    
    console.print(table)
    console.print()
    
    # Workflow visualization
    tree = Tree("[bold blue]🔄 Workflow[/bold blue]")
    
    if isinstance(config.workflow, SequentialWorkflow):
        tree.label = "[bold blue]🔄 Sequential Workflow[/bold blue]"
        for i, step in enumerate(config.workflow.steps, 1):
            tree.add(f"[yellow]{i}.[/yellow] {step.agent}")
    
    elif isinstance(config.workflow, ParallelWorkflow):
        tree.label = "[bold blue]⚡ Parallel Workflow[/bold blue]"
        branches = tree.add("[cyan]Parallel Branches[/cyan]")
        for branch in config.workflow.branches:
            branches.add(f"├── {branch}")
        
        if config.workflow.then:
            tree.add(f"[magenta]Then → {config.workflow.then.agent}[/magenta]")
    
    console.print(tree)


if __name__ == "__main__":
    main()
