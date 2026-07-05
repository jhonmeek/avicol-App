"""Reporting direction et fiche de lot AGASA.

Ce module transforme les donnees deja presentes en base en structures
testables, puis en apercus texte ou lignes CSV.
"""

from datetime import datetime

import indicators


def today_iso():
    return datetime.now().strftime("%Y-%m-%d")


def _days_between(date_debut, date_fin):
    try:
        debut = datetime.strptime(str(date_debut), "%Y-%m-%d")
        fin = datetime.strptime(str(date_fin), "%Y-%m-%d")
    except (TypeError, ValueError):
        return 0
    return (fin - debut).days


def _num(value):
    return value if value is not None else 0


def _csv_number(value, decimals=2):
    value = float(value or 0)
    if value.is_integer():
        return str(int(value))
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def _format_money(value):
    return f"{float(value or 0):,.0f} FCFA"


def _format_percent(value):
    return f"{float(value or 0):.2f}%"


def _bande_dict(bande):
    if not bande:
        return {}
    return {
        "id": bande[0],
        "nom": bande[1],
        "date_debut": bande[2],
        "effectif_initial": bande[3] or 0,
        "prix_achat_poussin": bande[4] or 0,
        "statut": bande[5] if len(bande) > 5 and bande[5] else "en_cours",
        "activite": bande[6] if len(bande) > 6 and bande[6] else "chair",
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
        "poids_moyen_g": poids_moyen_g,
        "poids_vif_kg": poids_vif_kg,
        "ic": ic,
        "gmq": gmq,
    }


def _lot_metrics(db, bande):
    bande_id = bande[0]
    bande_info = _bande_dict(bande)
    activite = bande_info["activite"]
    initial = bande_info["effectif_initial"]
    mortalites = db.get_total_mortalites(bande_id) or 0
    restants = db.get_poulets_restants(bande_id) or 0
    vendus = db.get_total_vendus(bande_id) or 0
    cout_initial = db.get_cout_initial(bande_id) or 0
    depenses = db.get_total_depenses(bande_id) or 0
    couts = db.get_total_couts(bande_id) or 0
    recettes_poulets = db.get_total_ventes(bande_id) or 0
    recettes_oeufs = db.get_total_ventes_oeufs(bande_id) or 0
    recettes_activite = (
        recettes_oeufs if activite == "ponte" else recettes_poulets
    )
    zootech = _zootechnie_metrics(db, bande)
    oeufs_produits = db.get_total_oeufs(bande_id) or 0
    jours_ponte = db.get_nombre_jours_ponte(bande_id) or 0
    stock_oeufs = db.get_stock_oeufs(bande_id) or 0
    taux_ponte = indicators.taux_ponte_moyen(
        oeufs_produits, restants, jours_ponte
    )
    return {
        **bande_info,
        "mortalites": mortalites,
        "restants": restants,
        "vendus": vendus,
        "cout_initial": cout_initial,
        "depenses": depenses,
        "couts": couts,
        "recettes_poulets": recettes_poulets,
        "recettes_oeufs": recettes_oeufs,
        "recettes_activite": recettes_activite,
        "resultat": recettes_activite - couts,
        "taux_mortalite": indicators.taux_mortalite(mortalites, initial),
        "aliment_kg": zootech["aliment_kg"],
        "poids_moyen_g": zootech["poids_moyen_g"],
        "poids_vif_kg": zootech["poids_vif_kg"],
        "ic": zootech["ic"],
        "gmq": zootech["gmq"],
        "oeufs_produits": oeufs_produits,
        "stock_oeufs": stock_oeufs,
        "ventes_oeufs": recettes_oeufs,
        "jours_ponte": jours_ponte,
        "taux_ponte": taux_ponte,
    }


def _event(date, type_, detail, quantite="", montant="", reference="", order=50):
    return {
        "date": date or "",
        "type": type_,
        "detail": detail or "",
        "quantite": quantite,
        "montant": montant,
        "reference": reference or "",
        "_order": order,
    }


def _article_map(db):
    return {
        article[0]: {
            "nom_article": article[1],
            "categorie": article[2],
            "unite": article[3],
            "seuil_alerte": article[4],
        }
        for article in db.get_articles_stock()
    }


