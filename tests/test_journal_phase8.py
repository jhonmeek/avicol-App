import pytest

from database import Database


def test_migration_v8_table_journal_actions(tmp_path):
    db = Database(db_name=tmp_path / "v8.db")
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()

    assert db.SCHEMA_VERSION == 8
    assert "journal_actions" in tables


def test_journal_trace_creation_depense_vente(tmp_path):
    db = Database(db_name=tmp_path / "journal.db")
    bande_id = db.ajouter_bande("Lot A", "2026-01-01", 100, 500)
    db.ajouter_depense(bande_id, "2026-01-05", "Aliment", 15000)
    db.ajouter_vente(bande_id, "2026-02-01", 20, 2500, client="Client A")

    rows = db.get_journal_actions()
    db.close()

    actions = [row[2] for row in rows]
    assert actions[:3] == ["vente_poulets", "depense", "creation_bande"]
    assert rows[0][3] == "ventes"
    assert rows[0][5] == "20 sujets vendus pour 50000 FCFA"
    assert rows[2][4] == bande_id


def test_journal_filtre_par_entite_et_limite(tmp_path):
    db = Database(db_name=tmp_path / "journal_filtre.db")
    bande_id = db.ajouter_bande("Lot A", "2026-01-01", 100, 500)
    db.ajouter_mortalite(bande_id, "2026-01-03", 2, "Stress")
    db.ajouter_depense(bande_id, "2026-01-05", "Aliment", 15000)

    mortalites = db.get_journal_actions(entite="mortalites")
    limited = db.get_journal_actions(limit=1)
    db.close()

    assert [row[2] for row in mortalites] == ["mortalite"]
    assert len(limited) == 1
    assert limited[0][2] == "depense"


def test_journal_ne_trace_pas_vente_refusee(tmp_path):
    db = Database(db_name=tmp_path / "journal_refus.db")
    bande_id = db.ajouter_bande("Lot A", "2026-01-01", 10, 500)

    with pytest.raises(ValueError):
        db.ajouter_vente(bande_id, "2026-02-01", 20, 2500)

    actions = [row[2] for row in db.get_journal_actions()]
    db.close()

    assert actions == ["creation_bande"]
