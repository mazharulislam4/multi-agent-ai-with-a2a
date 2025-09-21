#!/usr/bin/env python3
"""
Multi-Agent NORA Main Entry Point

This script provides a unified entry point for starting all components
of the Multi-Agent NORA system.
"""

import asyncio
import logging
import subprocess
import sys
import os
import signal
from typing import List, Optional
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


class MultiAgentSystem:
    """Manager for the Multi-Agent NORA system"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.python_exe = self._get_python_executable()
    
    def _get_python_executable(self) -> str:
        """Get the correct Python executable path"""
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return str(venv_python)
        return sys.executable
    
    async def start_agent(self, agent_name: str, module_path: str, port: int) -> Optional[subprocess.Popen]:
        """Start an individual agent"""
        try:
            console.print(f"[blue]Starting {agent_name} agent on port {port}...[/blue]")
            
            process = subprocess.Popen(
                [self.python_exe, "-m", module_path],
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            
            # Give the process a moment to start
            await asyncio.sleep(2)
            
            if process.poll() is None:
                console.print(f"[green]✓ {agent_name} agent started successfully[/green]")
                return process
            else:
                stdout, stderr = process.communicate()
                console.print(f"[red]✗ {agent_name} agent failed to start[/red]")
                console.print(f"[red]Error: {stderr}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]✗ Failed to start {agent_name}: {str(e)}[/red]")
            return None
    
    async def start_all_agents(self):
        """Start all agents in the system"""
        agents = [
            ("Cisco Intersight", "agents.cisco_intersight.server", 8002),
            ("Service Catalog", "agents.service_catalog.server", 8001),
            ("Supervisor", "agents.supervisor.main", 8000),
        ]
        
        console.print(Panel.fit(
            "[bold blue]Multi-Agent NORA System[/bold blue]\n"
            "Starting all agent components...",
            title="🚀 System Startup"
        ))
        
        for agent_name, module_path, port in agents:
            await self.start_agent(agent_name, module_path, port)
            await asyncio.sleep(1)  # Stagger startup
        
        if self.processes:
            console.print("\n[bold green]All agents started![/bold green]")
            self._show_status()
            console.print("\n[yellow]Press Ctrl+C to stop all agents[/yellow]")
            
            # Wait for interruption
            try:
                while True:
                    await asyncio.sleep(1)
                    # Check if any process has died
                    for i, process in enumerate(self.processes):
                        if process.poll() is not None:
                            console.print(f"[red]Agent process {i} has stopped unexpectedly[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down all agents...[/yellow]")
                self.stop_all_agents()
        else:
            console.print("[red]No agents were started successfully[/red]")
    
    def _show_status(self):
        """Show the status of all running agents"""
        table = Table(title="🤖 Agent Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Port", style="blue")
        table.add_column("URL", style="green")
        table.add_column("Status", style="bold")
        
        agents_info = [
            ("Cisco Intersight", "8002", "http://localhost:8002"),
            ("Service Catalog", "8001", "http://localhost:8001"),
            ("Supervisor", "8000", "http://localhost:8000"),
        ]
        
        for i, (name, port, url) in enumerate(agents_info):
            if i < len(self.processes) and self.processes[i].poll() is None:
                status = "🟢 Running"
            else:
                status = "🔴 Stopped"
            table.add_row(name, port, url, status)
        
        console.print(table)
    
    def stop_all_agents(self):
        """Stop all running agents"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
        
        self.processes.clear()
        console.print("[green]All agents stopped.[/green]")


@click.group()
def main():
    """Multi-Agent NORA System - AI Agent Management Platform"""
    pass


@main.command()
def start():
    """Start all agents in the Multi-Agent NORA system"""
    system = MultiAgentSystem()
    
    try:
        asyncio.run(system.start_all_agents())
    except KeyboardInterrupt:
        console.print("\n[yellow]Startup interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting system: {str(e)}[/red]")


