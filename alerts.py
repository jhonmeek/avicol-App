"""Alertes operationnelles visuelles.

Les alertes restent derivees des donnees existantes : pas de nouvelle table,
pas de nouvel etat a maintenir.
"""

from datetime import date, datetime, timedelta

import indicators


SEUIL_MORTALITE = 5.0
SEUIL_IC = 2.2
JOURS_ECHEANCE = 7
SEUIL_JOURS_SANS_SAISIE = 2


def _today_iso():
    return date.today().isoformat()


def _parse_iso(value):
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _days_between(date_debut, date_fin):
    try:
        return (_parse_iso(date_fin) - _parse_iso(date_debut)).days
    except (TypeError, ValueError):
        return 0


def _fmt_number(value, decimals=2):
    value = float(value or 0)
    if value.is_integer():
        return str(int(value))
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def _alert(niveau, type_, titre, detail, bande_id=None, bande_nom="", valeur=None,
           seuil=None, date_alerte=""):
    return {
        "niveau": niveau,
        "type": type_,
        "titre": titre,
        "detail": detail,
        "bande_id": bande_id,
        "bande_nom": bande_nom or "",
        "valeur": valeur,
        "seuil": seuil,
        "date": date_alerte or "",
    }


def _zootechnie_metrics(db, bande):
    bande_id = bande[0]
    restants = db.get_poulets_restants(bande_id) or 0
    total_aliment_kg = db.get_total_aliment_kg(bande_id) or 0
    latest_pesee = db.get_latest_pesee(bande_id)
    first_pesee = db.get_first_pesee(bande_id)
    poids_moyen_g = latest_pesee[3] if latest_pesee else 0
    poids_vif_restant_kg = indicators.poids_vif_estime_kg(
        restants, poids_moyen_g
    )
    poids_vendu_kg = db.get_total_poids_vendu(bande_id) or 0
    poids_vif_kg = indicators.poids_vif_produit_kg(
        poids_vif_restant_kg, poids_vendu_kg
    )
    ic = indicators.indice_consommation(total_aliment_kg, poids_vif_kg)
    gmq = 0.0
    if latest_pesee:
        if first_pesee and first_pesee[0] != latest_pesee[0]:
            jours = _days_between(first_pesee[2], latest_pesee[2])
            poids_initial_g = first_pesee[3]
        else:
            jours = _days_between(bande[2], latest_pesee[2])
            poids_initial_g = 0
        gmq = indicators.gain_moyen_quotidien(
            poids_initial_g, latest_pesee[3], jours
        )
    return {
        "aliment_kg": total_aliment_kg,
        "poids_vif_kg": poids_vif_kg,
        "poids_moyen_g": poids_moyen_g,
        "ic": ic,
        "gmq": gmq,
    }


def _alertes_mortalite(db, seuil_mortalite):
    alertes = []
    for bande in db.get_bandes():
        bande_id = bande[0]
        nom = bande[1]
        initial = bande[3] or 0
        morts = db.get_total_mortalites(bande_id) or 0
        taux = indicators.taux_mortalite(morts, initial)
        if taux > seuil_mortalite:
            niveau = "critique" if taux >= seuil_mortalite * 2 else "warning"
            alertes.append(
                _alert(
                    niveau,
                    "mortalite",
                    "Mortalite elevee",
                    f"{nom}: {taux:.1f}% de mortalite ({morts} sujets)",
                    bande_id,
                    nom,
                    taux,
                    seuil_mortalite,
                )
            )
    return alertes


def _alertes_ic(db, seuil_ic):
    alertes = []
    for bande in db.get_bandes():
        bande_id = bande[0]
        nom = bande[1]
        metrics = _zootechnie_metrics(db, bande)
        ic = metrics["ic"]
        if ic > seuil_ic:
            niveau = "critique" if ic >= seuil_ic * 1.3 else "warning"
            detail = (
                f"{nom}: IC {ic:.2f} pour "
                f"{metrics['aliment_kg']:.1f} kg d'aliment et "
                f"{metrics['poids_vif_kg']:.1f} kg vif"
            )
            alertes.append(
                _alert(
                    niveau,
                    "ic",
                    "Indice de consommation eleve",
                    detail,
                    bande_id,
                    nom,
                    ic,
                    seuil_ic,
                )
            )
    return alertes


def _alertes_stock(db):
    alertes = []
    for article in db.get_articles_stock():
        stock_id, nom_article, categorie, unite, seuil = article
        quantite = db.get_stock_quantite(stock_id) or 0
        if seuil > 0 and quantite < seuil:
            niveau = "critique" if quantite <= 0 else "warning"
            detail = (
                f"{nom_article}: {_fmt_number(quantite)} {unite} en stock "
                f"pour un seuil de {_fmt_number(seuil)}"
            )
            alertes.append(
                _alert(
                    niveau,
                    "stock",
                    "Stock sous seuil",
                    detail,
                    valeur=quantite,
                    seuil=seuil,
                )
            )
    return alertes


