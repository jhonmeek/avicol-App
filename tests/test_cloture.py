from database import Database


def test_cloturer_bande_change_statut(tmp_path):
    db = Database(db_name=tmp_path / "c.db")
    bande_id = db.ajouter_bande("Lot A", "2026-01-01", 100, 500)
    db.cloturer_bande(bande_id)
    statut = db.get_bande_info(bande_id)[5]  # colonne statut
    db.close()
    assert statut == "cloture"
