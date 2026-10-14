import os
from datetime import datetime
from pathlib import Path

from organizer.categories import category_for
from organizer.core import execute, plan_moves, restore
from organizer.history import HISTORY_NAME, drop_last_run, load_runs, save_run


def make_files(folder, names):
    for name in names:
        (folder / name).write_text("x")


def test_category_for_known_and_unknown_extensions():
    assert category_for(Path("photo.JPG")) == "Images"
    assert category_for(Path("notes.txt")) == "Documents"
    assert category_for(Path("file.unknown")) == "Other"
    assert category_for(Path("no_extension")) == "Other"


def test_plan_ignores_hidden_files_and_subfolders(tmp_path):
    make_files(tmp_path, ["a.png", ".hidden.txt"])
    (tmp_path / "subdir").mkdir()
    moves = plan_moves(tmp_path)
    assert [move.source.name for move in moves] == ["a.png"]


def test_execute_moves_files_into_category_folders(tmp_path):
    make_files(tmp_path, ["a.png", "b.pdf", "c.mp3"])
    done, failed = execute(plan_moves(tmp_path))
    assert not failed
    assert len(done) == 3
    assert (tmp_path / "Images" / "a.png").exists()
    assert (tmp_path / "Documents" / "b.pdf").exists()
    assert (tmp_path / "Audio" / "c.mp3").exists()


def test_name_conflict_gets_a_numbered_suffix(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.png").write_text("old")
    (tmp_path / "a.png").write_text("new")
    execute(plan_moves(tmp_path))
    assert (tmp_path / "Images" / "a.png").read_text() == "old"
    assert (tmp_path / "Images" / "a_1.png").read_text() == "new"


def test_sort_by_date_uses_modified_time(tmp_path):
    make_files(tmp_path, ["a.txt"])
    stamp = datetime(2021, 5, 17).timestamp()
    os.utime(tmp_path / "a.txt", (stamp, stamp))
    moves = plan_moves(tmp_path, "date")
    assert moves[0].destination == tmp_path / "2021" / "05" / "a.txt"


def test_undo_restores_files_and_removes_empty_folders(tmp_path):
    make_files(tmp_path, ["a.png", "b.pdf"])
    done, _ = execute(plan_moves(tmp_path))
    save_run(tmp_path, done)
    restored, failed = restore(tmp_path, load_runs(tmp_path)[-1])
    assert not failed
    assert len(restored) == 2
    assert (tmp_path / "a.png").exists()
    assert (tmp_path / "b.pdf").exists()
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / "Documents").exists()


def test_undo_reports_files_that_disappeared(tmp_path):
    make_files(tmp_path, ["a.png"])
    done, _ = execute(plan_moves(tmp_path))
    save_run(tmp_path, done)
    (tmp_path / "Images" / "a.png").unlink()
    restored, failed = restore(tmp_path, load_runs(tmp_path)[-1])
    assert restored == []
    assert len(failed) == 1


def test_history_can_be_saved_and_dropped(tmp_path):
    make_files(tmp_path, ["a.png"])
    done, _ = execute(plan_moves(tmp_path))
    save_run(tmp_path, done)
    assert len(load_runs(tmp_path)) == 1
    drop_last_run(tmp_path)
    assert load_runs(tmp_path) == []
    assert not (tmp_path / HISTORY_NAME).exists()
