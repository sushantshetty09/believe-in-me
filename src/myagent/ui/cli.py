import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from prompt_toolkit import PromptSession

from ..config import Config
from ..model import OllamaClient
from ..agent import Agent
from ..permissions import PermissionManager
from ..git_utils import undo_checkpoint

console = Console()

def main():
    parser = argparse.ArgumentParser(description="MyAgent - Local Autonomous Coding Agent")
    parser.add_argument("--model", type=str, default="qwen3-coder:30b", help="Model tag (e.g., qwen3-coder:30b)")
    parser.add_argument("--host", type=str, default="http://localhost:11434", help="Ollama host URL")
    parser.add_argument("--auto-approve", action="store_true", help="Auto approve all permissions")
    parser.add_argument("--workdir", type=str, default=".", help="Project root directory")
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    config = Config(model=args.model, host=args.host, workdir=workdir)
    model_client = OllamaClient(model=config.model, host=config.host)
    permission_manager = PermissionManager(auto_approve_all=args.auto_approve)

    def confirm_cb(prompt_text: str) -> bool:
        console.print(f"[yellow]{prompt_text}[/yellow]")
        return Confirm.ask("Approve execution?")

    agent = Agent(
        config=config,
        model_client=model_client,
        permission_manager=permission_manager,
        confirm_callback=confirm_cb,
    )

    console.print(Panel(f"[bold green]MyAgent[/bold green] | Model: [cyan]{config.model}[/cyan] | Workdir: [cyan]{workdir}[/cyan]\nType '/undo' to rollback changes, or Ctrl+C to exit.", title="Welcome"))

    session = PromptSession()
    messages = None

    while True:
        try:
            req = session.prompt("You> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not req:
            continue

        if req.lower() == "/undo":
            success, msg = undo_checkpoint(workdir)
            if success:
                console.print(f"[green]{msg}[/green]")
            else:
                console.print(f"[red]{msg}[/red]")
            continue

        def on_thought():
            console.print("[dim cyan]Thinking...[/dim cyan]")

        def on_tool_call(name: str, arguments: dict):
            console.print(f"[cyan]> Tool Call:[/cyan] [bold]{name}[/bold] {arguments}")

        def on_tool_result(name: str, result: str):
            preview = result[:200] + "..." if len(result) > 200 else result
            console.print(f"[dim]> Tool Result ({name}): {preview}[/dim]")

        def on_message(msg: str):
            console.print(Panel(msg, title="Agent Response", border_style="green"))

        try:
            messages = agent.run(
                user_request=req,
                messages=messages,
                on_thought=on_thought,
                on_tool_call=on_tool_call,
                on_tool_result=on_tool_result,
                on_message=on_message,
            )
        except KeyboardInterrupt:
            console.print("\n[red]Task interrupted by user.[/red]")

if __name__ == "__main__":
    main()
