# Avicole Pro

Application Windows de gestion et de pilotage avicole construite avec Python,
PyQt6, SQLite et Matplotlib.

## Fonctionnalités

- gestion des bandes d'élevage ;
- saisie journalière groupée (mortalité, aliment, oeufs, y compris 0 oeuf)
  en un seul écran ;
- suivi des mortalités, dépenses et ventes, avec suppression tracée des
  erreurs de saisie ;
- sorties d'effectif hors mortalité/vente (réforme, don, transfert,
  ajustement) ;
- consommation d'aliment directe ou déduite du stock depuis le même flux ;
- alertes opérationnelles : mortalité, indice de consommation, stock sous
  seuil, échéances sanitaires, saisie quotidienne manquante ;
- tableau de bord et indicateurs de performance ;
- graphiques analytiques et rapports ;
- exports CSV, sauvegarde et restauration de la base ;
- interface responsive avec thèmes institutionnel et fermier.

## Lancer en développement

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Les données sont enregistrées dans :

```text
%LOCALAPPDATA%\AvicolePro
```

## Construire pour Windows

Le script suivant génère l'exécutable PyInstaller puis l'installateur Inno
Setup :

```powershell
.\build_windows.ps1
```

Artefacts générés :

- `dist\AvicolePro\AvicolePro.exe` pour la version portable ;
- `installer\AvicolePro-Setup-3.1.0.exe` pour l'installation Windows.

Les dossiers `dist`, `build` et `installer` sont volontairement exclus de Git.
