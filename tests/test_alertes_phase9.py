from database import Database
import alerts


def test_alertes_operationnelles_detectent_les_quatre_familles(tmp_path):
    db = Database(db_name=tmp_path / "alertes.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-05", 6, "Stress")
    db.ajouter_consommation_aliment(bande_id, "2026-01-12", 500)
    db.ajouter_pesee(bande_id, "2026-01-15", 1000, 20)
    db.ajouter_article_stock("Vaccin Newcastle", "medicament", "dose", 10)
    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-10",
        "vaccination",
        "Gumboro",
        prochaine_echeance="2026-01-18",
    )

    alertes = db.get_alertes_operationnelles(date_reference="2026-01-15")
    db.close()

    types = {alerte["type"] for alerte in alertes}
    assert {"mortalite", "stock", "sanitaire", "ic"} <= types
    assert any(alerte["niveau"] == "critique" for alerte in alertes)
    assert any("Chair A" in alerte["detail"] for alerte in alertes)


def test_alertes_operationnelles_ne_signalent_pas_lot_conforme(tmp_path):
    db = Database(db_name=tmp_path / "alertes_ok.db")
    bande_id = db.ajouter_bande("Chair OK", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-05", 2)
    db.ajouter_consommation_aliment(bande_id, "2026-01-12", 100)
    db.ajouter_pesee(bande_id, "2026-01-15", 2000, 20)
    stock_id = db.ajouter_article_stock("Aliment croissance", "aliment", "kg", 10)
    db.ajouter_mouvement_stock(stock_id, "2026-01-01", "entree", 100)
    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-10",
        "vaccination",
        "Gumboro",
        prochaine_echeance="2026-02-15",
    )

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-15"
    )
    db.close()

    assert alertes == []


def test_alerte_sanitaire_en_retard_est_critique(tmp_path):
    db = Database(db_name=tmp_path / "alertes_retard.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-05",
        "vaccination",
        "Newcastle",
        prochaine_echeance="2026-01-10",
    )

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-15"
    )
    db.close()

    assert alertes[0]["type"] == "sanitaire"
    assert alertes[0]["niveau"] == "critique"
    assert "en retard" in alertes[0]["detail"]


def test_alertes_csv_rows_deterministes(tmp_path):
    db = Database(db_name=tmp_path / "alertes_csv.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_mortalite(bande_id, "2026-01-05", 12)

    alertes = alerts.build_alertes_operationnelles(
        db, date_reference="2026-01-15"
    )
    rows = alerts.alertes_csv_rows(alertes)
    db.close()

    assert rows[0] == ["Niveau", "Type", "Lot", "Titre", "Detail", "Valeur", "Seuil"]
    assert rows[1][0] == "critique"
    assert rows[1][1] == "mortalite"
