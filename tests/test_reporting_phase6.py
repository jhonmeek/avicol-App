from database import Database
import reporting


def test_fiche_lot_agasa_chair_trace_chronologique(tmp_path):
    db = Database(db_name=tmp_path / "agasa_chair.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 100)
    stock_id = db.ajouter_article_stock("Aliment demarrage", "aliment", "kg", 20)
    db.ajouter_mouvement_stock(stock_id, "2026-01-02", "entree", 200)
    db.ajouter_sortie_stock_aliment(
        stock_id, bande_id, "2026-01-05", 50, type_aliment="Demarrage"
    )
    db.ajouter_mortalite(bande_id, "2026-01-06", 5, "Stress", "Pic chaleur")
    db.ajouter_pesee(bande_id, "2026-01-15", 800, 20, "Controle S2")
    db.ajouter_intervention_sanitaire(
        bande_id, "2026-01-16", "vaccination", "Newcastle", dose="1 goutte"
    )
    db.ajouter_vente(
        bande_id, "2026-02-01", 80, 2500, client="Client A",
        paiement="Especes", poids_total=144
    )

    fiche = db.get_fiche_lot_agasa(bande_id)
    rows = reporting.fiche_lot_agasa_csv_rows(fiche)
    db.close()

    assert fiche["bande"]["nom"] == "Chair A"
    assert fiche["bande"]["activite"] == "chair"
    assert fiche["kpis"]["mortalites"] == 5
    assert fiche["kpis"]["aliment_kg"] == 50
    assert [row["type"] for row in fiche["chronologie"]] == [
        "Stock",
        "Aliment",
        "Mortalite",
        "Pesee",
        "Sanitaire",
        "Vente poulets",
    ]
    assert rows[0] == ["Date", "Type", "Detail", "Quantite", "Montant", "Reference"]
    assert rows[-1][2] == "80 sujets vendus a Client A"


def test_fiche_lot_agasa_ponte_inclut_oeufs_et_sanitaire(tmp_path):
    db = Database(db_name=tmp_path / "agasa_ponte.db")
    bande_id = db.ajouter_bande(
        "Ponte A", "2026-01-01", 50, 0, activite="ponte"
    )
    db.ajouter_ponte(bande_id, "2026-01-10", 500, "Bonne ponte")
    db.ajouter_vente_oeufs(bande_id, "2026-01-11", 300, 100, "Restaurant")
    db.ajouter_intervention_sanitaire(
        bande_id,
        "2026-01-12",
        "traitement",
        "Vitamines",
        prochaine_echeance="2026-01-26",
    )

    fiche = db.get_fiche_lot_agasa(bande_id)
    db.close()

    assert fiche["bande"]["activite"] == "ponte"
    assert fiche["kpis"]["oeufs_produits"] == 500
    assert fiche["kpis"]["stock_oeufs"] == 200
    assert fiche["kpis"]["ventes_oeufs"] == 30000
    assert [row["type"] for row in fiche["chronologie"]] == [
        "Ponte",
        "Vente oeufs",
        "Sanitaire",
    ]


def test_synthese_direction_alertes_echeances_et_csv(tmp_path):
    db = Database(db_name=tmp_path / "synthese.db")
    chair_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_vente(chair_id, "2026-02-01", 50, 2000, poids_total=90)
    db.ajouter_consommation_aliment(chair_id, "2026-01-15", 180)
    db.ajouter_pesee(chair_id, "2026-01-20", 1800, 20)
    db.ajouter_intervention_sanitaire(
        chair_id,
        "2026-01-10",
        "vaccination",
        "Gumboro",
        prochaine_echeance="2026-01-25",
    )

    ponte_id = db.ajouter_bande(
        "Ponte A", "2026-01-01", 80, 0, activite="ponte"
    )
    db.ajouter_ponte(ponte_id, "2026-01-10", 400)
    db.ajouter_vente_oeufs(ponte_id, "2026-01-11", 200, 100)

    db.ajouter_article_stock("Vaccin Newcastle", "medicament", "dose", 10)

    synthese = db.get_synthese_direction(date_reference="2026-01-15")
    rows = reporting.synthese_direction_csv_rows(synthese)
    texte = reporting.synthese_direction_text(synthese)
    db.close()

    assert synthese["rentabilite"]["chair"]["recettes"] == 100000
    assert synthese["rentabilite"]["ponte"]["recettes"] == 20000
    assert synthese["alertes_stock"][0]["nom_article"] == "Vaccin Newcastle"
    assert synthese["echeances_sanitaires"][0]["produit"] == "Gumboro"
    assert rows[0] == [
        "Lot",
        "Activite",
        "Recettes",
        "Couts",
        "Resultat",
        "Mortalite %",
        "IC",
        "GMQ g/j",
        "Taux ponte %",
    ]
    assert "SYNTHESE DIRECTION" in texte
    assert "ALERTES STOCK" in texte
