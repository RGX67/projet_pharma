# Analyse des dépenses pharmaceutiques en France (2016–2025)


> Projet data science — L3 Économie-Gestion · Université de Strasbourg  
> Données : **Open Medic / AMELI** (Assurance Maladie)

---

## Présentation du projet

Ce projet analyse l'évolution des **remboursements de médicaments en France** sur la période 2016–2025, à partir des données publiques de l'Assurance Maladie (Open Medic).

L'objectif est double :
- **Comprendre les dynamiques économiques** des dépenses pharmaceutiques (tendances, concentration, profils de classes thérapeutiques)
- **Appliquer des méthodes quantitatives** allant des statistiques descriptives jusqu'au machine learning

---

## Structure du projet

```
projet_pharma/
├── data/
│   ├── raw/                  → fichiers bruts Open Medic (AMELI)
│   └── clean/                → données nettoyées
├── notebooks/
│   ├── 02_analyse_classes_regions.ipynb → statistiques par classe ATC1, par région, croisement
│   ├── 04_regression_ols.ipynb          → OLS, Breusch-Pagan, erreurs robustes HC3
│   ├── 05_conclusions.ipynb             → interprétations économiques
│   ├── 06_machine_learning.ipynb        → Ridge, Lasso, comparaison des modèles
│   └── 07_clustering.ipynb              → K-Means, méthode du coude, profils ATC
├── outputs/                  → résultats exportés (CSV, graphiques)
├── requirements.txt
└── README.md
```

---

## Données

| Source | Description | Période |
|--------|-------------|---------|
| [Open Medic — AMELI](https://assurance-maladie.ameli.fr/etudes-et-donnees/open-medic-depenses-medicaments) | Remboursements par médicament, région, âge, sexe | 2016–2025 |

**Format** : fichiers CSV (séparateur `;`, encodage `latin-1`, décimales en virgule française)  
**Volume** : ~10 fichiers annuels, plusieurs millions de lignes au total

---

## Méthodes et outils

### Statistiques descriptives (notebook 02)
- Chargement agrégé dès la lecture (mémoire optimisée), harmonisation multi-années
- Analyse des classes thérapeutiques : remboursements, volume, coût par boîte
- Visualisations : barplots par classe ATC, scatter volume × coût, heatmap classe × région

### Économétrie (notebook 04–05)
- **Régression OLS** (`statsmodels`) : remboursement ~ année + volume + effets fixes ATC
- Diagnostic : test de **Breusch-Pagan** (hétéroscédasticité), erreurs robustes **HC3**
- Interprétation économique des coefficients : tendance temporelle, effet volume, primes ATC

### Machine Learning (notebook 06)
- **Ridge (L2)** et **Lasso (L1)** via `scikit-learn` avec validation croisée (`RidgeCV`, `LassoCV`)
- Sélection automatique de variables par Lasso
- Comparaison des performances : R², RMSE, nombre de variables actives

### Clustering (notebook 07)
- **K-Means** sur les classes ATC1 (remboursement moyen, volume, coût/boîte, taux de croissance)
- Choix du k optimal : méthode du coude + score de silhouette
- Identification de profils : *masse/bas coût*, *premium/spécialisé*, *croissance dynamique*, *déclin structurel*

---

## Principaux résultats

- Les remboursements pharmaceutiques ont progressé de manière **structurelle** sur 2016–2025, portés par le vieillissement et l'innovation coûteuse en oncologie
- Les **60 ans et plus** concentrent la majorité des dépenses, avec une part en hausse constante
- L'**oncologie** se distingue par un paradoxe : faible volume de boîtes, mais coût unitaire très élevé (thérapies ciblées, immunothérapies)
- Le modèle OLS confirme un **effet année significatif** : les dépenses augmentent même à volume constant, signe d'une inflation structurelle des prix
- Ridge et Lasso confirment la robustesse du modèle OLS ; Lasso identifie les classes ATC **vraiment discriminantes**
- Le clustering K-Means révèle des profils cohérents avec les grandes dynamiques du marché pharmaceutique français

---

## Stack technique

| Catégorie | Outils |
|-----------|--------|
| Langage | Python 3.14 |
| Environnement | VS Code + Jupyter Notebooks |
| Data wrangling | `pandas`, `numpy` |
| Visualisation | `matplotlib` |
| Économétrie | `statsmodels` |
| Machine Learning | `scikit-learn` |
| Versioning | Git / GitHub |

---

## Installation

```bash
git clone https://github.com/[RGX67]/projet_pharma.git
cd projet_pharma
pip install -r requirements.txt
```

Télécharger les fichiers Open Medic depuis [AMELI](https://assurance-maladie.ameli.fr/etudes-et-donnees/open-medic-depenses-medicaments) et les placer dans `data/raw/`.

Puis lancer les notebooks dans l'ordre (02 → 04 → 05 → 06 → 07) depuis VS Code ou Jupyter.

---

## Auteur

**Enes** — Étudiant en L3 Économie-Gestion, Université de Strasbourg  
Candidat au Master DS2E (Data Science pour l'Économie et l'Entreprise) — FSEG Strasbourg
