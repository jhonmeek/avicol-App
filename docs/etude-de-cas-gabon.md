# Étude de cas — Avicole Pro au service d'une ferme gabonaise

*Document de démonstration — chiffres indicatifs basés sur les ordres de grandeur
du marché gabonais en 2026. Toutes les fonctionnalités citées existent dans
l'application (schéma 9, Phase 2 « saisie quotidienne » incluse).*

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

1. **Création des bandes** : « Chair Mars-2026 » (500 poussins, 650 FCFA
   l'unité, activité *chair*) et « Pondeuses Bât. A » (200 sujets, activité
   *ponte*). L'application calcule d'office le coût initial du lot chair :
   **325 000 FCFA**.
2. **Articles de stock** avec seuils d'alerte : « Aliment démarrage » (seuil
   100 kg), « Aliment croissance » (seuil 200 kg), « Aliment ponte » (seuil
   200 kg), « Vaccin Newcastle » (seuil 250 doses), « Copeaux litière ».
3. **Prévisions du lot** chair (module Prévisions) : coût poussins 325 000,
   aliment prévu 720 000, sanitaire 70 000, autres charges 100 000 ; vente
   prévue de 475 sujets à 3 400 FCFA. Le prévisionnel affiche un bénéfice
   attendu d'environ **400 000 FCFA**. C'est la référence qui servira à juger
   le cycle — et à monter le dossier de crédit.

---

## 3. Un cycle chair raconté à travers l'application (45 jours)

### Semaine 1 — démarrage

Chaque soir, l'ouvrier enregistre la journée : morts éventuels (avec cause),
aliment distribué. La sortie d'aliment se fait depuis le module **Stocks** :
une seule saisie décrémente le stock **et** alimente le suivi de consommation
du lot — pas de double travail, pas d'écart entre le magasin et le suivi
technique. Pour le reste du quotidien, le bouton **« Saisie du jour »** du
tableau de bord regroupe morts + aliment + œufs en un seul formulaire (2 à
3 minutes chaque soir), avec un avertissement si la journée a déjà été saisie
— fini les doublons du cahier. Et en cas d'erreur de frappe (25 morts au lieu
de 5), la ligne se **supprime** d'un clic, l'opération restant tracée dans le
journal.

À J7, première **pesée** : 170 g de moyenne sur 20 sujets pesés.

L'intervention « Vaccin Gumboro » est saisie avec une **prochaine échéance à
J14**. C'est le point qui avait coûté un lot entier l'année précédente : cette
fois, 7 jours avant l'échéance, le tableau de bord affiche une alerte
*« Échéance sanitaire — Gumboro dans 5 jour(s) »*, qui passe en **critique**
si la date est dépassée.

### Semaine 3 — le coup de chaleur

Trois jours de forte chaleur. Les déclarations de mortalité s'accumulent :
9, 8, puis 6 sujets, cause « stress thermique ». Le cumul atteint 28 morts sur
500, soit **5,6 %** : le seuil d'alerte (5 %) est franchi et le tableau de
bord affiche *« Mortalité élevée — Chair Mars-2026 : 5,6 % (28 sujets) »*.

C'est la différence avec le cahier : l'alerte apparaît **pendant** le
problème, pas au moment du bilan. M. Ondo réagit (abreuvoirs supplémentaires,
ouverture des bâches la nuit, vitamine C — dépense de 12 000 FCFA saisie dans
la foulée). La mortalité retombe à 1–2 sujets par semaine. Le lot finira à
28 morts : sans réaction rapide, un épisode de ce type dépasse facilement
10 % au Gabon en saison chaude.

### Semaines 4–6 — pilotage par les indicateurs

Les pesées hebdomadaires alimentent deux indicateurs du tableau de bord :

- **GMQ** (gain moyen quotidien) : à J45, poids moyen 2 100 g, soit ~51 g/j
  depuis la première pesée — croissance conforme ;
- **IC** (indice de consommation) : l'application le recalcule en continu à
  partir de l'aliment cumulé et du poids vif produit. S'il dépasse 2,2, une
  alerte se déclenche — au prix du sac à 20 000 FCFA, un IC qui dérape de
  0,3 point sur un lot de 500 représente près de 60 000 FCFA d'aliment
  gaspillé (litière humide, gaspillage aux mangeoires, aliment de mauvaise
  qualité…).

Mi-cycle, l'alerte *« Stock sous seuil — Aliment croissance : 180 kg pour un
seuil de 200 »* déclenche la commande chez le fournisseur **avant** la
rupture. Une rupture d'aliment de 48 h en fin de cycle chair, c'est du poids
perdu qui ne se rattrape pas.

### La vente (J42–J47)

Deux ventes saisies : 400 sujets à 3 500 FCFA aux revendeuses (1 400 000 FCFA)
puis 72 sujets à 3 250 FCFA (234 000 FCFA), avec le poids total vendu
(~990 kg) pour que l'IC de fin de cycle reste juste une fois le lot vidé.

Garde-fou apprécié : le jour où l'ouvrier a voulu saisir 80 sujets alors qu'il
n'en restait que 72, l'application a **refusé la vente** — l'écart venait
d'une mortalité non déclarée la veille, corrigée aussitôt. Le stock théorique
et le poulailler réel restent alignés.

### Clôture et bilan du lot

Le lot est clôturé. Le tableau de bord fige le bilan :

