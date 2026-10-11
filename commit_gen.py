import os
import sys
import subprocess
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import CommitMessageResponse

app = typer.Typer(help="Automated Semantic Git Commit Message Generator CLI")
console = Console()


def get_staged_diff() -> str:
    """Run git diff --staged to capture current staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error running git command: {e}[/bold red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(
            "[bold red]Error: 'git' command not found. Ensure Git is installed and you are in a repository.[/bold red]"
        )
        raise typer.Exit(1)


@app.command()
def commit(
    diff_file: str = typer.Option(
        None,
        "--file",
        "-f",
        help="Optional path to a diff file instead of reading live staged git changes",
    ),
):
    """Analyze staged git changes and generate a semantic conventional commit message."""

    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    # Get diff from file if provided, otherwise fetch live staged git diff
    if diff_file:
        path = Path(diff_file)
        if not path.exists():
            console.print(
                f"[bold red]Error: Diff file not found -> {diff_file}[/bold red]"
            )
            raise typer.Exit(1)
        diff_text = path.read_text(encoding="utf-8")
    else:
        diff_text = get_staged_diff()

    if not diff_text:
        console.print(
            "[bold yellow]⚠️ No staged changes detected! Run 'git add' on your files first.[/bold yellow]"
        )
        raise typer.Exit(1)

    client = genai.Client()

    prompt = f"""
You are an expert senior software engineer and release manager. 
Analyze the following git diff and generate a professional, semantic Conventional Commit message. Follow standard conventions (e.g., feat, fix, refactor, docs, chore, etc.).

=== STAGED GIT DIFF ===
{diff_text}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Analyzing staged diff & generating commit message...",
            total=None,
        )

        try:
            # Temporarily suppress stderr to keep terminal output clean
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CommitMessageResponse,
                        temperature=0.1,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            result = CommitMessageResponse.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]Commit generation failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Dashboard using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]📦 Git Commit Message Generator[/bold cyan]\n"
            f"Semantic Type: [bold green]{result.commit_type}[/bold green] | Scope: [bold blue]{result.scope or 'None'}[/bold blue]",
            title="Conventional Commit AI",
            border_style="cyan",
        )
    )

    # Metadata Table
    meta_table = Table(show_header=True, header_style="bold magenta")
    meta_table.add_column("Property", style="dim")
    meta_table.add_column("Value", justify="right")

    meta_table.add_row("Commit Type", result.commit_type)
    meta_table.add_row("Scope", result.scope or "N/A")
    meta_table.add_row(
        "Breaking Change",
        "[bold red]Yes[/bold red]" if result.breaking_change else "[green]No[/green]",
    )
    console.print(meta_table)

    # Render the Final Formatted Commit Message in a Panel
    commit_syntax = Syntax(
        result.full_commit_message, "markdown", theme="monokai", word_wrap=True
    )
    console.print(
        Panel(
            commit_syntax,
            title="[bold yellow]✨ Generated Commit Message[/bold yellow]",
            border_style="yellow",
        )
    )

    # Helpful shell command hint
    console.print(
        Panel(
            f'git commit -m "{result.subject}"',
            title="[bold green]💡 Quick Git Command[/bold green]",
            border_style="green",
        )
    )
    console.print("\n")


if __name__ == "__main__":
    app()
