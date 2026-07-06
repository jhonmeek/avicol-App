# Étude de cas — Avicole Pro au service d'une ferme gabonaise

*Document de démonstration — chiffres indicatifs basés sur les ordres de grandeur
du marché gabonais en 2026. Toutes les fonctionnalités et tous les libellés
d'écran cités existent dans l'application (schéma 10 : saisie quotidienne,
suppressions tracées, sorties d'effectif et ponte « 0 œuf » inclus). Les
chemins d'interface sont notés ainsi : **Menu → Onglet → Bouton**.*

---

## 0. Repères dans l'interface

La barre latérale donne accès à six pages (les libellés peuvent varier
légèrement selon le thème choisi dans **Affichage → Thème**) :

| Page | Ce qu'on y fait |
|---|---|
| **Tableau de bord** | Cartes d'indicateurs, boutons d'action rapide (dont **« Saisie du jour »**), panneau **« Alertes opérationnelles »** |
| **Bandes** (ou « Bandes d'élevage ») | Liste des lots, onglets « Toutes les bandes » / « Statistiques », boutons « Voir » / « Modifier » |
| **Transactions** | Dix onglets : **Mortalités, Sorties effectif, Dépenses, Ventes, Aliment, Pesées, Œufs, Stocks, Sanitaire, Journal** — chaque ligne a son bouton **« Supprimer »** ; filtres « Période » et « Bande » en haut |
| **Analytiques** (ou « Analyse décisionnelle ») | Graphiques financiers, coûts, mortalité, productivité |
| **Rapports** | Liste « Type de rapport » (financier, production, sanitaire, complet, **Synthèse direction**, **Fiche lot AGASA**, **Prévisionnel vs réel**, **Alertes opérationnelles**, **Calibrage œufs**), boutons **« Générer »**, **« Exporter »** et **« Prévisions du lot »** |
| **Paramètres** | Onglets « Apparence » et « Données » (**« Sauvegarder maintenant »**, **« Restaurer »**) |

La clôture d'un lot se fait par le menu **Fichier → « Clôturer la bande
active »**.

---

## 1. Le contexte

**La ferme.** « Avicole de la Remboué », exploitation familiale installée à
Ntoum, à une trentaine de kilomètres de Libreville. Elle est tenue par
M. Ondo, aidé d'un ouvrier permanent. Deux activités :

- **Poulet de chair** : des lots de 500 sujets, environ 6 cycles par an,
  vendus vifs au marché de Ntoum et à des revendeuses de PK8 et Mont-Bouët ;
- **Ponte** : un bâtiment de 200 pondeuses, œufs vendus à l'alvéole (30 œufs)
  aux boutiques du quartier.

**Le marché gabonais, en quelques repères** (ordres de grandeur utilisés dans
cette étude) :

| Poste | Valeur indicative |
|---|---|
| Poussin chair d'un jour | 650 FCFA |
| Sac d'aliment 50 kg (provenderie locale) | 20 000 FCFA |
| Poulet vif ~2 kg au marché | 3 250 – 3 500 FCFA |
| Alvéole de 30 œufs | 2 800 FCFA (~93 FCFA/œuf) |
| Vaccins d'un cycle chair (Gumboro, Newcastle) | ~65 000 FCFA / lot de 500 |

Contraintes locales bien connues : la concurrence du poulet congelé importé
(qui impose de maîtriser ses coûts pour rester compétitif sur le poulet
« chaud »), le climat équatorial (pics de chaleur = stress thermique et
mortalité), les ruptures d'approvisionnement en aliment, et la traçabilité
demandée par l'AGASA (Agence Gabonaise de Sécurité Alimentaire) pour
formaliser l'activité.

**Avant l'application.** M. Ondo tenait un cahier : dates de vaccination de
mémoire, dépenses mélangées avec celles du ménage, aucun moyen de savoir si un
lot avait été rentable autrement qu'« au feeling » une fois l'argent dépensé.
Deux problèmes concrets l'ont décidé : un lot entier fragilisé parce qu'un
rappel de vaccin Gumboro a été oublié, et un refus de crédit parce qu'il ne
pouvait présenter aucun historique chiffré à la microfinance.

---

## 2. Mise en place (une demi-journée)

Application installée sur le PC portable familial (Windows, aucune connexion
internet requise — la base SQLite est locale, dans `%LOCALAPPDATA%\AvicolePro`).

1. **Création des bandes** — *Tableau de bord → bouton « Nouvelle bande »* :
   « Chair Mars-2026 » (500 poussins, 650 FCFA l'unité, activité *chair*) et
   « Pondeuses Bât. A » (200 sujets, activité *ponte*, choisie dans le
   sélecteur d'activité du dialogue). L'application calcule d'office le coût
   initial du lot chair : **325 000 FCFA**.
2. **Articles de stock** — *Transactions → onglet « Stocks » → bouton
   « Nouvel article »*, avec seuils d'alerte : « Aliment démarrage » (seuil
   100 kg), « Aliment croissance » (seuil 200 kg), « Aliment ponte » (seuil
   200 kg), « Vaccin Newcastle » (seuil 250 doses), « Copeaux litière ». Les
   livraisons du fournisseur entrent par le bouton **« Entrée de stock »**.
3. **Prévisions du lot** — *Rapports → bouton « Prévisions du lot »* : coût
   poussins 325 000, aliment prévu 720 000, sanitaire 70 000, autres charges
   100 000 ; vente prévue de 475 sujets à 3 400 FCFA. Le prévisionnel affiche
   un bénéfice attendu d'environ **400 000 FCFA**. C'est la référence qui
   servira à juger le cycle — et à monter le dossier de crédit.

---

## 3. Un cycle chair raconté à travers l'application (45 jours)

### Semaine 1 — la routine du soir

Chaque soir, l'ouvrier ouvre *Tableau de bord → bouton **« Saisie du jour »*** :
un seul formulaire pour la bande, la date, les **morts du jour** (avec cause),
l'**aliment distribué** et les **œufs ramassés** — 2 à 3 minutes. Si la
journée a déjà été saisie pour cette bande, un avertissement s'affiche dans le
dialogue : fini les doublons du cahier.

Quand l'aliment sort du magasin, la saisie passe par *Tableau de bord →
« Saisir aliment »* en choisissant l'article dans le champ **« Source
stock »** : une seule saisie décrémente le stock **et** crédite la
consommation du lot (le champ propose aussi « Ne pas déduire du stock » pour
un sac acheté au jour le jour). Magasin et suivi technique restent alignés
sans double travail.

En cas d'erreur de frappe (25 morts au lieu de 5), direction *Transactions →
onglet « Mortalités »* : chaque ligne a un bouton **« Supprimer »** avec
confirmation, l'opération étant tracée dans l'onglet **« Journal »**. On
supprime, on ressaisit, l'historique garde les deux traces.

À J7, première **pesée** — *Tableau de bord → « Nouvelle pesée »* : 170 g de
moyenne sur 20 sujets pesés.

L'intervention « Vaccin Gumboro » est saisie dans *Transactions → onglet
« Sanitaire » → bouton « Ajouter une intervention »*, avec une **prochaine
échéance à J14**. C'est le point qui avait coûté un lot entier l'année
précédente : cette fois, 7 jours avant l'échéance, le panneau **« Alertes
opérationnelles »** du tableau de bord affiche *« Échéance sanitaire —
Gumboro dans 5 jour(s) »*, et l'alerte passe en **critique** si la date est
dépassée.

### Semaine 3 — le coup de chaleur

Trois jours de forte chaleur. Les déclarations s'accumulent via « Saisie du
jour » : 9, 8, puis 6 sujets, cause « Stress thermique » (proposée dans la
liste des causes). Le cumul atteint 28 morts sur 500, soit **5,6 %** : le
seuil d'alerte (5 %) est franchi et le panneau des alertes affiche
*« Mortalité élevée — Chair Mars-2026 : 5,6 % de mortalité (28 sujets) »*.

C'est la différence avec le cahier : l'alerte apparaît **pendant** le
problème, pas au moment du bilan. M. Ondo réagit (abreuvoirs supplémentaires,
ouverture des bâches la nuit, vitamine C — dépense de 12 000 FCFA saisie via
*« Enregistrer une dépense »*). La mortalité retombe à 1–2 sujets par
semaine. Le lot finira à 28 morts : sans réaction rapide, un épisode de ce
type dépasse facilement 10 % au Gabon en saison chaude.

### Semaine 5 — la sortie qui n'est ni une mort ni une vente

Pour la fête du village, la famille prélève 2 coquelets. Plutôt que de
fausser la mortalité ou d'oublier l'écart, l'ouvrier utilise *Tableau de
bord → bouton **« Sortie effectif »*** (motif « Don » ; la liste propose
aussi Réforme, Transfert, Vol, Ajustement, Autre). L'effectif disponible
passe à 470
sans polluer ni le taux de mortalité ni les statistiques de vente — et la
ligne reste visible dans *Transactions → onglet « Sorties effectif »*.

### Semaines 4–6 — pilotage par les cartes du tableau de bord

Les pesées hebdomadaires alimentent deux cartes du tableau de bord :

- **« GMQ »** : à J45, poids moyen 2 100 g, soit ~51 g/j depuis la première
  pesée — croissance conforme ;
- **« Indice de consommation »** : recalculé en continu à partir de l'aliment
  cumulé et du poids vif produit. S'il dépasse 2,2, l'alerte *« Indice de
  consommation élevé »* se déclenche — au prix du sac à 20 000 FCFA, un IC
  qui dérape de 0,3 point sur un lot de 500 représente près de 60 000 FCFA
  d'aliment gaspillé (litière humide, gaspillage aux mangeoires, aliment de
  mauvaise qualité…).

Mi-cycle, l'alerte *« Stock sous seuil — Aliment croissance : 180 kg en stock
pour un seuil de 200 »* déclenche la commande chez le fournisseur **avant**
la rupture. Une rupture d'aliment de 48 h en fin de cycle chair, c'est du
poids perdu qui ne se rattrape pas.

### La vente (J42–J47)

Deux ventes saisies via *Tableau de bord → « Enregistrer une vente »* :
400 sujets à 3 500 FCFA aux revendeuses (1 400 000 FCFA) puis 70 sujets à
3 250 FCFA (227 500 FCFA), avec le poids total vendu (~985 kg) pour que l'IC
de fin de cycle reste juste une fois le lot vidé.

Garde-fou apprécié : le jour où l'ouvrier a voulu saisir 80 sujets alors
qu'il n'en restait que 70, l'application a **refusé la vente** — l'écart
venait d'une mortalité non déclarée la veille, corrigée aussitôt. La carte
**« Poulets disponibles »** et le poulailler réel restent alignés.

### Clôture et bilan du lot

Menu **Fichier → « Clôturer la bande active »**. Les cartes du tableau de
bord figent le bilan :

| Carte du tableau de bord | Valeur |
|---|---|
| Recettes cumulées | 1 627 500 FCFA |
| Dépenses cumulées + coût poussins | 1 190 000 FCFA |
| **Résultat net** | **437 500 FCFA** |
| Retour sur investissement | ~37 % |
| Taux de mortalité | 5,6 % |
| Indice de consommation | 1,78 |
| GMQ | ~51 g/j |

Le rapport **« Prévisionnel vs réel »** (*Rapports → Type de rapport*)
compare au plan de départ : bénéfice réalisé 437 500 contre 400 000 prévus,
surcoût aliment de ~20 000 identifié (les sacs ont pris 500 FCFA en cours de
cycle — information notée pour négocier le prochain approvisionnement en
gros).

---

## 4. Le quotidien côté pondeuses

Chaque soir, la ponte passe par **« Saisie du jour »** (155–160 œufs), ou par
*Transactions → onglet « Œufs » → bouton « Ajouter une ponte »*. Le bandeau
de l'onglet Œufs affiche le stock d'œufs et le taux de ponte du lot
(environ 78 %). Au fil de la semaine :

- **Jour de vaccination** : les poules stressées ne pondent presque pas.
  L'ouvrier saisit **0 œuf** avec l'observation « vaccination » — la journée
  est documentée (ce n'est pas un oubli de saisie) et le taux de ponte reste
  calculé sur le bon nombre de jours ;
- **Calibrage** — *onglet « Œufs » → bouton « Calibrer »* : petit / moyen /
  gros / très gros / déclassé. Les gros partent aux boutiques, les déclassés
  sont vendus à prix réduit au quartier ; l'application refuse de calibrer
  plus d'œufs que la production, donc pas de « stocks fantômes » ;
- **Ventes à l'alvéole** — *onglet « Œufs » → bouton « Vendre des œufs »*
  (2 800 FCFA les 30, nom du client enregistré) : la garde de stock empêche
  de promettre plus d'œufs qu'il n'y en a réellement ;
- Le rapport de **rentabilité par activité** montre chair et ponte
  séparément : M. Ondo découvre que la ponte, moins spectaculaire, dégage un
  revenu mensuel régulier (~360 000 FCFA de ventes d'œufs par mois) qui paie
  les charges fixes entre deux cycles chair. Décision prise : passer à 300
  pondeuses au prochain renouvellement.

Et quand M. Ondo s'absente à Libreville, l'alerte *« Saisie quotidienne
manquante »* signale tout lot sans saisie depuis 2 jours (critique au-delà
de 6) : il voit immédiatement au retour si l'ouvrier a tenu le rythme — et
donc si les indicateurs de la semaine sont fiables.

---

## 5. Formalisation : AGASA et microfinance

Tout se passe dans la page **Rapports** : choisir le type dans la liste
« Type de rapport », le format (« Texte » ou « CSV »), puis **« Générer »**
pour l'aperçu et **« Exporter »** pour le fichier :

- **« Fiche lot AGASA »** : identité du lot, effectifs, mortalités,
  indicateurs (IC, GMQ, recettes/coûts/résultat) et **journal chronologique
  complet** de toutes les opérations — exactement le type de traçabilité
  attendu pour formaliser un élevage auprès de l'agence ;
- **« Synthèse direction »** et **« Prévisionnel vs réel »** : présentés à la
  microfinance avec deux cycles d'historique, ils remplacent le cahier
  illisible. Le dossier de crédit pour le bâtiment de 300 pondeuses s'appuie
  sur des marges démontrées, pas déclarées.

L'onglet *Transactions → « Journal »* horodate chaque action (création,
saisie, suppression — qui a enregistré quoi, quand) : quand un chiffre
étonne, on retrouve son origine. Et *Paramètres → onglet « Données » →
**« Sauvegarder maintenant »*** copie la base sur clé USB — réflexe pris
après chaque clôture de lot ; **« Restaurer »** la ramène en cas de panne
du PC.

---

## 6. Ce que l'application a changé, en résumé

| Problème du terrain (Gabon) | Réponse de l'application (où ?) | Effet mesurable |
|---|---|---|
| Rappel de vaccin oublié → lot perdu | Échéances sanitaires (onglet Sanitaire) + alerte à J-7 | Zéro rappel manqué sur le cycle |
| Mortalité découverte trop tard en saison chaude | Alerte « Mortalité élevée » > 5 % en temps réel (tableau de bord) | Épisode contenu à 5,6 % au lieu de >10 % |
| Rupture d'aliment en fin de cycle | Seuils par article + alerte « Stock sous seuil » (onglet Stocks) | Commande déclenchée avant rupture |
| Aliment gaspillé invisible dans un cahier | Carte « Indice de consommation », alerte > 2,2 | ~60 000 FCFA de dérive détectables par lot |
| Écarts entre poulailler réel et « papier » | Gardes : vente/sortie > disponible refusée ; « Sortie effectif » pour don, réforme, transfert, vol | Effectif théorique = effectif réel |
| « Le lot a-t-il rapporté ? » au feeling | Cartes Résultat net / ROI + rapport « Prévisionnel vs réel » | Décisions chiffrées (passage à 300 pondeuses) |
| Erreur de frappe qui fausse tout le bilan | Bouton « Supprimer » tracé au Journal, gardes d'intégrité | Correction en un clic, historique conservé |
| Saisies oubliées quand le patron s'absente | Alerte « Saisie quotidienne manquante » + « Saisie du jour » groupée | Régularité contrôlée, indicateurs fiables |
| Jour sans ponte confondu avec un oubli | Saisie explicite « 0 œuf » avec observation | Taux de ponte calculé sur les vrais jours |
| Pas de dossier pour l'AGASA ni la banque | Rapports « Fiche lot AGASA » + « Synthèse direction » exportables | Formalisation et accès au crédit |

**Le point clé** : tout repose sur une saisie quotidienne de 2 à 3 minutes,
sans internet, dans le vocabulaire du métier (bandes, pontes, alvéoles via
quantités, FCFA). La complexité — transactions, gardes d'intégrité, calculs
zootechniques — est dans la base de données, pas dans les mains de
l'utilisateur.

---

## 7. Précautions de lecture

- Les prix (poussin, sac, poulet vif, alvéole) sont des **ordres de
  grandeur** susceptibles de varier selon la saison, la zone (Libreville /
  intérieur) et le fournisseur ; l'application enregistre les prix réels
  saisis, l'étude ne fait que les illustrer.
- Le scénario suppose la discipline de saisie quotidienne — friction réduite
  par « Saisie du jour » (une saisie groupée par soir) et surveillée par
  l'alerte de saisie manquante ; les erreurs restent corrigeables par
  suppression tracée.
- Les libellés d'écran cités correspondent au thème par défaut ; le menu
  **Affichage → Thème** peut légèrement modifier l'intitulé de deux pages
  (« Bandes / Bandes d'élevage », « Analytiques / Analyse décisionnelle »).
