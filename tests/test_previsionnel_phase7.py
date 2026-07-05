from database import Database
import reporting


def test_migration_v7_table_previsions(tmp_path):
    db = Database(db_name=tmp_path / "v7.db")
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert db.SCHEMA_VERSION == 7
    assert "previsions_lot" in tables


def test_previsionnel_vs_reel_chair_ecarts_et_csv(tmp_path):
    db = Database(db_name=tmp_path / "prev_chair.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 100)
    db.ajouter_depense(bande_id, "2026-01-10", "Aliment", 20000)
    db.ajouter_vente(bande_id, "2026-02-01", 80, 1500, poids_total=120)
    db.enregistrer_prevision_lot(
        bande_id,
        cout_poussins_prevu=10000,
        cout_aliment_prevu=25000,
        cout_sanitaire_prevu=5000,
        autres_charges_prevues=10000,
        quantite_vendue_prevue=90,
        prix_vente_unitaire_prevu=1600,
    )

    rapport = db.get_previsionnel_reel()
    rows = reporting.previsionnel_reel_csv_rows(rapport)
    db.close()

    lot = rapport["lots"][0]
    assert lot["lot"]["nom"] == "Chair A"
    assert lot["prevision"]["recettes"] == 144000
    assert lot["prevision"]["couts"] == 50000
    assert lot["prevision"]["resultat"] == 94000
    assert lot["reel"]["recettes"] == 120000
    assert lot["reel"]["couts"] == 30000
    assert lot["reel"]["resultat"] == 90000
    assert lot["ecarts"]["resultat"] == -4000
    assert rows[0] == [
        "Lot",
        "Activite",
        "Recettes prevues",
        "Recettes reelles",
        "Ecart recettes",
        "Ecart recettes %",
        "Couts prevus",
        "Couts reels",
        "Ecart couts",
        "Ecart couts %",
        "Resultat prevu",
        "Resultat reel",
        "Ecart resultat",
        "Ecart resultat %",
    ]
    assert rows[1][:6] == ["Chair A", "chair", "144000", "120000", "-24000", "-16.67"]


def test_previsionnel_vs_reel_ponte_utilise_oeufs_prevus(tmp_path):
    db = Database(db_name=tmp_path / "prev_ponte.db")
    bande_id = db.ajouter_bande("Ponte A", "2026-01-01", 100, 0, activite="ponte")
    db.ajouter_ponte(bande_id, "2026-01-10", 1000)
    db.ajouter_vente_oeufs(bande_id, "2026-01-11", 800, 100, "Hotel")
    db.enregistrer_prevision_lot(
        bande_id,
        cout_aliment_prevu=30000,
        cout_sanitaire_prevu=5000,
        oeufs_prevus=1000,
        prix_oeuf_prevu=120,
    )

    rapport = db.get_previsionnel_reel()
    texte = reporting.previsionnel_reel_text(rapport)
    db.close()

    lot = rapport["lots"][0]
    assert lot["prevision"]["recettes"] == 120000
    assert lot["prevision"]["couts"] == 35000
    assert lot["reel"]["recettes"] == 80000
    assert lot["reel"]["couts"] == 0
    assert "PREVISIONNEL VS REEL" in texte
    assert "Ponte A" in texte


def test_synthese_direction_inclut_previsionnel_vs_reel(tmp_path):
    db = Database(db_name=tmp_path / "synthese_prev.db")
    bande_id = db.ajouter_bande("Chair A", "2026-01-01", 100, 0)
    db.ajouter_vente(bande_id, "2026-02-01", 50, 2000)
    db.enregistrer_prevision_lot(
        bande_id,
        cout_aliment_prevu=10000,
        quantite_vendue_prevue=50,
        prix_vente_unitaire_prevu=1800,
    )

    synthese = db.get_synthese_direction(date_reference="2026-01-15")
    texte = reporting.synthese_direction_text(synthese)
    db.close()

    assert synthese["previsionnel"]["totaux"]["recettes"]["prevu"] == 90000
    assert synthese["previsionnel"]["totaux"]["recettes"]["reel"] == 100000
    assert "PREVISIONNEL VS REEL" in texte
