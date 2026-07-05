from database import Database


def test_wal_mode_active(tmp_path):
    db = Database(db_name=tmp_path / "test.db")
    mode = db.conn.execute("PRAGMA journal_mode").fetchone()[0]
    db.close()
    assert mode.lower() == "wal"
