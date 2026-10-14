import argparse
import sys
from pathlib import Path

from rich.markup import escape
from rich.prompt import Confirm

from . import __version__, ui
from .core import execute, plan_moves, restore
from .demo import create_demo_folder
from .history import drop_last_run, load_runs, save_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="organizer",
        description="Sort the files of a messy folder into tidy subfolders.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    sort = commands.add_parser("sort", help="organize a folder")
    sort.add_argument("folder", help="folder to organize")
    sort.add_argument("--by", choices=["type", "date"], default="type", help="group files by type or by modified date")
    sort.add_argument("--dry-run", action="store_true", help="preview the changes without moving anything")
    sort.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")

    undo = commands.add_parser("undo", help="revert the last run on a folder")
    undo.add_argument("folder", help="folder to restore")
    undo.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")

    demo = commands.add_parser("demo", help="create a messy sample folder to try the tool on")
    demo.add_argument("folder", nargs="?", default="demo_folder", help="where to create it")

    return parser


def resolve_folder(raw: str) -> Path:
    folder = Path(raw).expanduser().resolve()
    if not folder.is_dir():
        ui.error(f"'{folder}' is not a folder.")
        sys.exit(1)
    return folder


def run_sort(args: argparse.Namespace) -> int:
    folder = resolve_folder(args.folder)
    ui.show_banner()
    ui.console.print(f"Scanning [bold]{escape(str(folder))}[/bold]\n")

    moves = plan_moves(folder, args.by)
    if not moves:
        ui.info("Nothing to organize. The folder has no loose files.")
        return 0

    ui.show_plan(folder, moves)
    ui.show_summary(folder, moves, "Preview")

    if args.dry_run:
        ui.info("Dry run: no files were moved.")
        return 0

    if not args.yes and not Confirm.ask(f"Move {len(moves)} files?", default=True):
        ui.info("Cancelled.")
        return 0

    with ui.make_progress() as progress:
        task = progress.add_task("Organizing", total=len(moves))
        done, failed = execute(moves, lambda: progress.advance(task))

    if done:
        save_run(folder, done)
        ui.success(f"Moved {len(done)} files. Run 'undo' to revert.")
    ui.show_failures(failed)
    return 1 if failed else 0


def run_undo(args: argparse.Namespace) -> int:
    folder = resolve_folder(args.folder)
    ui.show_banner()

    runs = load_runs(folder)
    if not runs:
        ui.info("No history found for this folder.")
        return 0

    last = runs[-1]
    ui.info(f"Last run: {last['timestamp']} ({len(last['moves'])} files)")

    if not args.yes and not Confirm.ask("Revert it?", default=True):
        ui.info("Cancelled.")
        return 0

    with ui.make_progress() as progress:
        task = progress.add_task("Restoring", total=len(last["moves"]))
        restored, failed = restore(folder, last, lambda: progress.advance(task))

    drop_last_run(folder)
    ui.success(f"Restored {len(restored)} files.")
    ui.show_failures(failed)
    return 1 if failed else 0


def run_demo(args: argparse.Namespace) -> int:
    folder = Path(args.folder).expanduser().resolve()
    ui.show_banner()
    count = create_demo_folder(folder)
    ui.success(f"Created {count} messy files in {folder}")
    name = escape(args.folder)
    ui.console.print("\nTry it:")
    ui.console.print(f"  [cyan]python -m organizer sort {name} --dry-run[/cyan]")
    ui.console.print(f"  [cyan]python -m organizer sort {name}[/cyan]")
    ui.console.print(f"  [cyan]python -m organizer undo {name}[/cyan]")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {"sort": run_sort, "undo": run_undo, "demo": run_demo}
    try:
        return handlers[args.command](args)
    except KeyboardInterrupt:
        ui.info("Interrupted.")
        return 130
