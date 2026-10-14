import os
import random
import time
from pathlib import Path

SAMPLE_NAMES = [
    "holiday_photo.jpg",
    "screenshot_2024-03-12.png",
    "logo_final_v2.png",
    "profile.webp",
    "invoice_march.pdf",
    "resume.docx",
    "meeting_notes.txt",
    "thesis_draft.docx",
    "book.epub",
    "budget_2024.xlsx",
    "expenses.csv",
    "sales_report.xlsx",
    "family_trip.mp4",
    "tutorial_part1.mkv",
    "clip.mov",
    "podcast_ep12.mp3",
    "voice_note.m4a",
    "song.flac",
    "project_backup.zip",
    "dataset.tar.gz",
    "old_files.rar",
    "script.py",
    "index.html",
    "styles.css",
    "config.json",
    "query.sql",
    "setup_v2.exe",
    "app.dmg",
    "mystery_file.xyz",
    "README_copy",
]


def create_demo_folder(folder: Path) -> int:
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(7)
    now = time.time()
    for name in SAMPLE_NAMES:
        path = folder / name
        path.write_bytes(b"demo")
        stamp = now - rng.randint(0, 900) * 86400
        os.utime(path, (stamp, stamp))
    return len(SAMPLE_NAMES)
