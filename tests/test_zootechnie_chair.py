import pytest

from database import Database


def test_migration_phase2_tables_zootechniques(tmp_path):
    db = Database(db_name=tmp_path / "z.db")
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert {"consommations_aliment", "pesees"} <= tables


def test_consommations_aliment_totalisees(tmp_path):
    db = Database(db_name=tmp_path / "aliment.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_consommation_aliment(
        bande_id, "2026-01-08", 120.5, "Demarrage", "Matin"
    )
    db.ajouter_consommation_aliment(
        bande_id, "2026-01-09", 130, "Demarrage", "Soir"
    )

    assert db.get_total_aliment_kg(bande_id) == pytest.approx(250.5)
    rows = db.get_consommations_aliment(bande_id)
    db.close()
    assert [row[3] for row in rows] == [130, 120.5]


def test_pesees_ordonnees_et_derniere_pesee(tmp_path):
    db = Database(db_name=tmp_path / "pesees.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_pesee(bande_id, "2026-01-08", 250, 30, "Semaine 1")
    db.ajouter_pesee(bande_id, "2026-01-29", 1800, 30, "Semaine 4")

    assert db.get_first_pesee(bande_id)[3] == 250
    assert db.get_latest_pesee(bande_id)[3] == 1800
    rows = db.get_pesees(bande_id)
    db.close()
    assert [row[2] for row in rows] == ["2026-01-29", "2026-01-08"]


def test_migration_phase2b_colonne_poids_total(tmp_path):
    db = Database(db_name=tmp_path / "poids.db")
    colonnes = {
        row[1] for row in db.conn.execute("PRAGMA table_info(ventes)").fetchall()
    }
    db.close()
    assert "poids_total" in colonnes


def test_vente_avec_poids_total_est_totalisee(tmp_path):
    db = Database(db_name=tmp_path / "poids2.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_vente(bande_id, "2026-02-01", 600, 2000, poids_total=1080.0)
    db.ajouter_vente(bande_id, "2026-02-02", 400, 2000, poids_total=720.0)

    total = db.get_total_poids_vendu(bande_id)
    db.close()
    assert total == pytest.approx(1800.0)


def test_vente_sans_poids_total_ne_casse_pas_le_total(tmp_path):
    db = Database(db_name=tmp_path / "poids3.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_vente(bande_id, "2026-02-01", 1000, 2000)  # pas de poids_total

    total = db.get_total_poids_vendu(bande_id)
    db.close()
    assert total == 0


def test_zootechnie_refuse_valeurs_invalides(tmp_path):
    db = Database(db_name=tmp_path / "invalides.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    with pytest.raises(ValueError):
        db.ajouter_consommation_aliment(bande_id, "2026-01-08", 0)

    with pytest.raises(ValueError):
        db.ajouter_pesee(bande_id, "2026-01-08", 0, 30)

    with pytest.raises(ValueError):
        db.ajouter_pesee(bande_id, "2026-01-08", 250, 0)

    db.close()
