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
