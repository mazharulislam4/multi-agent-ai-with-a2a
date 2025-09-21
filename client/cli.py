#!/usr/bin/env python3
"""
Multi-Agent NORA CLI Client

A command-line interface for interacting with the Multi-Agent NORA system.
Supports communication with Cisco Intersight, Service Catalog, and Supervisor agents.
"""

import sys
import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import (
    CISCO_INTERSIGHT_AGENT_URL, 
    SERVICE_CATALOG_AGENT_URL
)

console = Console()
logging.basicConfig(level=logging.WARNING)  # Reduce log noise


class MultiAgentClient:
    """Client for interacting with Multi-Agent NORA system"""
    
    AGENT_URLS = {
        'cisco': CISCO_INTERSIGHT_AGENT_URL,
        'service-catalog': SERVICE_CATALOG_AGENT_URL,
        'supervisor': 'http://localhost:8000'
    }
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        
    async def send_message(self, agent: str, message: str) -> Dict[str, Any]:
        """Send a message to an agent and return the response"""
        
        if agent not in self.AGENT_URLS:
            raise ValueError(f"Unknown agent: {agent}. Available: {list(self.AGENT_URLS.keys())}")
            
        url = self.AGENT_URLS[agent]
        
        # Different endpoints for different agents
        if agent == 'supervisor':
            endpoint = f"{url}/agent/chat"
            payload = {"message": message}
        else:
            endpoint = f"{url}/v1/messages"
            payload = {
                "id": f"{agent}_cli_call",
                "params": {
                    "message": {
                        "message_id": "cli_message_1",
                        "role": "user",
                        "parts": [{"text": message}]
                    }
                }
            }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException:
                raise click.ClickException(f"Timeout connecting to {agent} agent at {url}")
            except httpx.HTTPStatusError as e:
                raise click.ClickException(f"HTTP {e.response.status_code} error from {agent} agent: {e.response.text}")
            except Exception as e:
                raise click.ClickException(f"Error communicating with {agent} agent: {str(e)}")
    
    def extract_response_text(self, agent: str, response_data: Dict[str, Any]) -> str:
        """Extract the actual response text from the agent response"""
        
        if agent == 'supervisor':
            return response_data.get('response', 'No response received')
        else:
            # For a2a agents
            if 'message' in response_data and 'parts' in response_data['message']:
                parts = response_data['message']['parts']
                if parts and len(parts) > 0:
                    return parts[0].get('text', 'No text in response')
            return 'Invalid response format from agent'


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Multi-Agent NORA CLI - Interact with AI agents for Cisco and Service Catalog operations"""
    
    ctx.ensure_object(dict)
    
    if verbose:
        logging.basicConfig(level=logging.INFO)
        
    ctx.obj['client'] = MultiAgentClient()
    
    # Welcome message
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold blue]Multi-Agent NORA CLI[/bold blue]\n"
            "Interact with Cisco Intersight and Service Catalog agents\n\n"
            "Use --help to see available commands",
            title="🤖 Welcome"
        ))


@cli.command()
@click.argument('message')
@click.option('--agent', '-a', 
              type=click.Choice(['cisco', 'service-catalog', 'supervisor']), 
              default='supervisor',
              help='Which agent to send the message to')
@click.pass_context
def chat(ctx, message: str, agent: str):
    """Send a message to an agent and get a response"""
    
    client = ctx.obj['client']
    
    with console.status(f"[bold green]Sending message to {agent} agent..."):
        try:
            response = asyncio.run(client.send_message(agent, message))
            response_text = client.extract_response_text(agent, response)
            
            console.print()
            console.print(Panel(
                f"[bold cyan]You:[/bold cyan] {message}\n\n"
                f"[bold green]{agent.title()} Agent:[/bold green] {response_text}",
                title=f"🤖 {agent.title()} Agent Response"
            ))
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start an interactive chat session"""
    
    client = ctx.obj['client']
    
    console.print(Panel.fit(
        "[bold blue]Interactive Chat Mode[/bold blue]\n"
        "Type 'exit' to quit, 'switch' to change agents, 'help' for commands",
        title="🔄 Interactive Mode"
    ))
    
    current_agent = 'supervisor'
    
    while True:
        try:
            message = Prompt.ask(f"\n[bold cyan]You ({current_agent})[/bold cyan]")
            
            if message.lower() in ['exit', 'quit', 'bye']:
                console.print("[bold yellow]Goodbye! 👋[/bold yellow]")
                break
                
            elif message.lower() == 'switch':
                console.print("\nAvailable agents:")
                for i, agent in enumerate(['cisco', 'service-catalog', 'supervisor'], 1):
                    marker = "👈 current" if agent == current_agent else ""
                    console.print(f"  {i}. {agent} {marker}")
                
                choice = Prompt.ask("Select agent (1-3)")
                try:
                    agents = ['cisco', 'service-catalog', 'supervisor']
                    current_agent = agents[int(choice) - 1]
                    console.print(f"[bold green]Switched to {current_agent} agent[/bold green]")
                except (ValueError, IndexError):
                    console.print("[bold red]Invalid choice[/bold red]")
                continue
                
            elif message.lower() == 'help':
                console.print("""
[bold]Available commands:[/bold]
• [cyan]exit/quit/bye[/cyan] - Exit the chat
• [cyan]switch[/cyan] - Change the current agent
• [cyan]help[/cyan] - Show this help message
• [cyan]status[/cyan] - Show agent status
• Any other text - Send as a message to the current agent
""")
                continue
                
            elif message.lower() == 'status':
                asyncio.run(show_agent_status(client))
                continue
            
            with console.status(f"[bold green]Sending to {current_agent}..."):
                response = asyncio.run(client.send_message(current_agent, message))
                response_text = client.extract_response_text(current_agent, response)
                
                console.print(f"\n[bold green]{current_agent.title()}:[/bold green] {response_text}")
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Goodbye! 👋[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


async def show_agent_status(client: MultiAgentClient):
    """Show the status of all agents"""
    
    table = Table(title="🤖 Agent Status")
    table.add_column("Agent", style="cyan")
    table.add_column("URL", style="blue")
    table.add_column("Status", style="green")
    
    for agent, url in client.AGENT_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as http_client:
                response = await http_client.get(f"{url}/health" if agent != 'supervisor' else f"{url}/docs")
                status = "🟢 Online" if response.status_code == 200 else f"🟡 HTTP {response.status_code}"
        except:
            status = "🔴 Offline"
            
        table.add_row(agent, url, status)
    
    console.print(table)


@cli.command()
@click.pass_context  
def status(ctx):
    """Check the status of all agents"""
    client = ctx.obj['client']
    asyncio.run(show_agent_status(client))


@cli.command()
@click.option('--agent', '-a', 
              type=click.Choice(['cisco', 'service-catalog', 'supervisor']), 
              help='Show info for specific agent')
def info(agent):
    """Show information about the agents"""
    
    if agent:
        agents_info = {agent: MultiAgentClient.AGENT_URLS[agent]}
    else:
        agents_info = MultiAgentClient.AGENT_URLS
    
    for name, url in agents_info.items():
        panel_content = f"""
[bold]Agent:[/bold] {name.title()}
[bold]URL:[/bold] {url}
[bold]Purpose:[/bold] {get_agent_description(name)}
[bold]Capabilities:[/bold] {get_agent_capabilities(name)}
        """
        
        console.print(Panel(
            panel_content.strip(),
            title=f"🤖 {name.title()} Agent",
            border_style="blue"
        ))


def get_agent_description(agent: str) -> str:
    """Get description for an agent"""
    descriptions = {
        'cisco': 'Handles Cisco Intersight operations and greetings',
        'service-catalog': 'Manages service catalog operations and inquiries', 
        'supervisor': 'Routes requests to appropriate specialized agents'
    }
    return descriptions.get(agent, 'Unknown agent')


def get_agent_capabilities(agent: str) -> str:
    """Get capabilities for an agent"""
    capabilities = {
        'cisco': 'Device management, policy configuration, system information',
        'service-catalog': 'Service discovery, catalog browsing, service information',
        'supervisor': 'Intelligent routing, multi-agent coordination'
    }
    return capabilities.get(agent, 'Unknown capabilities')


@cli.command()
@click.argument('message')
@click.option('--all-agents', '-a', is_flag=True, help='Send to all agents')
@click.pass_context
def broadcast(ctx, message: str, all_agents: bool):
    """Send a message to multiple agents"""
    
    client = ctx.obj['client']
    
    if all_agents:
        agents = list(client.AGENT_URLS.keys())
    else:
        agents = ['cisco', 'service-catalog']  # Default to specialized agents
    
    console.print(f"[bold blue]Broadcasting to {len(agents)} agents...[/bold blue]\n")
    
    async def send_to_agents():
        tasks = []
        for agent in agents:
            task = asyncio.create_task(client.send_message(agent, message))
            tasks.append((agent, task))
        
        for agent, task in tasks:
            try:
                response = await task
                response_text = client.extract_response_text(agent, response)
                
                console.print(Panel(
                    f"[bold green]{agent.title()}:[/bold green] {response_text}",
                    title=f"🤖 {agent.title()} Response"
                ))
                
            except Exception as e:
                console.print(Panel(
                    f"[bold red]Error:[/bold red] {str(e)}",
                    title=f"❌ {agent.title()} Error",
                    border_style="red"
                ))
    
    asyncio.run(send_to_agents())


if __name__ == '__main__':
    cli()