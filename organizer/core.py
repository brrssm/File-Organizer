import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from .categories import category_for


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path


def collect_files(folder: Path) -> list:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )


def target_folder_name(path: Path, mode: str) -> str:
    if mode == "date":
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        return f"{modified.year}/{modified.month:02d}"
    return category_for(path)


def unique_path(path: Path, reserved: set) -> Path:
    candidate = path
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        counter += 1
    return candidate


def plan_moves(folder: Path, mode: str = "type") -> list:
    reserved = set()
    moves = []
    for file in collect_files(folder):
        wanted = folder / target_folder_name(file, mode) / file.name
        destination = unique_path(wanted, reserved)
        reserved.add(destination)
        moves.append(Move(file, destination))
    return moves


def execute(moves: list, on_step: Optional[Callable[[], None]] = None):
    done, failed = [], []
    for move in moves:
        try:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.source), str(move.destination))
            done.append(move)
        except OSError as error:
            failed.append((move.source, error.strerror or str(error)))
        if on_step:
            on_step()
    return done, failed


def remove_empty_parents(path: Path, stop: Path) -> None:
    parent = path.parent
    while parent != stop and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent


def restore(folder: Path, run: dict, on_step: Optional[Callable[[], None]] = None):
    restored, failed = [], []
    for item in reversed(run["moves"]):
        original = Path(item["source"])
        current = Path(item["destination"])
        if not current.exists():
            failed.append((current, "file no longer exists"))
        else:
            target = unique_path(original, set())
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current), str(target))
                restored.append(Move(current, target))
                remove_empty_parents(current, folder)
            except OSError as error:
                failed.append((current, error.strerror or str(error)))
        if on_step:
            on_step()
    return restored, failed
