"""Sauvegarde et restauration de la base SQLite sur chemins explicites.

Fonctions pures (aucune dépendance IU) : utilisables par l'application et
testables sans Qt. Utilise l'API de sauvegarde en ligne de sqlite3, cohérente
même lorsque la base est en mode WAL.
"""

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def create_backup(source_db_path, backups_dir, label="manuel"):
    """Copie cohérente de la base source vers backups_dir. Retourne le chemin."""
    source = Path(source_db_path)
    backups = Path(backups_dir)
    backups.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backups / f"avicole_backup_{label}_{stamp}.sqlite"

    source_conn = sqlite3.connect(str(source))
    try:
        dest_conn = sqlite3.connect(str(dest))
        try:
            source_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        source_conn.close()
    return dest


def restore_backup(backup_path, target_db_path, backups_dir):
    """Restaure backup_path sur target_db_path.

    Crée d'abord une sauvegarde de sécurité de la base actuelle (retournée),
    remplace le fichier cible puis nettoie les fichiers annexes WAL.
    Le connecteur applicatif doit être fermé avant l'appel et rouvert après.
    """
    backup_file = Path(backup_path)
    target = Path(target_db_path)

    safety = None
    if target.exists():
        safety = create_backup(target, backups_dir, label="securite_avant_restauration")

    shutil.copy2(backup_file, target)

    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(target) + suffix)
        if sidecar.exists():
            sidecar.unlink()

    return safety
