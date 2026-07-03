# streamlit run app.py
# Lancement : ouvrir un terminal dans le dossier projet_pharma/ et exécuter la commande ci-dessus

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import unicodedata
import re
import warnings
warnings.filterwarnings('ignore')

# --- Harmonisation des libellés ATC1 -----------------------------------------
# Open Medic change de format d'année en année (accents, casse, troncature 2016,
# corruption d'encodage 2025) : sans harmonisation, une même classe thérapeutique
# apparaît sous 2 à 4 orthographes différentes et fausse tout groupby('l_atc1').
ATC1_CANONIQUES = [
    'Anti-infectieux (usage systémique)',
    'Antinéoplasiques et agents immunomodulants',
    'Antiparasitaires, insecticides et répulsifs',
    'Dermatologie',
    'Divers',
    'Hormones systémiques, à l exclusion des hormones sexuelles et des insulines',
    'Organes sensoriels',
    'Sang et organes hématopoiétiques',
    'Système cardio-vasculaire',
    'Système digestif et métabolisme',
    'Système génito-urinaire et hormones sexuelles',
    'Système musculo-squelettique',
    'Système nerveux',
    'Système respiratoire',
]
ATC1_ALIAS = {'SANG ET ORGANES HEMATOPOIETQUES': 'Sang et organes hématopoiétiques'}  # coquille source 2022-2024

def _normaliser_atc1_cle(serie):
    s = serie.astype(str).str.strip().str.upper()
    s = s.apply(lambda x: unicodedata.normalize('NFKD', x))
    s = s.str.encode('ascii', 'ignore').str.decode('ascii')
    return s.str.replace(r'[^A-Z0-9\x1a]+', ' ', regex=True).str.strip()

_cle_vers_canonique = {_normaliser_atc1_cle(pd.Series([c])).iloc[0]: c for c in ATC1_CANONIQUES}
_cles_canoniques = list(_cle_vers_canonique.keys())

def _resoudre_atc1(cle_brute):
    if cle_brute in _cle_vers_canonique:
        return _cle_vers_canonique[cle_brute]
    if '\x1a' in cle_brute:
        motif = re.compile('^' + re.escape(cle_brute).replace(re.escape('\x1a'), '.') + '$')
        matches = [c for c in _cles_canoniques if motif.match(c)]
        if len(matches) == 1:
            return _cle_vers_canonique[matches[0]]
    matches = [c for c in _cles_canoniques if c.startswith(cle_brute)]
    return _cle_vers_canonique[matches[0]] if len(matches) == 1 else None

def harmoniser_atc1(serie):
    """Ramène les libellés l_atc1 bruts (jusqu'à 45 variantes observées) aux 14
    vraies classes ATC1, quelle que soit l'année source."""
    brut = serie.astype(str).str.strip().replace(ATC1_ALIAS)
    return _normaliser_atc1_cle(brut).map(_resoudre_atc1).fillna(brut)

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dépenses pharmaceutiques France",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / 'data'

def parse_euro(s):
    return (s.astype(str).str.strip()
             .str.replace('.', '', regex=False)
             .str.replace(',', '.', regex=False)
             .replace('', '0').astype(float))

@st.cache_data(show_spinner="Chargement des données…")
def load_data():
    raw_dir = DATA_DIR / 'raw'
    source  = Path('C:/Users/Enes/data')

    frames = []
    for annee in range(2016, 2026):
        for pat in [f'OPEN_MEDIC_{annee}.zip', f'OPEN_MEDIC_{annee}.csv']:
            for base in [raw_dir, source]:
                p = base / pat
                if p.exists():
                    df = pd.read_csv(p, sep=None, engine='python', encoding='latin-1')
                    df.columns = df.columns.str.lower().str.strip()
                    if 'l_atc1' not in df.columns:
                        df['l_atc1'] = ''
                    for col in ['rem', 'bse']:
                        if col in df.columns:
                            df[col] = parse_euro(df[col])
                    df['l_atc1'] = harmoniser_atc1(df['l_atc1'])
                    df['annee'] = annee
                    frames.append(df[['annee', 'l_atc1', 'rem', 'boites']])
                    break
            else:
                continue
            break

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df = df[df['l_atc1'].str.strip() != '']
    return df

