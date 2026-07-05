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