def _stock_events(db, bande_id):
    articles = _article_map(db)
    direct_rows = db.get_mouvements_stock_par_bande(bande_id)
    stock_ids = {row[1] for row in direct_rows}
    events = []
    added_ids = set()

    for row in direct_rows:
        article = articles.get(row[1], {})
        motif = row[6] or ""
        if (
            article.get("categorie") == "aliment"
            and row[3] == "sortie"
            and motif.startswith("Consommation aliment")
        ):
            continue
        detail = (
            f"{row[3]} stock {article.get('nom_article', row[1])}"
            f" ({motif})" if motif else
            f"{row[3]} stock {article.get('nom_article', row[1])}"
        )
        events.append(
            _event(
                row[2],
                "Stock",
                detail,
                _csv_number(row[4]),
                "",
                f"stock#{row[1]}",
                10,
            )
        )
        added_ids.add(row[0])

    for stock_id in sorted(stock_ids):
        article = articles.get(stock_id, {})
        for row in db.get_mouvements_stock(stock_id=stock_id):
            if row[0] in added_ids or row[5] is not None or row[3] != "entree":
                continue
            motif = row[6] or ""
            detail = (
                f"entree stock {article.get('nom_article', stock_id)}"
                f" ({motif})" if motif else
                f"entree stock {article.get('nom_article', stock_id)}"
            )
            events.append(
                _event(
                    row[2],
                    "Stock",
                    detail,
                    _csv_number(row[4]),
                    "",
                    f"stock#{stock_id}",
                    10,
                )
            )
    return events


def _chronologie(db, bande_id):
    events = []
    events.extend(_stock_events(db, bande_id))

    for row in db.get_consommations_aliment(bande_id):
        type_aliment = f" {row[4]}" if row[4] else ""
        observation = f" - {row[5]}" if row[5] else ""
        events.append(
            _event(
                row[2],
                "Aliment",
                f"{_csv_number(row[3])} kg{type_aliment}{observation}",
                _csv_number(row[3]),
                "",
                f"aliment#{row[0]}",
                20,
            )
        )

    for row in db.get_mortalites(bande_id):
        cause = f" - {row[4]}" if row[4] else ""
        description = f" - {row[5]}" if row[5] else ""
        events.append(
            _event(
                row[2],
                "Mortalite",
                f"{row[3]} morts{cause}{description}",
                row[3],
                "",
                f"mortalite#{row[0]}",
                30,
            )
        )

    for row in db.get_depenses(bande_id):
        fournisseur = f" - {row[6]}" if row[6] else ""
        description = f" - {row[4]}" if row[4] else ""
        events.append(
            _event(
                row[2],
                "Depense",
                f"{row[3]}{description}{fournisseur}",
                "",
                _csv_number(row[5]),
                f"depense#{row[0]}",
                40,
            )
        )

    for row in db.get_pesees(bande_id):
        observation = f" - {row[5]}" if row[5] else ""
        events.append(
            _event(
                row[2],
                "Pesee",
                f"Poids moyen {_csv_number(row[3])} g sur {row[4]} sujets"
                f"{observation}",
                _csv_number(row[3]),
                "",
                f"pesee#{row[0]}",
                50,
            )
        )

    for row in db.get_ventes(bande_id):
        client = f" a {row[6]}" if row[6] else ""
        paiement = f" - {row[7]}" if row[7] else ""
        poids = f" - {_csv_number(row[8])} kg" if row[8] else ""
        events.append(
            _event(
                row[2],
                "Vente poulets",
                f"{row[3]} sujets vendus{client}",
                row[3],
                _csv_number(row[5]),
                f"vente#{row[0]}{paiement}{poids}",
                60,
            )
        )

    for row in db.get_pontes(bande_id):
        observation = f" - {row[4]}" if row[4] else ""
        events.append(
            _event(
                row[2],
                "Ponte",
                f"{row[3]} oeufs produits{observation}",
                row[3],
                "",
                f"ponte#{row[0]}",
                70,
            )
        )

    for row in db.get_ventes_oeufs(bande_id):
        client = f" a {row[6]}" if row[6] else ""
        events.append(
            _event(
                row[2],
                "Vente oeufs",
                f"{row[3]} oeufs vendus{client}",
                row[3],
                _csv_number(row[5]),
                f"oeufs#{row[0]}",
                80,
            )
        )

    for row in db.get_interventions_sanitaires(bande_id):
        dose = f", dose {row[5]}" if row[5] else ""
        intervenant = f", {row[6]}" if row[6] else ""
        echeance = f", prochaine echeance {row[7]}" if row[7] else ""
        events.append(
            _event(
                row[2],
                "Sanitaire",
                f"{row[3]} {row[4]}{dose}{intervenant}{echeance}",
                "",
                "",
                f"sanitaire#{row[0]}",
                90,
            )
        )

    return sorted(
        events,
        key=lambda row: (row["date"], row["_order"], str(row["reference"])),
    )


