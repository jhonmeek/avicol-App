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


def test_ajouter_bande_activite_defaut_chair_et_explicite_ponte(tmp_path):
    db = Database(db_name=tmp_path / "activite.db")
    id_chair = db.ajouter_bande("Lot A", "2026-01-01", 1000, 500)
    id_ponte = db.ajouter_bande(
        "Lot Pondeuses", "2026-01-01", 200, 1500, activite="ponte"
    )
    info_chair = db.get_bande_info(id_chair)
    info_ponte = db.get_bande_info(id_ponte)
    db.close()
    assert info_chair[6] == "chair"
    assert info_ponte[6] == "ponte"


def test_mortalite_fonctionne_sur_lot_ponte(tmp_path):
    db = Database(db_name=tmp_path / "mortalite_ponte.db")
    bande_id = db.ajouter_bande(
        "Lot Pondeuses", "2026-01-01", 200, 1500, activite="ponte"
    )
    db.ajouter_mortalite(bande_id, "2026-01-10", 5)
    restants = db.get_poulets_restants(bande_id)
    db.close()
    assert restants == 195


def _bande_ponte(db, effectif=200):
    return db.ajouter_bande(
        "Lot Pondeuses", "2026-01-01", effectif, 1500, activite="ponte"
    )


def test_ajouter_ponte_credite_stock_et_totalise(tmp_path):
    db = Database(db_name=tmp_path / "ponte1.db")
    bande_id = _bande_ponte(db)

    db.ajouter_ponte(bande_id, "2026-03-01", 180)
    db.ajouter_ponte(bande_id, "2026-03-02", 185)

    total = db.get_total_oeufs(bande_id)
    jours = db.get_nombre_jours_ponte(bande_id)
    rows = db.get_pontes(bande_id)
    db.close()
    assert total == 365
    assert jours == 2
    assert [row[2] for row in rows] == ["2026-03-02", "2026-03-01"]


def test_ajouter_ponte_refuse_valeur_invalide(tmp_path):
    db = Database(db_name=tmp_path / "ponte2.db")
    bande_id = _bande_ponte(db)
    with pytest.raises(ValueError):
        db.ajouter_ponte(bande_id, "2026-03-01", -1)
    db.close()


def test_stock_oeufs_ac3(tmp_path):
    db = Database(db_name=tmp_path / "stock_ac3.db")
    bande_id = _bande_ponte(db)

    db.ajouter_ponte(bande_id, "2026-03-01", 600)
    db.ajouter_ponte(bande_id, "2026-03-02", 600)
    db.ajouter_ponte(bande_id, "2026-03-03", 600)  # total 1800

    db.ajouter_vente_oeufs(bande_id, "2026-03-04", 1200, 100)

    stock = db.get_stock_oeufs(bande_id)
    db.close()
    assert stock == 600  # AC-3 : 1800 pondus, 1200 vendus -> stock 600


def test_vente_oeufs_refusee_si_stock_insuffisant(tmp_path):
    db = Database(db_name=tmp_path / "stock_guard.db")
    bande_id = _bande_ponte(db)
    db.ajouter_ponte(bande_id, "2026-03-01", 100)
    with pytest.raises(ValueError):
        db.ajouter_vente_oeufs(bande_id, "2026-03-02", 150, 100)
    db.close()


def test_get_ventes_oeufs_et_total(tmp_path):
    db = Database(db_name=tmp_path / "ventes_oeufs.db")
    bande_id = _bande_ponte(db)
    db.ajouter_ponte(bande_id, "2026-03-01", 500)
    db.ajouter_vente_oeufs(bande_id, "2026-03-02", 300, 120, client="Marche central")

    total_ventes = db.get_total_ventes_oeufs(bande_id)
    rows = db.get_ventes_oeufs(bande_id)
    db.close()
    assert total_ventes == 36000
    assert rows[0][3] == 300  # quantite
    assert rows[0][4] == 120  # prix_unitaire
    assert rows[0][5] == 36000  # montant
    assert rows[0][6] == "Marche central"  # client
