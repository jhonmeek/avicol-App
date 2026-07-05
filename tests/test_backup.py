import backup
from database import Database


def test_create_backup_produit_un_fichier(tmp_path):
    db_path = tmp_path / "src.db"
    db = Database(db_name=db_path)
    db.ajouter_bande("Lot A", "2026-01-01", 100, 500)
    db.close()

    dest = backup.create_backup(db_path, tmp_path / "backups")
    assert dest.exists()

    restored = Database(db_name=dest)
    noms = [row[1] for row in restored.get_bandes()]
    restored.close()
    assert noms == ["Lot A"]


def test_restore_round_trip_ac4(tmp_path):
    db_path = tmp_path / "src.db"
    backups = tmp_path / "backups"

    db = Database(db_name=db_path)
    db.ajouter_bande("Lot A", "2026-01-01", 100, 500)
    db.close()

    snapshot = backup.create_backup(db_path, backups)

    # Mutation après la sauvegarde
    db = Database(db_name=db_path)
    db.ajouter_bande("Lot B", "2026-02-01", 200, 500)
    db.close()

    safety = backup.restore_backup(snapshot, db_path, backups)
    assert safety is not None and safety.exists()

    db = Database(db_name=db_path)
    noms = [row[1] for row in db.get_bandes()]
    db.close()
    assert noms == ["Lot A"]  # état d'origine restauré
