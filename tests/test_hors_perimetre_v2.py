import pytest

from database import Database


def _db(tmp_path, name="hors_perimetre.db"):
    return Database(db_name=tmp_path / name)


def test_schema_v10_autorise_ponte_zero_oeuf(tmp_path):
    db = _db(tmp_path, "schema_v10.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION

    colonnes = {
        row[1] for row in db.conn.execute("PRAGMA table_info(sorties_effectif)")
    }
    db.close()

    assert {"bande_id", "date", "nombre", "motif", "description"} <= colonnes


def test_ponte_zero_oeuf_enregistre_le_jour_sans_mouvement_stock(tmp_path):
    db = _db(tmp_path, "zero_oeuf.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 200, 0, activite="ponte")

    db.ajouter_ponte(bande_id, "2026-03-01", 0, "Repos de ponte")

    pontes = db.get_pontes(bande_id)
    assert pontes[0][3] == 0
    assert db.get_nombre_jours_ponte(bande_id) == 1
    assert db.get_total_oeufs(bande_id) == 0
    assert db.get_stock_oeufs(bande_id) == 0
    db.close()


def test_saisie_journaliere_accepte_zero_oeuf_explicite(tmp_path):
    db = _db(tmp_path, "zero_oeuf_quotidien.db")
    bande_id = db.ajouter_bande("Ponte B", "2026-01-01", 200, 0, activite="ponte")

    db.enregistrer_saisie_journaliere(bande_id, "2026-03-01", oeufs=0)

    assert db.get_pontes(bande_id)[0][3] == 0
    assert db.get_stock_oeufs(bande_id) == 0
    actions = db.get_journal_actions(action="saisie_journaliere")
    assert len(actions) == 1
    db.close()


def test_consommation_aliment_directe_reste_possible(tmp_path):
    db = _db(tmp_path, "aliment_direct.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)

    db.enregistrer_consommation_aliment(
        bande_id, "2026-01-10", 35, "Croissance", "Sans stock"
    )

    assert db.get_total_aliment_kg(bande_id) == 35
    db.close()


def test_consommation_aliment_depuis_stock_est_atomique(tmp_path):
    db = _db(tmp_path, "aliment_stock.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    stock_id = db.ajouter_article_stock("Aliment croissance", "aliment", "kg")
    db.ajouter_mouvement_stock(stock_id, "2026-01-02", "entree", 100)

    db.enregistrer_consommation_aliment(
        bande_id, "2026-01-10", 40, "Croissance", "Distribution", stock_id
    )

    assert db.get_stock_quantite(stock_id) == 60
    assert db.get_total_aliment_kg(bande_id) == 40
    mouvements = db.get_mouvements_stock(stock_id)
    assert mouvements[0][3] == "sortie"
    assert mouvements[0][5] == bande_id
    db.close()


def test_consommation_aliment_depuis_stock_refuse_categorie_non_aliment(tmp_path):
    db = _db(tmp_path, "aliment_categorie.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    stock_id = db.ajouter_article_stock("Vaccin", "medicament", "dose")
    db.ajouter_mouvement_stock(stock_id, "2026-01-02", "entree", 100)

    with pytest.raises(ValueError):
        db.enregistrer_consommation_aliment(
            bande_id, "2026-01-10", 40, stock_id=stock_id
        )

    assert db.get_stock_quantite(stock_id) == 100
    assert db.get_total_aliment_kg(bande_id) == 0
    db.close()


def test_sortie_effectif_reduit_restants_sans_mortalite_ni_vente(tmp_path):
    db = _db(tmp_path, "sortie_effectif.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)

    db.ajouter_sortie_effectif(bande_id, "2026-01-12", 12, "don", "Voisinage")

    assert db.get_poulets_restants(bande_id) == 88
    assert db.get_total_mortalites(bande_id) == 0
    assert db.get_total_vendus(bande_id) == 0
    assert db.get_total_sorties_effectif(bande_id) == 12
    sorties = db.get_sorties_effectif(bande_id)
    assert sorties[0][4] == "don"
    db.close()


def test_sortie_effectif_refuse_si_superieure_aux_restants(tmp_path):
    db = _db(tmp_path, "sortie_effectif_refus.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 10, 0)

    with pytest.raises(ValueError):
        db.ajouter_sortie_effectif(bande_id, "2026-01-12", 12, "reforme")

    assert db.get_poulets_restants(bande_id) == 10
    assert db.get_sorties_effectif(bande_id) == []
    db.close()


def test_supprimer_sortie_effectif_restaure_effectif(tmp_path):
    db = _db(tmp_path, "sortie_effectif_suppr.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_sortie_effectif(bande_id, "2026-01-12", 12, "reforme")
    sortie_id = db.get_sorties_effectif(bande_id)[0][0]

    db.supprimer_sortie_effectif(sortie_id)

    assert db.get_sorties_effectif(bande_id) == []
    assert db.get_poulets_restants(bande_id) == 100
    actions = db.get_journal_actions(action="suppression_sortie_effectif")
    assert len(actions) == 1
    db.close()
