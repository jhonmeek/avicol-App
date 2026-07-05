import pytest

from database import Database
import reporting


def test_migration_v9_table_calibrages_oeufs(tmp_path):
    db = Database(db_name=tmp_path / "v9.db")
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    schema_version = db.get_schema_version()
    db.close()

    assert schema_version == db.SCHEMA_VERSION
    assert "calibrages_oeufs" in tables


def test_ajouter_calibrage_oeufs_et_repartition(tmp_path):
    db = Database(db_name=tmp_path / "calibrage.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 100, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-01-10", 500)

    db.ajouter_calibrage_oeufs(
        bande_id, "2026-01-11", "gros", 300, poids_moyen_g=62, observation="Lot A"
    )
    db.ajouter_calibrage_oeufs(bande_id, "2026-01-11", "moyen", 200)

    repartition = dict(db.get_calibrage_oeufs_par_categorie(bande_id))
    rows = db.get_calibrages_oeufs(bande_id)
    db.close()

    assert repartition == {"gros": 300, "moyen": 200}
    assert rows[0][3] == "moyen"
    assert rows[1][5] == 62


def test_calibrage_refuse_categorie_invalide_et_surproduction(tmp_path):
    db = Database(db_name=tmp_path / "calibrage_refus.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 100, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-01-10", 100)

    with pytest.raises(ValueError):
        db.ajouter_calibrage_oeufs(bande_id, "2026-01-11", "geant", 10)
    with pytest.raises(ValueError):
        db.ajouter_calibrage_oeufs(bande_id, "2026-01-11", "gros", 101)

    db.close()


def test_rapport_calibrage_oeufs_csv_et_fiche_agasa(tmp_path):
    db = Database(db_name=tmp_path / "calibrage_report.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 100, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-01-10", 500)
    db.ajouter_calibrage_oeufs(bande_id, "2026-01-11", "gros", 300, 62)

    rapport = reporting.build_calibrage_oeufs(db)
    rows = reporting.calibrage_oeufs_csv_rows(rapport)
    fiche = db.get_fiche_lot_agasa(bande_id)
    db.close()

    assert rapport["totaux"] == {"gros": 300}
    assert rows[0] == ["Date", "Lot", "Categorie", "Quantite", "Poids moyen g", "Observation"]
    assert rows[1][:4] == ["2026-01-11", "Ponte A", "gros", "300"]
    assert fiche["kpis"]["oeufs_calibres"] == 300
    assert "Calibrage oeufs" in [row["type"] for row in fiche["chronologie"]]
