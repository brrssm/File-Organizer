from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff", ".ico"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".ppt", ".pptx", ".epub"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".go", ".rs", ".sh", ".sql"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
}

OTHER = "Other"

EXTENSION_TO_CATEGORY = {
    extension: category
    for category, extensions in CATEGORIES.items()
    for extension in extensions
}


def category_for(path: Path) -> str:
    return EXTENSION_TO_CATEGORY.get(path.suffix.lower(), OTHER)