df_raw = load_data()

if df_raw.empty:
    st.error("Aucune donnée trouvée. Vérifiez que les fichiers Open Medic sont dans data/raw/ ou C:/Users/Enes/data/")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — Filtres
# ---------------------------------------------------------------------------
st.sidebar.title("Filtres")
st.sidebar.markdown("---")

annees_dispo = sorted(df_raw['annee'].unique())
annee_min, annee_max = int(min(annees_dispo)), int(max(annees_dispo))

plage = st.sidebar.slider(
    "Plage d'années",
    min_value=annee_min,
    max_value=annee_max,
    value=(annee_min, annee_max)
)

classes_dispo = sorted(df_raw['l_atc1'].unique())
classes_sel = st.sidebar.multiselect(
    "Classes ATC1",
    options=classes_dispo,
    default=classes_dispo,
    placeholder="Toutes les classes"
)
if not classes_sel:
    classes_sel = classes_dispo

# Données filtrées
df = df_raw[
    (df_raw['annee'].between(plage[0], plage[1])) &
    (df_raw['l_atc1'].isin(classes_sel))
]

st.sidebar.markdown("---")
st.sidebar.metric("Lignes sélectionnées", f"{len(df):,}")
st.sidebar.metric("Classes ATC", len(classes_sel))
st.sidebar.metric("Années", f"{plage[0]} – {plage[1]}")

# ---------------------------------------------------------------------------
# Titre principal
# ---------------------------------------------------------------------------
st.title("💊 Analyse des dépenses pharmaceutiques en France 2016–2025")
st.markdown("Source : **Open Medic / AMELI** — Assurance Maladie")
st.markdown("---")

# ---------------------------------------------------------------------------
# Section 1 — Vue globale
# ---------------------------------------------------------------------------
st.header("1. Vue globale")

total_rem    = df['rem'].sum()
total_boites = df['boites'].sum()
n_classes    = df['l_atc1'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total remboursé",       f"{total_rem / 1e9:.2f} Md€")
col2.metric("Boîtes remboursées",    f"{total_boites / 1e6:.1f} M")
col3.metric("Classes thérapeutiques",str(n_classes))

st.markdown(" ")

# Courbe d'évolution annuelle
evo = df.groupby('annee').agg(rem=('rem', 'sum'), boites=('boites', 'sum')).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
fig.patch.set_facecolor('#0E1117')
for ax in axes:
    ax.set_facecolor('#0E1117')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444')
    ax.spines['bottom'].set_color('#444')
    ax.tick_params(colors='#CCC')
    ax.yaxis.label.set_color('#CCC')
    ax.xaxis.label.set_color('#CCC')
    ax.title.set_color('#FFF')

axes[0].fill_between(evo['annee'], evo['rem'] / 1e9, alpha=0.25, color='#4FC3F7')
axes[0].plot(evo['annee'], evo['rem'] / 1e9, marker='o', color='#4FC3F7', linewidth=2)
axes[0].set_title('Remboursements totaux (Md€)')
axes[0].set_xlabel('Année')
axes[0].set_xticks(evo['annee'])
axes[0].tick_params(axis='x', rotation=45)

axes[1].fill_between(evo['annee'], evo['boites'] / 1e6, alpha=0.25, color='#81C784')
axes[1].plot(evo['annee'], evo['boites'] / 1e6, marker='o', color='#81C784', linewidth=2)
axes[1].set_title('Boîtes remboursées (M)')
axes[1].set_xlabel('Année')
axes[1].set_xticks(evo['annee'])
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)
plt.close()

# ---------------------------------------------------------------------------
# Section 2 — Par classe thérapeutique
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("2. Par classe thérapeutique")

atc = (df.groupby('l_atc1')
         .agg(rem_total=('rem', 'sum'), boites_total=('boites', 'sum'))
         .sort_values('rem_total', ascending=False)
         .reset_index())
