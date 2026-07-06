import pytest

from database import Database


def _db(tmp_path, name="suppr.db"):
    return Database(db_name=tmp_path / name)


def test_supprimer_mortalite_restaure_effectif(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 500)
    db.ajouter_mortalite(bande_id, "2026-01-05", 10, "Stress")
    mortalite_id = db.get_mortalites(bande_id)[0][0]

    db.supprimer_mortalite(mortalite_id)

    assert db.get_mortalites(bande_id) == []
    assert db.get_poulets_restants(bande_id) == 100
    db.close()


def test_supprimer_mortalite_inexistante_leve_erreur(tmp_path):
    db = _db(tmp_path)
    with pytest.raises(ValueError):
        db.supprimer_mortalite(999)
    db.close()


def test_supprimer_depense_recalcule_couts(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_depense(bande_id, "2026-01-05", "aliment", 50000)
    depense_id = db.get_depenses(bande_id)[0][0]

    db.supprimer_depense(depense_id)

    assert db.get_total_depenses(bande_id) == 0
    db.close()


def test_supprimer_vente_restaure_effectif_et_recettes(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_vente(bande_id, "2026-02-01", 40, 3000)
    vente_id = db.get_ventes(bande_id)[0][0]

    db.supprimer_vente(vente_id)

    assert db.get_total_ventes(bande_id) == 0
    assert db.get_poulets_restants(bande_id) == 100
    db.close()


def test_supprimer_consommation_aliment_recalcule_ic(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_consommation_aliment(bande_id, "2026-01-10", 250)
    conso_id = db.get_consommations_aliment(bande_id)[0][0]

    db.supprimer_consommation_aliment(conso_id)

    assert db.get_total_aliment_kg(bande_id) == 0
    db.close()


def test_supprimer_pesee(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_pesee(bande_id, "2026-01-15", 950, 20)
    pesee_id = db.get_pesees(bande_id)[0][0]

    db.supprimer_pesee(pesee_id)

    assert db.get_pesees(bande_id) == []
    assert db.get_latest_pesee(bande_id) is None
    db.close()


def test_suppression_tracee_dans_le_journal(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-05", 3)
    mortalite_id = db.get_mortalites(bande_id)[0][0]

    db.supprimer_mortalite(mortalite_id)

    actions = db.get_journal_actions(action="suppression_mortalite")
    assert len(actions) == 1
    assert actions[0][4] == mortalite_id
    db.close()


def test_supprimer_ponte_retire_production_et_stock(tmp_path):
    db = _db(tmp_path, "oeufs.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-03-01", 150)
    ponte_id = db.get_pontes(bande_id)[0][0]

    db.supprimer_ponte(ponte_id)

    assert db.get_total_oeufs(bande_id) == 0
    assert db.get_stock_oeufs(bande_id) == 0
    db.close()


def test_supprimer_ponte_refusee_si_oeufs_deja_vendus(tmp_path):
    db = _db(tmp_path, "oeufs_vendus.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-03-01", 100)
    db.ajouter_vente_oeufs(bande_id, "2026-03-02", 80, 100)
    ponte_id = db.get_pontes(bande_id)[0][0]

    with pytest.raises(ValueError):
        db.supprimer_ponte(ponte_id)
    assert db.get_total_oeufs(bande_id) == 100
    db.close()


def test_supprimer_ponte_refusee_si_oeufs_deja_calibres(tmp_path):
    db = _db(tmp_path, "oeufs_calibres.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-03-01", 100)
    db.ajouter_ponte(bande_id, "2026-03-02", 50)
    db.ajouter_calibrage_oeufs(bande_id, "2026-03-02", "moyen", 120)
    premiere_ponte_id = db.get_pontes(bande_id)[-1][0]

    with pytest.raises(ValueError):
        db.supprimer_ponte(premiere_ponte_id)
    db.close()


def test_supprimer_vente_oeufs_restaure_le_stock(tmp_path):
    db = _db(tmp_path, "vente_oeufs.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-03-01", 100)
    db.ajouter_vente_oeufs(bande_id, "2026-03-02", 60, 100)
    vente_id = db.get_ventes_oeufs(bande_id)[0][0]

    db.supprimer_vente_oeufs(vente_id)

    assert db.get_stock_oeufs(bande_id) == 100
    assert db.get_total_ventes_oeufs(bande_id) == 0
    db.close()
