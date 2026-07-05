import pytest

from database import Database


def test_migration_v5_tables_stock(tmp_path):
    db = Database(db_name=tmp_path / "v5.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert {"stocks", "mouvements_stock"} <= tables
