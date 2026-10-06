"""src/utils/ui.py

Rich terminal UX components for Bug Solver Agent.
Provides live progress indicators, node execution cards, syntax-highlighted diffs,
and final summary scorecards.
"""

from __future__ import annotations

import os
from typing import Any

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

NODE_METADATA: dict[str, dict[str, str]] = {
    "Planner": {
        "icon": "🧠",
        "color": "cyan",
        "description": "Analyzing codebase, diagnosing bug, and formulating fix strategy",
    },
    "Coder": {
        "icon": "💻",
        "color": "yellow",
        "description": "Synthesizing code edits and applying patch to workspace",
    },
    "Test Runner": {
        "icon": "🧪",
        "color": "magenta",
        "description": "Executing test suite inside isolated subprocess sandbox",
    },
    "Evaluator": {
        "icon": "⚖️",
        "color": "green",
        "description": "Verifying test outcomes and validating patch correctness",
    },
    "PR Writer": {
        "icon": "🚀",
        "color": "blue",
        "description": "Committing verified changes, pushing branch, and opening PR",
    },
}


def print_banner(
    repo_path: str | os.PathLike,
    provider: str | None = None,
    model: str | None = None,
    mode: str = "Local",
) -> None:
    """Renders the Bug Solver ASCII / Rich startup banner."""
    title_text = Text()
    title_text.append("⚡ BUG SOLVER AGENT ", style="bold cyan")
    title_text.append("— Autonomous SWE-bench Repair Loop\n", style="bold white")

    info_text = Text()
    info_text.append("Repository: ", style="dim")
    info_text.append(f"{repo_path}\n", style="bold white")
    info_text.append("Provider: ", style="dim")
    info_text.append(f"{provider or 'ollama'}  ", style="bold green")
    info_text.append("Model: ", style="dim")
    info_text.append(f"{model or 'default'}  ", style="bold green")
    info_text.append("Mode: ", style="dim")
    info_text.append(f"{mode}", style="bold yellow")

    panel = Panel(
        info_text,
        title=title_text,
        title_align="left",
        border_style="cyan",
        box=ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)


def print_node_start(node_name: str, step_num: int, total_steps: int = 5) -> None:
    """Prints a styled header when a graph node starts execution."""
    meta = NODE_METADATA.get(
        node_name, {"icon": "⚙️", "color": "white", "description": "Processing"}
    )
    color = meta["color"]
    icon = meta["icon"]

    header = Text()
    header.append(f"[{step_num}/{total_steps}] ", style=f"bold {color}")
    header.append(f"{icon} {node_name} ", style=f"bold {color}")
    header.append("─── ", style=f"dim {color}")
    header.append(meta["description"], style="dim white")

    console.print(header)


def print_diff(diff_text: str, title: str = "Generated Git Diff") -> None:
    """Renders unified diff with rich syntax highlighting."""
    if not diff_text or not diff_text.strip():
        return
    syntax = Syntax(diff_text.strip(), "diff", theme="monokai", line_numbers=False)
    console.print(
        Panel(syntax, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow", box=ROUNDED)
    )


def print_node_result(
    node_name: str,
    state_update: dict[str, Any],
    diff_snippet: str | None = None,
) -> None:
    """Renders formatted results for a completed graph node."""
    if node_name == "Planner":
        files = state_update.get("relevant_files", [])
        plan = state_update.get("fix_plan", "")
        if files:
            files_str = ", ".join(f"[bold cyan]{f}[/bold cyan]" for f in files)
            console.print(f"  [dim]Target files identified:[/dim] {files_str}")
        if plan:
            plan_preview = plan.strip().split("\n")[0][:120]
            console.print(f"  [dim]Strategy:[/dim] {plan_preview}...")

    elif node_name == "Coder":
        patch = state_update.get("patch_code", "")
        if patch:
            console.print(f"  [dim]Patch applied:[/dim] {patch}")
        if diff_snippet:
            print_diff(diff_snippet)

    elif node_name == "Test Runner":
        output = state_update.get("test_output", "")
        summary_lines = [
            ln for ln in output.splitlines() if "passed" in ln or "failed" in ln or "error" in ln.lower()
        ]
        if summary_lines:
            console.print(f"  [dim]Test Summary:[/dim] [bold]{summary_lines[-1].strip()}[/bold]")
        else:
            console.print("  [dim]Test Runner completed execution sandbox.[/dim]")

    elif node_name == "Evaluator":
        status = state_update.get("status", "UNKNOWN")
        retry_count = state_update.get("retry_count", 0)
        if status == "SUCCESS":
            console.print(
                "  [bold green]✔ Patch Verification PASSED![/bold green] All tests satisfied."
            )
        else:
            console.print(
                f"  [bold red]✖ Patch Verification FAILED.[/bold red] Retry count: {retry_count}"
            )

    elif node_name == "PR Writer":
        status = state_update.get("status", "")
        console.print(f"  [bold blue]✔ Finalization complete:[/bold blue] {status}")

    console.print()


def print_summary_card(
    repo_path: str,
    task_desc: str,
    final_status: str,
    nodes_executed: list[str],
    retries: int,
    branch_name: str | None = None,
    pr_url: str | None = None,
) -> None:
    """Renders a final completion scorecard table."""
    table = Table(
        title="🏁 Execution Summary & Outcome",
        box=ROUNDED,
        header_style="bold cyan",
        border_style="cyan",
    )
    table.add_column("Property", style="bold white", width=22)
    table.add_column("Value", style="dim white")

    table.add_row("Target Repository", str(repo_path))
    table.add_row("Task / Issue", str(task_desc)[:80])

    status_styled = (
        "[bold green]✔ SUCCESS (Resolved)[/bold green]"
        if final_status == "SUCCESS"
        else f"[bold red]✖ {final_status}[/bold red]"
    )
    table.add_row("Final Status", status_styled)
    table.add_row("Workflow Path", " ➔ ".join(nodes_executed))
    table.add_row("Retries Incurred", str(retries))

    if branch_name:
        table.add_row("Working Branch", f"[bold yellow]{branch_name}[/bold yellow]")
    if pr_url:
        table.add_row("Pull Request", f"[bold blue]{pr_url}[/bold blue]")

    console.print(table)
