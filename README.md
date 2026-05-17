# Analyse des dépenses pharmaceutiques en France (2016–2025)

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![Statut](https://img.shields.io/badge/Statut-En%20cours-yellow)

> Projet réalisé dans le cadre d'une candidature au **Master DS2E** (Data Science pour l'Économie et l'Entreprise).

---

## Problématique

Les dépenses pharmaceutiques remboursées par l'Assurance Maladie représentent
un enjeu budgétaire et de santé publique majeur en France.
Ce projet cherche à répondre à trois questions :

1. **Quelles sont les tendances** des remboursements sur la période 2016–2025 ?
2. **Quels facteurs** (année, volume, classe thérapeutique) expliquent statistiquement le montant remboursé ?
3. **Peut-on segmenter** les classes thérapeutiques selon leur profil de dépenses pour orienter les décisions ?

---

## Données

| Paramètre | Détail |
|-----------|--------|
| **Source officielle** | [Open Medic — Assurance Maladie / AMELI](https://www.ameli.fr/l-assurance-maladie/statistiques-et-publications/donnees-statistiques/medicament/open-medic-bases-completes.php) |
| **Période** | 2016 – 2025 (10 années) |
| **Format** | CSV / ZIP, encodage Latin-1 |
| **Volume** | ~1,8 million de lignes par année (~18 millions au total) |
| **Granularité** | Médicament (CIP13) × Classe ATC × Région × Âge × Sexe |

### Variables principales

| Variable | Description |
|----------|-------------|
| `ATC1` → `ATC5` | Classification anatomique, thérapeutique et chimique (5 niveaux) |
| `l_cip13` | Nom commercial du médicament |
| `BOITES` | Nombre de boîtes remboursées |
| `REM` | Montant total remboursé (€) |
| `age` | Tranche d'âge du patient (< 20 / 20–59 / 60+ ans) |
| `sexe` | Sexe du patient (1 = Homme / 2 = Femme) |
| `BEN_REG` | Code région INSEE du bénéficiaire |

---

## Méthodologie

### Partie 1 — Analyse descriptive
Exploration des tendances temporelles, des classes thérapeutiques les plus coûteuses,
des disparités régionales et des profils démographiques.

### Partie 2 — Modélisation OLS
Régression linéaire multiple pour quantifier l'effet marginal de l'année, du volume
de boîtes et des classes ATC sur les remboursements.
Diagnostics statistiques : résidus, QQ-plot, test de Breusch-Pagan, erreurs robustes HC3.

### Partie 3 — Machine Learning
- **Régression régularisée** (Ridge / Lasso) : comparaison des performances et sélection de variables
- **Clustering K-Means** : segmentation des classes thérapeutiques par profil de dépenses,
  avec méthode du coude et score de silhouette

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| `01_import_nettoyage.ipynb` | Chargement, détection d'encodage, nettoyage des types, export CSV propre |
| `02_analyse_descriptive.ipynb` | Statistiques descriptives par classe ATC et par région |
| `03_visualisations.ipynb` | Graphiques d'évolution, heatmaps, comparaisons inter-régionales |
| `04_regression_ols.ipynb` | Régression OLS simple et multiple, diagnostics, erreurs robustes |
| `05_conclusions.ipynb` | Rapport de synthèse avec interprétation économique complète |
| `06_machine_learning.ipynb` | Ridge CV, Lasso CV, comparaison OLS vs régularisé, export résultats |
| `07_clustering.ipynb` | K-Means, méthode du coude, profils des clusters, export CSV |

**Ordre d'exécution recommandé :** `01` → `02` → `03` → `04` → `05` → `06` → `07`

---

## Dashboard interactif

Un dashboard **Streamlit** permet d'explorer les données de manière interactive,
avec des filtres par plage d'années et par classe thérapeutique.

### Lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer le dashboard
python -m streamlit run app.py
```

Le dashboard s'ouvre automatiquement sur **http://localhost:8501**

### Fonctionnalités

| Section | Contenu |
|---------|---------|
| **Sidebar** | Slider années, multiselect classes ATC, métriques en temps réel |
| **Vue globale** | Total remboursé, courbes d'évolution remboursements et volume |
| **Par classe** | Barplot top 10 + tableau interactif avec coût par boîte |
| **Comparaison** | Scatter plot volume vs remboursement, taille = coût unitaire |

---

## Structure du projet

```
projet_pharma/
│
├── data/
│   ├── raw/                        ← Fichiers Open Medic bruts (non versionnés)
│   └── clean/                      ← Données nettoyées et tables de synthèse
│
├── notebooks/
│   ├── 01_import_nettoyage.ipynb
│   ├── 02_analyse_descriptive.ipynb
│   ├── 03_visualisations.ipynb
│   ├── 04_regression_ols.ipynb
│   ├── 05_conclusions.ipynb
│   ├── 06_machine_learning.ipynb
│   └── 07_clustering.ipynb
│
├── outputs/
│   ├── resultats_ols.csv
│   ├── metriques_ols.csv
│   ├── comparaison_modeles.csv
│   ├── comparaison_coefficients.csv
│   └── clustering_atc1.csv
│
├── app.py                          ← Dashboard Streamlit
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Librairies utilisées

| Librairie | Usage |
|-----------|-------|
| `pandas` | Manipulation et agrégation des données |
| `numpy` | Calculs numériques et transformations |
| `matplotlib` | Visualisations statiques |
| `scipy` | Tests statistiques, QQ-plot |
| `statsmodels` | Régression OLS, diagnostics, erreurs robustes |
| `scikit-learn` | Ridge, Lasso, K-Means, StandardScaler, métriques |
| `streamlit` | Dashboard interactif |

---

## Installation

```bash
git clone https://github.com/<votre-username>/projet_pharma.git
cd projet_pharma
pip install -r requirements.txt
```

> Les fichiers de données brutes ne sont pas versionnés (voir `.gitignore`).
> Téléchargez les fichiers Open Medic sur [ameli.fr](https://www.ameli.fr/l-assurance-maladie/statistiques-et-publications/donnees-statistiques/medicament/open-medic-bases-completes.php)
> et placez-les dans `data/raw/`.

---

*Projet réalisé dans le cadre d'une candidature au **Master DS2E** — Data Science pour l'Économie et l'Entreprise.*  
*Données : Open Medic / AMELI — Assurance Maladie française*