def _alertes_sanitaires(db, date_reference, jours_echeance):
    ref = _parse_iso(date_reference)
    limite = ref + timedelta(days=jours_echeance)
    alertes = []
    bandes = {bande[0]: bande[1] for bande in db.get_bandes()}
    for row in db.get_interventions_sanitaires():
        prochaine = row[7]
        if not prochaine:
            continue
        try:
            echeance = _parse_iso(prochaine)
        except (TypeError, ValueError):
            continue
        if echeance < ref:
            niveau = "critique"
            retard = (ref - echeance).days
            detail_suffix = f"en retard de {retard} jour(s)"
        elif echeance <= limite:
            niveau = "warning"
            restant = (echeance - ref).days
            detail_suffix = f"dans {restant} jour(s)"
        else:
            continue
        bande_nom = bandes.get(row[1], f"Lot #{row[1]}")
        alertes.append(
            _alert(
                niveau,
                "sanitaire",
                "Echeance sanitaire",
                f"{bande_nom}: {row[4]} {detail_suffix}",
                row[1],
                bande_nom,
                (echeance - ref).days,
                jours_echeance,
                prochaine,
            )
        )
    return alertes


def _alertes_saisie_manquante(db, date_reference, jours_sans_saisie):
    ref = _parse_iso(date_reference)
    alertes = []
    for bande in db.get_bandes():
        statut = bande[5] if len(bande) > 5 and bande[5] else "en_cours"
        if statut != "en_cours":
            continue
        derniere = db.get_derniere_date_saisie(bande[0])
        point_depart = derniere or bande[2]
        try:
            jours = (ref - _parse_iso(point_depart)).days
        except (TypeError, ValueError):
            continue
        if jours < jours_sans_saisie:
            continue
        niveau = "critique" if jours >= jours_sans_saisie * 3 else "warning"
        if derniere:
            detail = (
                f"{bande[1]}: aucune saisie depuis {jours} jour(s) "
                f"(derniere le {derniere})"
            )
        else:
            detail = (
                f"{bande[1]}: aucune saisie depuis {jours} jour(s) "
                "(aucune saisie enregistree pour ce lot)"
            )
        alertes.append(
            _alert(
                niveau,
                "saisie",
                "Saisie quotidienne manquante",
                detail,
                bande[0],
                bande[1],
                jours,
                jours_sans_saisie,
            )
        )
    return alertes


def build_alertes_operationnelles(
    db, date_reference=None, seuil_mortalite=SEUIL_MORTALITE,
    seuil_ic=SEUIL_IC, jours_echeance=JOURS_ECHEANCE,
    jours_sans_saisie=SEUIL_JOURS_SANS_SAISIE
):
    date_reference = date_reference or _today_iso()
    alertes = []
    alertes.extend(_alertes_mortalite(db, seuil_mortalite))
    alertes.extend(_alertes_stock(db))
    alertes.extend(_alertes_sanitaires(db, date_reference, jours_echeance))
    alertes.extend(_alertes_ic(db, seuil_ic))
    alertes.extend(
        _alertes_saisie_manquante(db, date_reference, jours_sans_saisie)
    )
    priority = {"critique": 0, "warning": 1, "info": 2}
    type_priority = {
        "mortalite": 0,
        "sanitaire": 1,
        "stock": 2,
        "ic": 3,
        "saisie": 4,
    }
    return sorted(
        alertes,
        key=lambda row: (
            priority.get(row["niveau"], 9),
            type_priority.get(row["type"], 99),
            row["type"],
            row["bande_nom"],
            row["titre"],
            row["detail"],
        ),
    )


def alertes_csv_rows(alertes):
    rows = [["Niveau", "Type", "Lot", "Titre", "Detail", "Valeur", "Seuil"]]
    for alerte in alertes:
        rows.append([
            alerte["niveau"],
            alerte["type"],
            alerte["bande_nom"],
            alerte["titre"],
            alerte["detail"],
            _fmt_number(alerte["valeur"]) if alerte["valeur"] is not None else "",
            _fmt_number(alerte["seuil"]) if alerte["seuil"] is not None else "",
        ])
    return rows


def alertes_text(alertes):
    lines = [
        "AVICOLE PRO",
        "ALERTES OPERATIONNELLES",
        f"Edite le {datetime.now():%d/%m/%Y a %H:%M}",
        "=" * 58,
        "",
    ]
    if not alertes:
        lines.append("Aucune alerte operationnelle.")
        return "\n".join(lines)

    for alerte in alertes:
        lot = f" - {alerte['bande_nom']}" if alerte["bande_nom"] else ""
        lines.append(
            f"[{alerte['niveau'].upper()}] {alerte['titre']}{lot}"
        )
        lines.append(f"  Type : {alerte['type']}")
        lines.append(f"  Detail : {alerte['detail']}")
        if alerte["valeur"] is not None or alerte["seuil"] is not None:
            lines.append(
                "  Valeur / seuil : "
                f"{_fmt_number(alerte['valeur']) if alerte['valeur'] is not None else '-'}"
                " / "
                f"{_fmt_number(alerte['seuil']) if alerte['seuil'] is not None else '-'}"
            )
        lines.append("")
    return "\n".join(lines).rstrip()
