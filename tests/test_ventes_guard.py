import pytest
from database import Database


def _bande_avec_effectif_50(tmp_path):
    db = Database(db_name=tmp_path / "v.db")
    bande_id = db.ajouter_bande("Test", "2026-01-01", 100, 500)
    db.ajouter_mortalite(bande_id, "2026-01-05", 20)
    db.ajouter_vente(bande_id, "2026-01-10", 30, 2000)  # restants = 50
    return db, bande_id


def test_vente_refusee_si_superieure_effectif(tmp_path):
    db, bande_id = _bande_avec_effectif_50(tmp_path)
    with pytest.raises(ValueError):
        db.ajouter_vente(bande_id, "2026-01-11", 60, 2000)
    db.close()


def test_vente_egale_effectif_acceptee(tmp_path):
    db, bande_id = _bande_avec_effectif_50(tmp_path)
    db.ajouter_vente(bande_id, "2026-01-11", 50, 2000)
    assert db.get_poulets_restants(bande_id) == 0
    db.close()
