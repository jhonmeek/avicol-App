from database import Database


def test_fresh_db_at_latest_version(tmp_path):
    db = Database(db_name=tmp_path / "m.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert {"bandes", "mortalites", "depenses", "ventes"} <= tables


def test_migrations_are_idempotent(tmp_path):
    path = tmp_path / "m.db"
    Database(db_name=path).close()          # 1re ouverture : applique les migrations
    db = Database(db_name=path)             # 2e ouverture : ne doit rien réappliquer
    rows = db.conn.execute(
        "SELECT COUNT(*) FROM schema_version WHERE version = 1"
    ).fetchone()[0]
    db.close()
    assert rows == 1
