import pytest

from database import Database


def test_migration_v6_table_interventions(tmp_path):
    db = Database(db_name=tmp_path / "v6.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert "interventions_sanitaires" in tables


def test_ajouter_intervention_et_lister(tmp_path):
    db = Database(db_name=tmp_path / "int1.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-08",
        "vaccination",
        "Newcastle",
        dose="1 goutte",
        intervenant="Dr Nze",
        prochaine_echeance="2026-01-22",
    )
    db.ajouter_intervention_sanitaire(
        bande_id, "2026-01-10", "traitement", "Anticoccidien", dose="2 ml/L"
    )

    rows = db.get_interventions_sanitaires(bande_id)
    db.close()
    assert len(rows) == 2
    assert rows[0][2] == "2026-01-10"
    assert rows[1][4] == "Newcastle"


def test_ajouter_intervention_refuse_type_invalide(tmp_path):
    db = Database(db_name=tmp_path / "int2.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    with pytest.raises(ValueError):
        db.ajouter_intervention_sanitaire(
            bande_id, "2026-01-08", "chirurgie", "Produit X"
        )

    db.close()


def test_ajouter_intervention_refuse_produit_vide(tmp_path):
    db = Database(db_name=tmp_path / "int3.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    with pytest.raises(ValueError):
        db.ajouter_intervention_sanitaire(
            bande_id, "2026-01-08", "vaccination", ""
        )

    db.close()


def test_interventions_a_venir(tmp_path):
    db = Database(db_name=tmp_path / "echeances.db")
    bande_id = db.ajouter_bande("Lot chair", "2026-01-01", 1000, 500)

    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-01",
        "vaccination",
        "Marek",
        prochaine_echeance="2026-01-10",
    )
    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-05",
        "vaccination",
        "Gumboro",
        prochaine_echeance="2026-01-25",
    )
    db.ajouter_intervention_sanitaire(
        bande_id, "2026-01-06", "traitement", "Vitamines"
    )

    a_venir = db.get_interventions_a_venir("2026-01-15")
    db.close()
    produits = [row[4] for row in a_venir]
    assert produits == ["Gumboro"]
