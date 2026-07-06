import pytest

from database import Database


def _db(tmp_path, name="quotidien.db"):
    return Database(db_name=tmp_path / name)


def test_derniere_date_saisie_prend_le_max_toutes_tables(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-05", 2)
    db.ajouter_consommation_aliment(bande_id, "2026-01-08", 50)
    db.ajouter_depense(bande_id, "2026-01-03", "litiere", 10000)

    assert db.get_derniere_date_saisie(bande_id) == "2026-01-08"
    db.close()


def test_derniere_date_saisie_sans_aucune_saisie(tmp_path):
    db = _db(tmp_path, "vide.db")
    bande_id = db.ajouter_bande("Chair B", "2026-01-01", 100, 0)

    assert db.get_derniere_date_saisie(bande_id) is None
    db.close()


def test_compter_saisies_du_jour_detecte_les_doublons(tmp_path):
    db = _db(tmp_path, "doublons.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-03-01", 150)
    db.ajouter_mortalite(bande_id, "2026-03-01", 1)

    compte = db.compter_saisies_du_jour(bande_id, "2026-03-01")
    assert compte == {"mortalites": 1, "aliment": 0, "pontes": 1}

    compte_veille = db.compter_saisies_du_jour(bande_id, "2026-02-28")
    assert compte_veille == {"mortalites": 0, "aliment": 0, "pontes": 0}
    db.close()


def test_saisie_journaliere_complete(tmp_path):
    db = _db(tmp_path, "journaliere.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")

    db.enregistrer_saisie_journaliere(
        bande_id, "2026-03-01", morts=2, cause="Cause inconnue",
        aliment_kg=25.5, type_aliment="Ponte phase 1", oeufs=160,
    )

    assert db.get_total_mortalites(bande_id) == 2
    assert db.get_total_aliment_kg(bande_id) == 25.5
    assert db.get_total_oeufs(bande_id) == 160
    assert db.get_stock_oeufs(bande_id) == 160
    db.close()


def test_saisie_journaliere_partielle(tmp_path):
    db = _db(tmp_path, "partielle.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)

    db.enregistrer_saisie_journaliere(bande_id, "2026-01-10", aliment_kg=40)

    assert db.get_total_aliment_kg(bande_id) == 40
    assert db.get_total_mortalites(bande_id) == 0
    assert db.get_total_oeufs(bande_id) == 0
    db.close()


def test_saisie_journaliere_vide_refusee(tmp_path):
    db = _db(tmp_path, "vide2.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)

    with pytest.raises(ValueError):
        db.enregistrer_saisie_journaliere(bande_id, "2026-01-10")
    db.close()


def test_saisie_journaliere_atomique_si_mortalite_invalide(tmp_path):
    db = _db(tmp_path, "atomique.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 10, 0)

    with pytest.raises(ValueError):
        db.enregistrer_saisie_journaliere(
            bande_id, "2026-01-10", morts=50, aliment_kg=40
        )

    assert db.get_total_aliment_kg(bande_id) == 0
    assert db.get_total_mortalites(bande_id) == 0
    db.close()


def test_saisie_journaliere_tracee_dans_le_journal(tmp_path):
    db = _db(tmp_path, "journal.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)

    db.enregistrer_saisie_journaliere(bande_id, "2026-01-10", morts=1)

    actions = db.get_journal_actions(action="saisie_journaliere")
    assert len(actions) == 1
    db.close()
