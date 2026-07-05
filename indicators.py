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
