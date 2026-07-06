from database import Database
import alerts


def _db(tmp_path, name="alertes_saisie.db"):
    return Database(db_name=tmp_path / name)


def test_alerte_si_aucune_saisie_depuis_le_seuil(tmp_path):
    db = _db(tmp_path)
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-10", 1)

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-13"
    )
    db.close()

    saisie = [a for a in alertes if a["type"] == "saisie"]
    assert len(saisie) == 1
    assert saisie[0]["niveau"] == "warning"
    assert "3 jour(s)" in saisie[0]["detail"]


def test_alerte_critique_apres_trois_fois_le_seuil(tmp_path):
    db = _db(tmp_path, "critique.db")
    db.ajouter_bande("Chair B", "2026-01-01", 100, 0)

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-15"
    )
    db.close()

    saisie = [a for a in alertes if a["type"] == "saisie"]
    assert len(saisie) == 1
    assert saisie[0]["niveau"] == "critique"


def test_pas_d_alerte_si_saisie_recente(tmp_path):
    db = _db(tmp_path, "recente.db")
    bande_id = db.ajouter_bande("Chair C", "2026-01-01", 100, 0)
    db.ajouter_consommation_aliment(bande_id, "2026-01-14", 40)

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-15"
    )
    db.close()

    assert [a for a in alertes if a["type"] == "saisie"] == []


def test_pas_d_alerte_pour_bande_cloturee(tmp_path):
    db = _db(tmp_path, "cloture.db")
    bande_id = db.ajouter_bande("Chair D", "2026-01-01", 100, 0)
    db.cloturer_bande(bande_id)

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-02-15"
    )
    db.close()

    assert [a for a in alertes if a["type"] == "saisie"] == []
