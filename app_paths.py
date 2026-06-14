"""Chemins persistants utilisés en développement et après installation."""

import os
import shutil
from pathlib import Path


APP_NAME = "AvicolePro"


def data_dir():
    root = os.environ.get("LOCALAPPDATA")
    base = Path(root) if root else Path.home() / "AppData" / "Local"
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path():
    target = data_dir() / "gestion_poulets.db"
    if target.exists():
        return target

    project_dir = Path(__file__).resolve().parent
    candidates = (
        Path.cwd() / "gestion_poulets.db",
        project_dir / "gestion_poulets.db",
        project_dir.parent / "gestion_poulets.db",
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve() != target.resolve():
            shutil.copy2(candidate, target)
            break
    return target


def ensure_user_directories():
    directories = {}
    for name in ("rapports", "exports", "backups", "logs", "temp"):
        path = data_dir() / name
        path.mkdir(parents=True, exist_ok=True)
        directories[name] = path
    return directories
