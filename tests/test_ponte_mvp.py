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