| Indicateur | Valeur |
|---|---|
| Recettes | 1 634 000 FCFA |
| Coûts totaux (poussins + dépenses) | 1 190 000 FCFA |
| **Bénéfice net** | **444 000 FCFA** |
| ROI | 37 % |
| Taux de mortalité | 5,6 % |
| IC | 1,77 |
| GMQ | ~51 g/j |

Le module **Prévisionnel vs réel** compare au plan de départ : bénéfice réalisé
444 000 contre 400 000 prévus, surcoût aliment de ~20 000 identifié (les sacs
ont pris 500 FCFA en cours de cycle — information notée pour négocier le
prochain approvisionnement en gros).

---

## 4. Le quotidien côté pondeuses

Chaque soir : **saisie de la ponte** (155–160 œufs par jour, soit un taux de
ponte d'environ 78 % affiché automatiquement), puis au fil de la semaine :

- **Calibrage** en petit / moyen / gros — les gros partent aux boutiques, les
  déclassés sont vendus à prix réduit au quartier ; l'application refuse de
  calibrer plus d'œufs que la production, donc pas de « stocks fantômes » ;
- **Ventes à l'alvéole** (2 800 FCFA les 30) avec nom du client — la garde de
  stock empêche de promettre plus d'œufs qu'il n'y en a réellement ;
- Le tableau **rentabilité par activité** montre chair et ponte séparément :
  M. Ondo découvre que la ponte, moins spectaculaire, dégage un revenu
  mensuel régulier (~360 000 FCFA de ventes d'œufs par mois) qui paie les
  charges fixes entre deux cycles chair. Décision prise : passer à 300
  pondeuses au prochain renouvellement.

Et quand M. Ondo s'absente à Libreville, l'alerte **« saisie quotidienne
manquante »** signale tout lot sans saisie depuis 2 jours (critique au-delà
de 6) : il voit immédiatement au retour si l'ouvrier a tenu le rythme —
et donc si les indicateurs de la semaine sont fiables.

---

## 5. Formalisation : AGASA et microfinance

Deux documents sortent de l'application en un clic :

- **La fiche lot AGASA** : identité du lot, effectifs, mortalités, indicateurs
  (IC, GMQ, recettes/coûts/résultat) et **journal chronologique complet** de
  toutes les opérations — exactement le type de traçabilité attendu pour
  formaliser un élevage auprès de l'agence. Export texte ou CSV.
- **La synthèse direction + le prévisionnel vs réel** : présentés à la
  microfinance avec deux cycles d'historique, ils remplacent le cahier
  illisible. Le dossier de crédit pour le bâtiment de 300 pondeuses s'appuie
  sur des marges démontrées, pas déclarées.

Le **journal des actions** horodate chaque saisie (qui a enregistré quoi,
quand) : quand un chiffre étonne, on retrouve son origine. Et la
**sauvegarde** régulière de la base sur clé USB protège deux ans de données
contre une panne du PC — réflexe pris après chaque clôture de lot.

---

## 6. Ce que l'application a changé, en résumé

| Problème du terrain (Gabon) | Réponse de l'application | Effet mesurable |
|---|---|---|
| Rappel de vaccin oublié → lot perdu | Échéances sanitaires + alerte à J-7 | Zéro rappel manqué sur le cycle |
| Mortalité découverte trop tard en saison chaude | Alerte mortalité > 5 % en temps réel | Épisode contenu à 5,6 % au lieu de >10 % |
| Rupture d'aliment en fin de cycle | Seuils de stock + alerte sous seuil | Commande déclenchée avant rupture |
| Aliment gaspillé invisible dans un cahier | IC calculé en continu, alerte > 2,2 | ~60 000 FCFA de dérive détectables par lot |
| Écarts entre poulailler réel et « papier » | Gardes : vente/sortie > disponible refusée | Stock théorique = stock réel |
| « Le lot a-t-il rapporté ? » au feeling | Bénéfice, ROI, marge par lot + prévisionnel vs réel | Décisions chiffrées (passage à 300 pondeuses) |
| Erreur de frappe qui fausse tout le bilan | Suppression tracée au journal, gardes d'intégrité | Correction en un clic, historique conservé |
| Saisies oubliées quand le patron s'absente | Alerte « saisie manquante » après 2 jours + saisie groupée du soir | Régularité contrôlée, indicateurs fiables |
| Pas de dossier pour l'AGASA ni la banque | Fiche lot AGASA + synthèse direction exportables | Formalisation et accès au crédit |

**Le point clé pour une V1** : tout repose sur une saisie quotidienne de
2 à 3 minutes, sans internet, dans le vocabulaire du métier (bandes, pontes,
alvéoles via quantités, FCFA). La complexité — transactions, gardes
d'intégrité, calculs zootechniques — est dans la base de données, pas dans les
mains de l'utilisateur.

---

## 7. Précautions de lecture

- Les prix (poussin, sac, poulet vif, alvéole) sont des **ordres de grandeur**
  susceptibles de varier selon la saison, la zone (Libreville / intérieur) et
  le fournisseur ; l'application enregistre les prix réels saisis, l'étude ne
  fait que les illustrer.
- Le scénario suppose la discipline de saisie quotidienne — friction réduite
  par l'écran « Saisie du jour » (une saisie groupée par soir) et surveillée
  par l'alerte de saisie manquante ; les erreurs restent corrigeables par
  suppression tracée.