def build_fiche_lot_agasa(db, bande_id):
    bande = db.get_bande_info(bande_id)
    if not bande:
        raise ValueError("Lot introuvable.")
    kpis = _lot_metrics(db, bande)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "bande": _bande_dict(bande),
        "kpis": kpis,
        "chronologie": _chronologie(db, bande_id),
    }


def fiche_lot_agasa_csv_rows(fiche):
    rows = [["Date", "Type", "Detail", "Quantite", "Montant", "Reference"]]
    for event in fiche["chronologie"]:
        rows.append([
            event["date"],
            event["type"],
            event["detail"],
            str(event["quantite"] or ""),
            str(event["montant"] or ""),
            event["reference"],
        ])
    return rows


def fiche_lot_agasa_text(fiche):
    bande = fiche["bande"]
    kpis = fiche["kpis"]
    lines = [
        "AVICOLE PRO",
        "FICHE LOT AGASA",
        f"Edite le {datetime.now():%d/%m/%Y a %H:%M}",
        "=" * 58,
        "",
        "IDENTITE DU LOT",
        "-" * 58,
        f"Lot : {bande['nom']}",
        f"Activite : {bande['activite']}",
        f"Date debut : {bande['date_debut']}",
        f"Statut : {bande['statut']}",
        f"Effectif initial : {bande['effectif_initial']:,}",
        f"Effectif restant : {kpis['restants']:,}",
        f"Mortalites : {kpis['mortalites']:,}"
        f" ({_format_percent(kpis['taux_mortalite'])})",
        "",
        "INDICATEURS",
        "-" * 58,
        f"Recettes activite : {_format_money(kpis['recettes_activite'])}",
        f"Couts : {_format_money(kpis['couts'])}",
        f"Resultat : {_format_money(kpis['resultat'])}",
        f"Aliment : {kpis['aliment_kg']:,.1f} kg",
        f"IC : {kpis['ic']:.2f}",
        f"GMQ : {kpis['gmq']:.2f} g/j",
        f"Oeufs produits : {kpis['oeufs_produits']:,}",
        f"Stock oeufs : {kpis['stock_oeufs']:,}",
        "",
        "JOURNAL CHRONOLOGIQUE",
        "-" * 58,
    ]
    if not fiche["chronologie"]:
        lines.append("Aucune operation tracee.")
    for event in fiche["chronologie"]:
        amount = f" | {event['montant']} FCFA" if event["montant"] else ""
        quantity = f" | {event['quantite']}" if event["quantite"] else ""
        lines.append(
            f"{event['date']} | {event['type']} | {event['detail']}"
            f"{quantity}{amount}"
        )
    return "\n".join(lines)


