"""Calculs zootechniques et financiers — fonctions pures et testables.

Source de vérité unique des formules du tableau de bord (voir cahier des
charges §7 et §11). Aucune dépendance à l'IU ou à la base de données.
"""


def poulets_restants(initial, morts, vendus):
    return initial - morts - vendus


def taux_mortalite(morts, initial):
    return (morts / initial * 100) if initial > 0 else 0.0

def taux_viabilite(morts, initial):
    return (100.0 - taux_mortalite(morts, initial)) if initial > 0 else 0.0


def benefice(ventes, couts):
    return ventes - couts


def roi(benefice_net, couts):
    return (benefice_net / couts * 100) if couts > 0 else 0.0


def marge(benefice_net, ventes):
    return (benefice_net / ventes * 100) if ventes > 0 else 0.0


def prix_moyen(ventes, vendus):
    return (ventes / vendus) if vendus > 0 else 0.0


def efficacite(vendus, initial):
    return (vendus / initial * 100) if initial > 0 else 0.0


def poids_vif_estime_kg(effectif_present, poids_moyen_g):
    """Estime la biomasse vive du lot a partir de la derniere pesee."""
    if effectif_present <= 0 or poids_moyen_g <= 0:
        return 0.0
    return effectif_present * poids_moyen_g / 1000


def poids_vif_produit_kg(poids_vif_restant_kg, poids_vendu_kg):
    """Poids vif total produit par le lot = biomasse restante + poids vendu.

    Sans le poids vendu, l'IC s'effondre a 0 des que le lot est integralement
    vendu (plus aucun sujet ne reste au denominateur).
    """
    return (poids_vif_restant_kg or 0.0) + (poids_vendu_kg or 0.0)


def indice_consommation(aliment_kg, poids_vif_produit_kg):
    """IC/FCR = kg d'aliment consommes / kg de poids vif produit."""
    return (aliment_kg / poids_vif_produit_kg) if poids_vif_produit_kg > 0 else 0.0


def gain_moyen_quotidien(poids_initial_g, poids_final_g, jours):
    """GMQ = gain de poids moyen par sujet et par jour, en grammes."""
    if jours <= 0 or poids_final_g <= poids_initial_g:
        return 0.0
    return (poids_final_g - poids_initial_g) / jours


def taux_ponte(nombre_oeufs, poules_presentes):
    """Taux de ponte quotidien = oeufs pondus / poules presentes (%)."""
    return (nombre_oeufs / poules_presentes * 100) if poules_presentes > 0 else 0.0


def taux_ponte_moyen(total_oeufs, poules_presentes, nombre_jours):
    """Taux de ponte moyen sur la periode = total oeufs / (poules x jours), en %."""
    if poules_presentes <= 0 or nombre_jours <= 0:
        return 0.0
    return total_oeufs / (poules_presentes * nombre_jours) * 100
