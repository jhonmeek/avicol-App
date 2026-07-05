import pytest
import indicators


def test_poulets_restants_ac1():
    assert indicators.poulets_restants(1000, 30, 900) == 70


def test_taux_mortalite_ac1():
    assert indicators.taux_mortalite(30, 1000) == pytest.approx(3.0)


def test_taux_viabilite_ac1():
    assert indicators.taux_viabilite(30, 1000) == pytest.approx(97.0)


def test_indicateurs_financiers_ac5():
    b = indicators.benefice(3_395_000, 2_400_000)
    assert b == 995_000
    assert indicators.roi(b, 2_400_000) == pytest.approx(41.46, abs=0.01)
    assert indicators.marge(b, 3_395_000) == pytest.approx(29.31, abs=0.01)


def test_bornes_effectif_initial_nul():
    assert indicators.taux_mortalite(0, 0) == 0.0
    assert indicators.roi(100, 0) == 0.0
    assert indicators.marge(100, 0) == 0.0


def test_poids_vif_estime():
    assert indicators.poids_vif_estime_kg(500, 1800) == pytest.approx(900.0)


def test_indice_consommation_reel():
    assert indicators.indice_consommation(1620, 900) == pytest.approx(1.8)


def test_gain_moyen_quotidien_reel():
    assert indicators.gain_moyen_quotidien(250, 1800, 28) == pytest.approx(55.36, abs=0.01)


def test_bornes_indicateurs_zootechniques():
    assert indicators.poids_vif_estime_kg(0, 1800) == 0.0
    assert indicators.indice_consommation(100, 0) == 0.0
    assert indicators.gain_moyen_quotidien(1800, 1700, 7) == 0.0
    assert indicators.gain_moyen_quotidien(250, 1800, 0) == 0.0


def test_poids_vif_produit_kg_combine_restant_et_vendu():
    assert indicators.poids_vif_produit_kg(300.0, 600.0) == pytest.approx(900.0)


def test_ic_fin_de_cycle_ne_s_effondre_pas_a_zero():
    # Lot entierement vendu : plus aucun sujet restant, mais le poids vendu
    # doit rester au denominateur de l'IC (sinon l'indice retombe a 0).
    poids_vif_restant = indicators.poids_vif_estime_kg(0, 1800)  # 0 restant
    poids_produit = indicators.poids_vif_produit_kg(poids_vif_restant, 1800.0)
    ic = indicators.indice_consommation(3240, poids_produit)
    assert poids_vif_restant == 0.0
    assert ic == pytest.approx(1.8)
