from database import Database


def test_rentabilite_separee_par_activite(tmp_path):
    db = Database(db_name=tmp_path / "rent1.db")

    chair_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_vente(chair_id, "2026-02-01", 50, 2000)

    ponte_id = db.ajouter_bande(
        "Ponte A", "2026-01-01", 100, 0, activite="ponte"
    )
    db.ajouter_ponte(ponte_id, "2026-03-01", 500)
    db.ajouter_vente_oeufs(ponte_id, "2026-03-02", 300, 100)

    rent = db.get_rentabilite_par_activite()
    db.close()

    assert rent["chair"]["recettes"] == 100000
    assert rent["chair"]["benefice"] == 100000
    assert rent["chair"]["nb_lots"] == 1
    assert rent["ponte"]["recettes"] == 30000
    assert rent["ponte"]["benefice"] == 30000
    assert rent["ponte"]["nb_lots"] == 1


def test_rentabilite_bande_sans_activite_comptee_en_chair(tmp_path):
    db = Database(db_name=tmp_path / "rent2.db")
    db.ajouter_bande("Legacy", "2026-01-01", 100, 0)

    rent = db.get_rentabilite_par_activite()
    db.close()

    assert rent["chair"]["nb_lots"] == 1
    assert rent["ponte"]["nb_lots"] == 0


def test_rentabilite_deduit_depenses_par_activite(tmp_path):
    db = Database(db_name=tmp_path / "rent3.db")

    chair_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_vente(chair_id, "2026-02-01", 50, 2000)
    db.ajouter_depense(chair_id, "2026-01-10", "Aliment", 25000)

    ponte_id = db.ajouter_bande(
        "Ponte A", "2026-01-01", 100, 0, activite="ponte"
    )
    db.ajouter_ponte(ponte_id, "2026-03-01", 500)
    db.ajouter_vente_oeufs(ponte_id, "2026-03-02", 300, 100)
    db.ajouter_depense(ponte_id, "2026-03-03", "Aliment", 5000)

    rent = db.get_rentabilite_par_activite()
    db.close()

    assert rent["chair"]["couts"] == 25000
    assert rent["chair"]["benefice"] == 75000
    assert rent["ponte"]["couts"] == 5000
    assert rent["ponte"]["benefice"] == 25000