atc['cout_boite'] = (atc['rem_total'] / atc['boites_total']).round(2)
atc['part_pct']   = (atc['rem_total'] / atc['rem_total'].sum() * 100).round(1)

top10 = atc.head(10)

fig2, ax2 = plt.subplots(figsize=(12, 5))
fig2.patch.set_facecolor('#0E1117')
ax2.set_facecolor('#0E1117')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#444')
ax2.spines['bottom'].set_color('#444')
ax2.tick_params(colors='#CCC')
ax2.xaxis.label.set_color('#CCC')
ax2.title.set_color('#FFF')

colors = plt.cm.Blues_r(np.linspace(0.2, 0.8, len(top10)))
bars = ax2.barh(
    [l[:40] for l in top10['l_atc1'].iloc[::-1]],
    top10['rem_total'].iloc[::-1] / 1e9,
    color=colors[::-1]
)
ax2.set_xlabel('Remboursement total (Md€)', color='#CCC')
ax2.set_title(f'Top 10 classes ATC — Remboursements {plage[0]}–{plage[1]}', color='#FFF')
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}Md€'))

for bar, val in zip(bars, top10['rem_total'].iloc[::-1] / 1e9):
    ax2.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
             f'{val:.2f}Md€', va='center', fontsize=8, color='#CCC')

plt.tight_layout()
st.pyplot(fig2)
plt.close()

st.markdown("##### Tableau détaillé")
df_table = atc.rename(columns={
    'l_atc1':       'Classe ATC1',
    'rem_total':    'Remboursement (€)',
    'boites_total': 'Boîtes',
    'cout_boite':   'Coût / boîte (€)',
    'part_pct':     'Part (%)',
})
df_table['Remboursement (€)'] = df_table['Remboursement (€)'].map('{:,.0f}'.format)
df_table['Boîtes']            = df_table['Boîtes'].map('{:,.0f}'.format)
st.dataframe(df_table, use_container_width=True, height=350)

# ---------------------------------------------------------------------------
# Section 3 — Comparaison scatter
# ---------------------------------------------------------------------------
st.markdown("---")
st.header("3. Comparaison : volume vs remboursement")

st.markdown("Chaque point représente une **classe ATC1**. La taille des points est proportionnelle au coût moyen par boîte.")

fig3, ax3 = plt.subplots(figsize=(13, 7))
fig3.patch.set_facecolor('#0E1117')
ax3.set_facecolor('#0E1117')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_color('#444')
ax3.spines['bottom'].set_color('#444')
ax3.tick_params(colors='#CCC')
ax3.xaxis.label.set_color('#CCC')
ax3.yaxis.label.set_color('#CCC')
ax3.title.set_color('#FFF')

sizes = np.clip(atc['cout_boite'] / atc['cout_boite'].max() * 800, 40, 800)
scatter = ax3.scatter(
    atc['boites_total'] / 1e6,
    atc['rem_total']    / 1e6,
    s=sizes,
    c=atc['rem_total'],
    cmap='YlOrRd',
    alpha=0.85,
    edgecolors='white',
    linewidths=0.4
)

for _, row in atc.iterrows():
    ax3.annotate(
        row['l_atc1'][:25],
        (row['boites_total'] / 1e6, row['rem_total'] / 1e6),
        fontsize=7, color='#DDD',
        xytext=(5, 4), textcoords='offset points'
    )

cbar = plt.colorbar(scatter, ax=ax3)
cbar.set_label('Remboursement total (€)', color='#CCC')
cbar.ax.yaxis.set_tick_params(color='#CCC')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#CCC')

ax3.set_xlabel('Volume total (millions de boîtes)')
ax3.set_ylabel('Remboursement total (M€)')
ax3.set_title('Boîtes vs Remboursement — taille = coût moyen par boîte')
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}M'))
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}M€'))

plt.tight_layout()
st.pyplot(fig3)
plt.close()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("Données : Open Medic / AMELI — Assurance Maladie française | Dashboard réalisé avec Streamlit")
