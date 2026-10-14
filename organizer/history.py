import json
from datetime import datetime
from pathlib import Path

HISTORY_NAME = ".organizer_history.json"


def history_path(folder: Path) -> Path:
    return folder / HISTORY_NAME


def load_runs(folder: Path) -> list:
    path = history_path(folder)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_run(folder: Path, moves) -> None:
    runs = load_runs(folder)
    runs.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "moves": [
                {"source": str(move.source), "destination": str(move.destination)}
                for move in moves
            ],
        }
    )
    history_path(folder).write_text(json.dumps(runs, indent=2), encoding="utf-8")


def drop_last_run(folder: Path) -> None:
    runs = load_runs(folder)
    if runs:
        runs.pop()
    path = history_path(folder)
    if runs:
        path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    else:
        path.unlink(missing_ok=True)