def build_synthese_direction(db, date_reference=None):
    date_reference = date_reference or today_iso()
    lots = [_lot_metrics(db, bande) for bande in db.get_bandes()]
    lots = sorted(lots, key=lambda row: (row["activite"], row["nom"], row["id"]))
    rentabilite = {
        "chair": {"recettes": 0, "couts": 0, "benefice": 0, "nb_lots": 0},
        "ponte": {"recettes": 0, "couts": 0, "benefice": 0, "nb_lots": 0},
    }
    for lot in lots:
        activite = lot["activite"] if lot["activite"] in rentabilite else "chair"
        rentabilite[activite]["recettes"] += lot["recettes_activite"]
        rentabilite[activite]["couts"] += lot["couts"]
        rentabilite[activite]["benefice"] += lot["resultat"]
        rentabilite[activite]["nb_lots"] += 1

    alertes_stock = []
    for article in db.get_articles_sous_seuil():
        quantite = db.get_stock_quantite(article[0])
        alertes_stock.append({
            "id": article[0],
            "nom_article": article[1],
            "categorie": article[2],
            "unite": article[3],
            "seuil_alerte": article[4],
            "quantite": quantite,
        })

    echeances = []
    for row in db.get_interventions_a_venir(date_reference):
        bande = db.get_bande_info(row[1])
        bande_nom = bande[1] if bande else f"Lot #{row[1]}"
        echeances.append({
            "id": row[0],
            "bande_id": row[1],
            "bande_nom": bande_nom,
            "date": row[2],
            "type_intervention": row[3],
            "produit": row[4],
            "dose": row[5],
            "intervenant": row[6],
            "prochaine_echeance": row[7],
        })

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "date_reference": date_reference,
        "lots": lots,
        "rentabilite": rentabilite,
        "alertes_stock": alertes_stock,
        "echeances_sanitaires": echeances,
    }


def synthese_direction_csv_rows(synthese):
    rows = [[
        "Lot",
        "Activite",
        "Recettes",
        "Couts",
        "Resultat",
        "Mortalite %",
        "IC",
        "GMQ g/j",
        "Taux ponte %",
    ]]
    for lot in synthese["lots"]:
        rows.append([
            lot["nom"],
            lot["activite"],
            _csv_number(lot["recettes_activite"]),
            _csv_number(lot["couts"]),
            _csv_number(lot["resultat"]),
            _csv_number(lot["taux_mortalite"]),
            _csv_number(lot["ic"]),
            _csv_number(lot["gmq"]),
            _csv_number(lot["taux_ponte"]),
        ])
    return rows


def synthese_direction_text(synthese):
    rentabilite = synthese["rentabilite"]
    lines = [
        "AVICOLE PRO",
        "SYNTHESE DIRECTION",
        f"Date de reference : {synthese['date_reference']}",
        f"Edite le {datetime.now():%d/%m/%Y a %H:%M}",
        "=" * 58,
        "",
        "RENTABILITE PAR ACTIVITE",
        "-" * 58,
    ]
    for activite, libelle in (("chair", "Poulet de chair"), ("ponte", "Ponte")):
        bloc = rentabilite[activite]
        lines.extend([
            f"{libelle} - {bloc['nb_lots']} lot(s)",
            f"  Recettes : {_format_money(bloc['recettes'])}",
            f"  Couts    : {_format_money(bloc['couts'])}",
            f"  Resultat : {_format_money(bloc['benefice'])}",
        ])

    lines.extend(["", "LOTS", "-" * 58])
    if not synthese["lots"]:
        lines.append("Aucun lot enregistre.")
    for lot in synthese["lots"]:
        lines.append(
            f"{lot['nom']} ({lot['activite']}) - "
            f"Recettes {_format_money(lot['recettes_activite'])}, "
            f"Couts {_format_money(lot['couts'])}, "
            f"Resultat {_format_money(lot['resultat'])}, "
            f"Mortalite {_format_percent(lot['taux_mortalite'])}, "
            f"IC {lot['ic']:.2f}, GMQ {lot['gmq']:.2f} g/j, "
            f"Taux ponte {lot['taux_ponte']:.2f}%"
        )

    lines.extend(["", "ALERTES STOCK", "-" * 58])
    if not synthese["alertes_stock"]:
        lines.append("Aucune alerte stock.")
    for alerte in synthese["alertes_stock"]:
        lines.append(
            f"{alerte['nom_article']} ({alerte['categorie']}) : "
            f"{_csv_number(alerte['quantite'])} {alerte['unite']} "
            f"/ seuil {_csv_number(alerte['seuil_alerte'])}"
        )

    lines.extend(["", "ECHEANCES SANITAIRES", "-" * 58])
    if not synthese["echeances_sanitaires"]:
        lines.append("Aucune echeance sanitaire a venir.")
    for echeance in synthese["echeances_sanitaires"]:
        lines.append(
            f"{echeance['prochaine_echeance']} - "
            f"{echeance['type_intervention']} {echeance['produit']} "
            f"({echeance['bande_nom']})"
        )
    return "\n".join(lines)
