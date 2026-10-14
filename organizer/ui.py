from collections import Counter
from pathlib import Path

from rich.console import Console, Group
from rich.markup import escape
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

PREVIEW_LIMIT = 12
BAR_WIDTH = 24


def show_banner() -> None:
    title = Text("FILE ORGANIZER", style="bold cyan", justify="center")
    subtitle = Text("Turn a messy folder into a tidy one", style="dim", justify="center")
    console.print(Panel(Group(title, subtitle), border_style="cyan", padding=(1, 6)))


def info(message: str) -> None:
    console.print(f"[bold blue]i[/bold blue] {escape(message)}")


def success(message: str) -> None:
    console.print(f"[bold green]✔[/bold green] {escape(message)}")


def error(message: str) -> None:
    console.print(f"[bold red]✘ Error:[/bold red] {escape(message)}")


def show_plan(folder: Path, moves: list) -> None:
    table = Table(title="Planned moves", header_style="bold magenta", border_style="dim")
    table.add_column("File", overflow="fold")
    table.add_column("Goes to", style="green")
    for move in moves[:PREVIEW_LIMIT]:
        table.add_row(Text(move.source.name), Text(str(move.destination.parent.relative_to(folder))))
    hidden = len(moves) - PREVIEW_LIMIT
    if hidden > 0:
        table.add_row(Text(f"... and {hidden} more", style="dim"), "")
    console.print(table)


def show_summary(folder: Path, moves: list, title: str = "Summary") -> None:
    counts = Counter(str(move.destination.parent.relative_to(folder)) for move in moves)
    total = sum(counts.values())
    table = Table(title=title, header_style="bold cyan", border_style="dim")
    table.add_column("Folder")
    table.add_column("Files", justify="right")
    table.add_column("Share")
    for name, count in counts.most_common():
        bar = "█" * max(1, round(count / total * BAR_WIDTH))
        table.add_row(Text(name), str(count), Text(bar, style="cyan"))
    console.print(table)


def show_failures(failed: list) -> None:
    if not failed:
        return
    table = Table(title="Could not process", header_style="bold red", border_style="red")
    table.add_column("File", overflow="fold")
    table.add_column("Reason")
    for path, reason in failed:
        table.add_row(Text(path.name), Text(reason))
    console.print(table)


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    )
