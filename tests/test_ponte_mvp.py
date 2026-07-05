import pytest

from database import Database


def test_migration_v4_colonne_activite(tmp_path):
    db = Database(db_name=tmp_path / "v4.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION
    colonnes = {
        row[1] for row in db.conn.execute("PRAGMA table_info(bandes)").fetchall()
    }
    db.close()
    assert "activite" in colonnes


def test_migration_v4_tables_ponte(tmp_path):
    db = Database(db_name=tmp_path / "v4b.db")
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert {"pontes", "mouvements_oeufs"} <= tables


def test_ajouter_bande_activite_defaut_chair_et_explicite_ponte(tmp_path):
    db = Database(db_name=tmp_path / "activite.db")
    id_chair = db.ajouter_bande("Lot A", "2026-01-01", 1000, 500)
    id_ponte = db.ajouter_bande(
        "Lot Pondeuses", "2026-01-01", 200, 1500, activite="ponte"
    )
    info_chair = db.get_bande_info(id_chair)
    info_ponte = db.get_bande_info(id_ponte)
    db.close()
    assert info_chair[6] == "chair"
    assert info_ponte[6] == "ponte"


def test_mortalite_fonctionne_sur_lot_ponte(tmp_path):
    db = Database(db_name=tmp_path / "mortalite_ponte.db")
    bande_id = db.ajouter_bande(
        "Lot Pondeuses", "2026-01-01", 200, 1500, activite="ponte"
    )
    db.ajouter_mortalite(bande_id, "2026-01-10", 5)
    restants = db.get_poulets_restants(bande_id)
    db.close()
    assert restants == 195