@main.command()
@click.option('--agent', type=click.Choice(['cisco', 'service-catalog', 'supervisor']),
              help='Start only a specific agent')
def start_agent(agent):
    """Start a specific agent"""
    system = MultiAgentSystem()
    
    agent_configs = {
        'cisco': ("Cisco Intersight", "agents.cisco_intersight.server", 8002),
        'service-catalog': ("Service Catalog", "agents.service_catalog.server", 8001),
        'supervisor': ("Supervisor", "agents.supervisor.main", 8000),
    }
    
    if agent not in agent_configs:
        console.print(f"[red]Unknown agent: {agent}[/red]")
        return
    
    async def start_single():
        name, module, port = agent_configs[agent]
        process = await system.start_agent(name, module, port)
        
        if process:
            console.print(f"\n[green]{name} agent is running on port {port}[/green]")
            console.print("[yellow]Press Ctrl+C to stop[/yellow]")
            
            try:
                while process.poll() is None:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                console.print(f"\n[yellow]Stopping {name} agent...[/yellow]")
                system.stop_all_agents()
    
    try:
        asyncio.run(start_single())
    except KeyboardInterrupt:
        console.print("\n[yellow]Agent stopped[/yellow]")


@main.command()
def status():
    """Check the status of all agents"""
    import httpx
    
    async def check_status():
        agents = [
            ("Cisco Intersight", "http://localhost:8002"),
            ("Service Catalog", "http://localhost:8001"),
            ("Supervisor", "http://localhost:8000"),
        ]
        
        table = Table(title="🤖 Agent Status Check")
        table.add_column("Agent", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Status", style="bold")
        
        for name, url in agents:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    if name == "Supervisor":
                        response = await client.get(f"{url}/docs")
                    else:
                        response = await client.get(f"{url}/health")
                    
                    if response.status_code == 200:
                        status = "🟢 Online"
                    else:
                        status = f"🟡 HTTP {response.status_code}"
            except httpx.ConnectError:
                status = "🔴 Offline"
            except Exception as e:
                status = f"🟠 Error: {str(e)[:20]}..."
            
            table.add_row(name, url, status)
        
        console.print(table)
    
    asyncio.run(check_status())


@main.command()
def info():
    """Show information about the Multi-Agent NORA system"""
    
    info_text = """
[bold blue]Multi-Agent NORA System[/bold blue]

This system consists of three main components:

🤖 [bold cyan]Cisco Intersight Agent[/bold cyan] (Port 8002)
   • Handles Cisco Intersight operations and greetings
   • Provides device management and policy configuration
   • Endpoint: http://localhost:8002

🤖 [bold cyan]Service Catalog Agent[/bold cyan] (Port 8001) 
   • Manages service catalog operations and inquiries
   • Provides service discovery and catalog browsing
   • Endpoint: http://localhost:8001

🤖 [bold cyan]Supervisor Agent[/bold cyan] (Port 8000)
   • Routes requests to appropriate specialized agents
   • Provides intelligent coordination between agents
   • Endpoint: http://localhost:8000

[bold green]CLI Usage:[/bold green]
   • nora - Interactive CLI client
   • nora chat "message" - Send a message
   • nora interactive - Start interactive mode
   • nora status - Check agent status

[bold green]Environment Setup:[/bold green]
   • Ensure .env file has OPENAI_API_KEY set
   • Run 'uv sync' to install dependencies
   • All agents use GPT-3.5-turbo by default
    """
    
    console.print(Panel(info_text.strip(), title="ℹ️  System Information"))


@main.command()
def cli():
    """Launch the interactive CLI client"""
    try:
        # Import and run the CLI
        from client.cli import cli as nora_cli
        nora_cli()
    except ImportError as e:
        console.print(f"[red]Error importing CLI: {str(e)}[/red]")
        console.print("[yellow]Make sure dependencies are installed with 'uv sync'[/yellow]")
    except Exception as e:
        console.print(f"[red]Error running CLI: {str(e)}[/red]")


if __name__ == "__main__":
    main()
