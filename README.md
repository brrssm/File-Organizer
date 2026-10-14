# File Organizer

A small command-line tool that turns a messy folder (hello, Downloads) into a tidy one. Preview first, confirm, and undo whenever you want.

![demo](docs/demo.gif)

## Features

- **Sort by type** (Images, Documents, Videos...) or **by date** (`2024/05`)
- **Dry run** to preview every move before anything happens
- **Undo** the last run, restoring files and removing empty folders
- **Safe by design:** never overwrites a file, duplicates become `name_1.ext`
- Skips hidden files and existing subfolders
- Clean terminal UI with tables and progress bars, powered by [Rich](https://github.com/Textualize/rich)

## Install

```bash
git clone https://github.com/brrssm/file-organizer.git
cd file-organizer
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Optional: `pip install -e .` gives you a short `organizer` command.

## Usage

Try it safely on a generated messy folder:

```bash
python -m organizer demo
python -m organizer sort demo_folder --dry-run
python -m organizer sort demo_folder
python -m organizer undo demo_folder
```

On your own folders:

```bash
python -m organizer sort ~/Downloads
python -m organizer sort ~/Downloads --by date
python -m organizer sort ~/Downloads --yes
```

| Command | What it does |
|---|---|
| `sort FOLDER` | Organize a folder (`--by type\|date`, `--dry-run`, `--yes`) |
| `undo FOLDER` | Revert the last run on that folder |
| `demo [FOLDER]` | Create a messy sample folder to play with |

## Categories

| Folder | Extensions |
|---|---|
| Images | jpg, png, gif, webp, svg, heic... |
| Videos | mp4, mkv, mov, avi... |
| Audio | mp3, wav, flac, m4a... |
| Documents | pdf, docx, txt, md, pptx, epub... |
| Spreadsheets | xlsx, csv, ods... |
| Archives | zip, rar, 7z, tar, gz... |
| Code | py, js, html, css, json, sql... |
| Installers | exe, msi, dmg, deb, apk |
| Other | everything else |

Edit `organizer/categories.py` to add your own.

## How undo works

Every run saves a log of its moves in a hidden `.organizer_history.json` inside the target folder. `undo` reads the last entry, moves each file back, and removes the category folders left empty.

## Project structure

```
organizer/
├── categories.py   extension to folder mapping
├── core.py         planning, moving and restoring files
├── history.py      run log used by undo
├── ui.py           terminal output (Rich)
├── cli.py          argument parsing and commands
└── demo.py         messy sample folder generator
tests/test_core.py
```

## Tests

```bash
pytest -v
```

## License

MIT
