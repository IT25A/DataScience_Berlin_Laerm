"""
DATA SCIENCE: Lärm, soziale Lage und Angebotsmieten in Berlin
=============================================================

Leitfrage:
Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von
Lärm betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

Räumliche Einheit: 542 LOR-Planungsräume (PLR), Gebietsstand 2021 / MSS 01/2023.
Alle Analysen beschreiben Zusammenhänge auf Gebietsebene. Korrelation ist keine
Kausalität (ökologischer Fehlschluss beachten).

Ablauf:
1. Daten laden und über die PLR-ID verknüpfen
2. PCA über die vier MSS-Status-Indikatoren -> Benachteiligungsindex (PC1)
3. Deskriptive Statistik, Korrelationen, Gruppenvergleiche
4. OLS-Regressionen (HC3 und nach Prognoseraum geclusterte Standardfehler)
5. K-Means-Clustering (Lärm, Benachteiligung, Miete)
6. Moran's I (Variablen und Regressionsresiduen)
7. Karten und Ergebnisgrafik zur Leitfrage

Quellen:
MSS 2023 Index-Tabellen (Tabelle 1, 2.1 und 3; Datenstand 31.12.2022):
https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2023/tabellen-der-index-indikatoren/
Lärmkarten Berlin 2022 (WFS ua_stratlaerm_2022, Fassadenpegel), siehe aggregate_noise.py:
https://www.berlin.de/umweltatlas/verkehr-laerm/laermbelastung/2022/download/
IBB Wohnungsmarktbericht 2025 (Angebotsmieten nach Planungsräumen):
https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html
LOR-Geodaten / Planungsräume:
https://daten.odis-berlin.de/
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

try:
    from libpysal.weights import Queen
    from esda.moran import Moran
    HAS_PYSAL = True
except ImportError:
    HAS_PYSAL = False


# ---------------------------------------------------------------------------
# 1. PROJEKT-KONFIGURATION – HIER DATEINAMEN UND SPALTEN ANPASSEN
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "outputs"

# Geodaten der Berliner LOR-Planungsräume (GeoJSON mit Geometrie)
BOUNDARIES_FILE = RAW / "planungsraeume.geojson"  # GeoJSON von ODIS Berlin
BOUNDARY_COLUMNS = ["plr_id", "plr_name", "pgr_id", "bez", "stadtraum_name", "geometry"]

# Alle Daten beziehen sich auf das Jahr der Lärmkarte (2022):
# MSS 2023 (Datenstand 31.12.2022) und IBB-Mieten 2022.
# Die Tabellen werden über die achtstellige PLR-ID erkannt, nicht über
# feste Kopfzeilen. Werte = Spaltenposition in der jeweiligen Excel-Tabelle.
SOCIAL_STATUS_FILE = RAW / "mss2023_gesamtindex_plr.xlsx"                # Tabelle 1
SOCIAL_INDICATOR_FILE = RAW / "mss2023_indexindikatoren_anteile_plr.xlsx"  # Tabelle 2.1
SOCIAL_ZVALUE_FILE = RAW / "mss2023_indexindikatoren_zwerte_plr.xlsx"      # Tabelle 3
SOCIAL_INDICATOR_COLUMNS = {
    "arbeitslosenanteil_prozent": 3,    # S1: Arbeitslose nach SGB II
    "alleinerziehende_prozent": 4,      # S2: Kinder in alleinerziehenden Haushalten
    "transferbezugsanteil_prozent": 5,  # S3: Transferbezug SGB II und XII
    "kinderarmut_prozent": 6,           # S4: Kinder unter 15 in SGB-II-Bedarfsgemeinschaften
}
SOCIAL_INDICATORS = list(SOCIAL_INDICATOR_COLUMNS)
MSS_CLASS_LABELS = {1: "hoch", 2: "mittel", 3: "niedrig", 4: "sehr niedrig"}

# Mietdaten: IBB-Tabelle mit Planungsraum-ID (Spalte 1), Median (4) und Fallzahl (6).
RENT_FILE = RAW / "Mietdaten.xlsx"
RENT_SHEET = "Planungsräume_2022"       # Hauptanalyse: gleiches Jahr wie Lärmkarte
RENT_SHEET_2025 = "Planungsräume_2025"  # Robustheitscheck: aktuellste Mietdaten

# Lärmdaten: aggregierte Fassadenpegel aus aggregate_noise.py
NOISE_CSV = PROCESSED / "laermdaten_aggregiert.csv"
NOISE_COLUMNS = [
    "laerm_gesamt_lden_db", "laerm_gesamt_ln_db", "laerm_strassen_lden_db",
    "laerm_gesamt_lden_median_db", "anteil_fassaden_lden_ueber_65_prozent",
    "anteil_fassaden_ln_ueber_55_prozent", "anzahl_laermpegel",
]

# Kontrollvariablen der Regression und Gruppierung für geclusterte Standardfehler
CONTROL_VARIABLES = ["log_einwohnerdichte", "innere_stadt"]
CLUSTER_SE_COLUMN = "pgr_id"  # 58 Prognoseräume

# IBB-Angebotsmieten mit sehr wenigen Inseraten sind instabil (IBB-Grenze: 21).
MIN_RENT_LISTINGS = 21
RENT_ROBUSTNESS_THRESHOLDS = [10, 21, 30]

# K-Means: None = Clusterzahl mit höchstem Silhouette-Score, sonst feste Zahl.
# k=4: k=2 hat den höchsten Silhouette-Score (0,33), trennt aber nur "benachteiligt/
# günstig" von "wohlhabend/teuer" und blendet Lärm aus. k=4 (Silhouette 0,28 > 0,25)
# ergibt eine interpretierbare Typologie laut/leise x benachteiligt/wohlhabend.
N_CLUSTERS: int | None = 4
CLUSTER_FEATURES = ["laerm_gesamt_lden_db", "benachteiligungsindex", "angebotsmiete_median_eur_m2"]
# Clusterbenennung: |z-Mittelwert| > Schwelle -> "hoch"/"niedrig", sonst "mittel"
CLUSTER_LEVEL_THRESHOLD_Z = 0.25

# Reproduzierbarkeit
RANDOM_STATE = 42
MORAN_PERMUTATIONS = 999
SIGNIFICANCE_LEVEL = 0.05


# ---------------------------------------------------------------------------
# 2. HILFSFUNKTIONEN
# ---------------------------------------------------------------------------

DEUTSCHE_BESCHRIFTUNG = {
    "laerm_gesamt_lden_db": "Gesamtlärm LDEN, energetisch [dB(A)]",
    "laerm_gesamt_ln_db": "Gesamtlärm LN (Nacht) [dB(A)]",
    "laerm_strassen_lden_db": "Straßenlärm LDEN [dB(A)]",
    "laerm_gesamt_lden_median_db": "Gesamtlärm LDEN, Median [dB(A)]",
    "anteil_fassaden_lden_ueber_65_prozent": "Fassaden > 65 dB(A) LDEN [%]",
    "anteil_fassaden_ln_ueber_55_prozent": "Fassaden > 55 dB(A) LN [%]",
    "arbeitslosenanteil_prozent": "S1 Arbeitslosigkeit [%]",
    "alleinerziehende_prozent": "S2 Alleinerziehende [%]",
    "transferbezugsanteil_prozent": "S3 Transferbezug [%]",
    "kinderarmut_prozent": "S4 Kinderarmut [%]",
    "benachteiligungsindex": "Benachteiligungsindex (PC1, z)",
    "mss_statusklasse": "MSS-Statusklasse",
    "angebotsmiete_median_eur_m2": "Median-Angebotsmiete [EUR/m²]",
    "einwohnerdichte": "Einwohnerdichte [EW/km²]",
    "log_einwohnerdichte": "log(1 + Einwohnerdichte)",
    "innere_stadt": "Innere Stadt (0/1)",
}


def label(col: str) -> str:
    return DEUTSCHE_BESCHRIFTUNG.get(col, col)


def ensure_dirs() -> None:
    for folder in (RAW, PROCESSED, OUT):
        folder.mkdir(parents=True, exist_ok=True)


def normalize_plr_id(series: pd.Series) -> pd.Series:
    """PLR-ID als achtstellige Zeichenkette vereinheitlichen."""
    s = series.astype("string").str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    return s.str.zfill(8)


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def read_plr_rows(path: Path, sheet, id_col: int) -> pd.DataFrame:
    """Liest nur die Zeilen einer Excel-Tabelle, die eine gültige PLR-ID enthalten.

    So werden Titel-, Kopf- und Fußnotenzeilen zuverlässig ignoriert.
    """
    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")
    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype={id_col: str})
    ids = normalize_plr_id(raw[id_col])
    rows = raw.loc[ids.str.fullmatch(r"\d{8}").fillna(False)].copy()
    rows[id_col] = ids[rows.index]
    if rows[id_col].duplicated().any():
        raise ValueError(f"Doppelte PLR-IDs in {path.name} ({sheet}).")
    return rows.reset_index(drop=True)


def p_text(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


# ---------------------------------------------------------------------------
# 3. DATENIMPORT UND ZUSAMMENFÜHRUNG
# ---------------------------------------------------------------------------

def load_boundaries() -> gpd.GeoDataFrame:
    if not BOUNDARIES_FILE.exists():
        raise FileNotFoundError(
            f"Planungsraum-Daten fehlen: {BOUNDARIES_FILE}\n"
            "Bitte LOR-Planungsräume herunterladen und ablegen."
        )
    gdf = gpd.read_file(BOUNDARIES_FILE)
    if gdf.crs is None:
        raise ValueError("Die Planungsraum-Geodaten haben kein CRS. Koordinatensystem klären!")
    gdf["plr_id"] = normalize_plr_id(gdf["plr_id"])
    return gdf[BOUNDARY_COLUMNS].drop_duplicates("plr_id")


def load_social() -> pd.DataFrame:
    """MSS 2023 (Stand 31.12.2022): Statusklasse (Tab. 1), Einzelindikatoren S1-S4 (Tab. 2.1), Status-Index (Tab. 3)."""
    status = read_plr_rows(SOCIAL_STATUS_FILE, 0, 0)
    social = pd.DataFrame({
        "plr_id": status[0],
        "einwohner": to_number(status[2]),
        "mss_statusklasse": to_number(status[3]),
        "sozialstatus_kategorie": status[4].astype("string").str.strip(),
        "sozialdynamik_kategorie": status[6].astype("string").str.strip(),
    })
    expected = social["mss_statusklasse"].map(MSS_CLASS_LABELS)
    inconsistent = social["sozialstatus_kategorie"].notna() & (expected != social["sozialstatus_kategorie"].str.lower())
    if inconsistent.any():
        raise ValueError(f"MSS-Klasse und Klassenname passen nicht zusammen: {social.loc[inconsistent, 'plr_id'].tolist()}")

    indicator_rows = read_plr_rows(SOCIAL_INDICATOR_FILE, 0, 0)
    indicators = pd.DataFrame({"plr_id": indicator_rows[0]})
    for name, position in SOCIAL_INDICATOR_COLUMNS.items():
        indicators[name] = to_number(indicator_rows[position])

    zvalue_rows = read_plr_rows(SOCIAL_ZVALUE_FILE, 0, 0)
    official = pd.DataFrame({"plr_id": zvalue_rows[0], "mss_statusindex": to_number(zvalue_rows[8])})

    social = social.merge(indicators, on="plr_id", how="left", validate="one_to_one")
    return social.merge(official, on="plr_id", how="left", validate="one_to_one")


def load_rents(sheet: str) -> pd.DataFrame:
    """Liest IBB-Planungsraummieten (Median und Zahl der Inserate)."""
    rows = read_plr_rows(RENT_FILE, sheet, 1)
    return pd.DataFrame({
        "plr_id": rows[1],
        "plr_name_ibb": rows[2].astype("string").str.strip(),
        "angebotsmiete_median_roh": to_number(rows[4]),
        "anzahl_mietinserate": to_number(rows[6]),
    })


def load_noise() -> pd.DataFrame:
    if not NOISE_CSV.exists():
        raise FileNotFoundError(f"Keine Lärmdaten gefunden: {NOISE_CSV}. Bitte zuerst aggregate_noise.py ausführen.")
    noise = pd.read_csv(NOISE_CSV, dtype={"plr_id": str})
    noise["plr_id"] = normalize_plr_id(noise["plr_id"])
    missing = [c for c in NOISE_COLUMNS if c not in noise.columns]
    if missing:
        print(f"Hinweis: Lärmspalten fehlen (aggregate_noise.py neu ausführen): {missing}")
    return noise[["plr_id"] + [c for c in NOISE_COLUMNS if c in noise.columns]]


def load_all_data() -> gpd.GeoDataFrame:
    print("\n[1] Lade Planungsräume, MSS-, Miet- und Lärmdaten ...")
    areas = load_boundaries()
    social = load_social()
    rents = load_rents(RENT_SHEET)
    rents_2025 = load_rents(RENT_SHEET_2025).drop(columns="plr_name_ibb").rename(columns={
        "angebotsmiete_median_roh": "angebotsmiete_2025_median_roh",
        "anzahl_mietinserate": "anzahl_mietinserate_2025",
    })
    noise = load_noise()

    data = areas.merge(social, on="plr_id", how="left", validate="one_to_one")
    data = data.merge(rents, on="plr_id", how="left", validate="one_to_one")
    data = data.merge(rents_2025, on="plr_id", how="left", validate="one_to_one")
    data = data.merge(noise, on="plr_id", how="left", validate="one_to_one")

    # Namensabgleich: deckt vertauschte oder abweichende Zuordnungen in der IBB-Tabelle auf.
    name_check = data.loc[
        data["plr_name_ibb"].notna() & (data["plr_name"] != data["plr_name_ibb"]),
        ["plr_id", "plr_name", "plr_name_ibb"],
    ]
    name_check.to_csv(OUT / "pruefung_namensabweichungen_ibb.csv", index=False)
    if len(name_check):
        print(f"Hinweis: {len(name_check)} PLR-Namen weichen in der IBB-Tabelle ab (siehe pruefung_namensabweichungen_ibb.csv).")

    # Abgeleitete Variablen
    data["flaeche_km2"] = data.geometry.area / 1e6
    data["einwohnerdichte"] = data["einwohner"] / data["flaeche_km2"]
    data["log_einwohnerdichte"] = np.log1p(data["einwohnerdichte"])
    data["innere_stadt"] = (data["stadtraum_name"] == "Innere Stadt").astype(int)

    # Angebotsmieten mit zu geringer Fallzahl aus der Hauptanalyse nehmen (nicht imputieren).
    data["angebotsmiete_median_eur_m2"] = data["angebotsmiete_median_roh"].where(
        data["anzahl_mietinserate"] >= MIN_RENT_LISTINGS
    )

    # Datenqualitätsbericht NACH allen Filtern
    quality_cols = [c for c in data.columns if c not in ("geometry", "plr_id", "plr_name", "plr_name_ibb")]
    quality = pd.DataFrame({
        "gueltig": data[quality_cols].notna().sum(),
        "fehlend": data[quality_cols].isna().sum(),
    })
    quality.to_csv(OUT / "datenqualitaet.csv")
    print(f"\nDatenqualität nach Join und Mietfilter (Planungsräume: {len(data)}):")
    print(quality.to_string())
    return data


def save_merged(data: gpd.GeoDataFrame) -> None:
    out = data.copy()
    for col in out.columns:
        if isinstance(out[col].dtype, pd.CategoricalDtype):
            out[col] = out[col].astype("string")
    out.to_file(PROCESSED / "berlin_merged.gpkg", driver="GPKG")
    out.drop(columns="geometry").to_csv(PROCESSED / "berlin_merged.csv", index=False)
    print(f"Zusammengeführter Datensatz gespeichert: {PROCESSED / 'berlin_merged.gpkg'}")


# ---------------------------------------------------------------------------
# 4. PCA: BENACHTEILIGUNGSINDEX AUS DEN MSS-STATUS-INDIKATOREN
# ---------------------------------------------------------------------------

def run_pca_benachteiligungsindex(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """PCA ausschließlich für soziale Indikatoren (S1-S4); PC1 wird der Deprivationsindex."""
    print("\n[2] PCA: Benachteiligungsindex aus S1-S4 ...")
    X = df[SOCIAL_INDICATORS].dropna()
    n, p = X.shape

    # Bartlett-Test auf Sphärizität: Sind die Indikatoren überhaupt korreliert?
    corr = X.corr()
    corr.to_csv(OUT / "pca_indikator_korrelationen.csv")
    bartlett_chi2 = -(n - 1 - (2 * p + 5) / 6) * np.log(np.linalg.det(corr.values))
    bartlett_p = stats.chi2.sf(bartlett_chi2, p * (p - 1) / 2)

    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA()
    components = pca.fit_transform(X_scaled)
    names = [f"PC{i + 1}" for i in range(p)]

    explained = pd.DataFrame({
        "component": names,
        "eigenvalue": pca.explained_variance_,
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "cumulative_variance": np.cumsum(pca.explained_variance_ratio_),
    })
    explained.to_csv(OUT / "pca_explained_variance.csv", index=False)

    # Ladungen = Korrelation zwischen Indikator und Komponente
    loadings = pd.DataFrame(pca.components_.T * np.sqrt(pca.explained_variance_), index=SOCIAL_INDICATORS, columns=names)

    # Vorzeichen so festlegen, dass höhere Werte stärkere Benachteiligung bedeuten.
    sign = np.sign(loadings["PC1"].sum())
    loadings["PC1"] *= sign
    loadings.to_csv(OUT / "pca_loadings.csv")
    pc1 = sign * components[:, 0]

    df = df.copy()
    df.loc[X.index, "benachteiligungsindex"] = (pc1 - pc1.mean()) / pc1.std(ddof=1)

    # Validierung gegen den amtlichen MSS-Status-Index und die Statusklasse
    valid = df[["benachteiligungsindex", "mss_statusindex", "mss_statusklasse"]].dropna()
    r_official = stats.pearsonr(valid["benachteiligungsindex"], valid["mss_statusindex"]).statistic
    rho_class = stats.spearmanr(valid["benachteiligungsindex"], valid["mss_statusklasse"]).statistic

    report = (
        f"PCA über {p} MSS-Status-Indikatoren, n = {n} Planungsräume\n"
        f"Bartlett-Test: Chi² = {bartlett_chi2:.1f}, {p_text(bartlett_p)}\n"
        f"Eigenwerte: {np.round(pca.explained_variance_, 3).tolist()} (Kaiser-Kriterium: >1)\n"
        f"Erklärte Varianz PC1: {pca.explained_variance_ratio_[0]:.1%}\n\n"
        f"Ladungen PC1:\n{loadings['PC1'].round(3).to_string()}\n\n"
        f"Validierung: Pearson r(PC1, amtlicher MSS-Status-Index) = {r_official:.3f}\n"
        f"Validierung: Spearman rho(PC1, MSS-Statusklasse) = {rho_class:.3f}\n"
        "Der Index ist z-standardisiert (Mittelwert 0, SD 1); höhere Werte = stärkere Benachteiligung.\n"
    )
    (OUT / "pca_bericht.txt").write_text(report, encoding="utf-8")
    print(report)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].bar(names, pca.explained_variance_, color="steelblue")
    axes[0].axhline(1, color="grey", linestyle="--", label="Kaiser-Kriterium")
    axes[0].set_title("Scree-Plot")
    axes[0].set_ylabel("Eigenwert")
    axes[0].legend()
    loadings["PC1"].rename(index=label).sort_values().plot.barh(ax=axes[1], color="darkorange")
    axes[1].set_title(f"Ladungen PC1 ({pca.explained_variance_ratio_[0]:.1%} erklärte Varianz)")
    axes[1].set_xlim(0, 1)
    fig.tight_layout()
    fig.savefig(OUT / "pca_scree_ladungen.png", dpi=170)
    plt.close(fig)
    return df


# ---------------------------------------------------------------------------
# 5. EDA: DESKRIPTIVE STATISTIK, KORRELATIONEN UND GRUPPENVERGLEICHE
# ---------------------------------------------------------------------------

EDA_COLUMNS = [
    "laerm_gesamt_lden_db", "laerm_gesamt_ln_db", "laerm_strassen_lden_db",
    "laerm_gesamt_lden_median_db", "anteil_fassaden_lden_ueber_65_prozent",
    "benachteiligungsindex", *SOCIAL_INDICATORS,
    "angebotsmiete_median_eur_m2", "einwohnerdichte",
]
NOISE_TARGETS = [
    "laerm_gesamt_lden_db", "laerm_gesamt_ln_db", "laerm_strassen_lden_db",
    "laerm_gesamt_lden_median_db", "anteil_fassaden_lden_ueber_65_prozent",
]


def run_eda(df: gpd.GeoDataFrame) -> None:
    print("\n[3] Explorative Datenanalyse ...")
    cols = [c for c in EDA_COLUMNS if c in df.columns and df[c].notna().sum() > 2]

    summary = df[cols].describe().T
    summary["variance"] = df[cols].var()
    summary["skewness"] = df[cols].skew()
    summary.to_csv(OUT / "descriptive_statistics.csv")
    print(summary.round(3).to_string())

    for col in cols:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(df[col].dropna(), kde=True, ax=ax)
        ax.set_title(f"Verteilung: {label(col)}")
        ax.set_xlabel(label(col))
        fig.tight_layout()
        fig.savefig(OUT / f"hist_{col}.png", dpi=160)
        plt.close(fig)

    # Boxplots je Variable (unterschiedliche Einheiten -> eigene Achsen)
    ncols = 4
    nrows = int(np.ceil(len(cols) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3.2 * nrows))
    for ax, col in zip(axes.flat, cols):
        sns.boxplot(y=df[col].dropna(), ax=ax, color="lightsteelblue")
        ax.set_title(label(col), fontsize=9)
        ax.set_ylabel("")
    for ax in list(axes.flat)[len(cols):]:
        ax.set_visible(False)
    fig.suptitle("Boxplots der Analysevariablen")
    fig.tight_layout()
    fig.savefig(OUT / "boxplots.png", dpi=160)
    plt.close(fig)

    for method in ("pearson", "spearman"):
        corr = df[cols].corr(method=method)
        corr.to_csv(OUT / f"correlation_matrix_{method}.csv")
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr.rename(index=label, columns=label), annot=True, cmap="vlag", center=0, fmt=".2f", ax=ax)
        ax.set_title(f"{method.capitalize()}-Korrelationsmatrix")
        fig.tight_layout()
        fig.savefig(OUT / f"correlation_heatmap_{method}.png", dpi=170)
        plt.close(fig)

    # Paarweise Pearson-/Spearman-Tests
    pairs = [("benachteiligungsindex", target) for target in NOISE_TARGETS]
    pairs += [(indicator, "laerm_gesamt_lden_db") for indicator in SOCIAL_INDICATORS]
    pairs += [
        ("angebotsmiete_median_eur_m2", "laerm_gesamt_lden_db"),
        ("benachteiligungsindex", "angebotsmiete_median_eur_m2"),
    ]
    scatter_pairs = {
        ("benachteiligungsindex", "laerm_gesamt_lden_db"),
        ("benachteiligungsindex", "anteil_fassaden_lden_ueber_65_prozent"),
        ("angebotsmiete_median_eur_m2", "laerm_gesamt_lden_db"),
        ("benachteiligungsindex", "angebotsmiete_median_eur_m2"),
    }
    rows = []
    for x, y in pairs:
        if x not in df or y not in df:
            continue
        pair = df[[x, y]].dropna()
        pearson = stats.pearsonr(pair[x], pair[y])
        spearman = stats.spearmanr(pair[x], pair[y])
        rows.append({
            "x": x, "y": y, "n": len(pair),
            "pearson_r": pearson.statistic, "pearson_p": pearson.pvalue,
            "spearman_rho": spearman.statistic, "spearman_p": spearman.pvalue,
        })
        if (x, y) not in scatter_pairs:
            continue
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        sns.regplot(data=pair, x=x, y=y, lowess=True, scatter_kws={"alpha": 0.5, "s": 14},
                    line_kws={"color": "crimson"}, ax=ax)
        ax.set_title(f"{label(x)} vs. {label(y)}\nr = {pearson.statistic:.2f}, rho = {spearman.statistic:.2f}, n = {len(pair)}",
                     fontsize=10)
        ax.set_xlabel(label(x))
        ax.set_ylabel(label(y))
        fig.tight_layout()
        fig.savefig(OUT / f"scatter_{x}_vs_{y}.png", dpi=170)
        plt.close(fig)
    pd.DataFrame(rows).to_csv(OUT / "pairwise_correlations.csv", index=False)


def run_group_comparison(df: gpd.GeoDataFrame) -> pd.DataFrame:
    """Lärm nach MSS-Statusklasse und nach Quintilen des Benachteiligungsindex.

    Kruskal-Wallis (rangbasiert) und ANOVA prüfen, ob sich die Gruppen unterscheiden,
    ohne einen linearen Verlauf vorauszusetzen.
    """
    print("\n[4] Gruppenvergleiche ...")
    targets = [c for c in ("laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent") if c in df.columns]
    tests, profiles = [], []
    for group_col in ("mss_statusklasse", "deprivationsquintil"):
        for target in targets:
            sub = df[[group_col, target]].dropna()
            groups = [g[target] for _, g in sub.groupby(group_col, observed=True)]
            kw = stats.kruskal(*groups)
            anova = stats.f_oneway(*groups)
            tests.append({
                "gruppe": group_col, "zielvariable": target, "n": len(sub),
                "kruskal_H": kw.statistic, "kruskal_p": kw.pvalue,
                "anova_F": anova.statistic, "anova_p": anova.pvalue,
            })
            profile = sub.groupby(group_col, observed=True)[target].agg(["count", "mean", "median", "std"])
            profiles.append(profile.assign(gruppe=group_col, zielvariable=target).reset_index(names="stufe"))
    tests = pd.DataFrame(tests)
    tests.to_csv(OUT / "gruppenvergleich_tests.csv", index=False)
    pd.concat(profiles).to_csv(OUT / "gruppenvergleich_profile.csv", index=False)
    print(tests.round(4).to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for ax, group_col, title in zip(axes, ("mss_statusklasse", "deprivationsquintil"),
                                    ("MSS-Statusklasse (1 = hoch, 4 = sehr niedrig)", "Quintile des Benachteiligungsindex")):
        sub = df[[group_col, "laerm_gesamt_lden_db"]].dropna()
        sns.boxplot(data=sub, x=group_col, y="laerm_gesamt_lden_db", color="lightsteelblue", showfliers=False, ax=ax)
        sns.stripplot(data=sub, x=group_col, y="laerm_gesamt_lden_db", color="black", alpha=0.25, size=2.5, ax=ax)
        p = tests.query("gruppe == @group_col and zielvariable == 'laerm_gesamt_lden_db'")["kruskal_p"].iloc[0]
        ax.set_title(f"{title}\nKruskal-Wallis: {p_text(p)}", fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel(label("laerm_gesamt_lden_db"))
        ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "boxplot_laerm_nach_sozialer_lage.png", dpi=170)
    plt.close(fig)
    return tests


# ---------------------------------------------------------------------------
# 6. REGRESSIONEN
# ---------------------------------------------------------------------------

def fit_regression(df: pd.DataFrame, target: str, predictors: list[str], name: str,
                   cluster_se: bool) -> tuple[sm.regression.linear_model.RegressionResultsWrapper, pd.DataFrame] | None:
    """OLS mit HC3- oder nach Prognoseraum geclusterten Standardfehlern.

    HC3 korrigiert nur Heteroskedastizität. Bei räumlich korrelierten Residuen sind
    geclusterte Standardfehler die konservativere Wahl.
    """
    if target not in df.columns or any(c not in df.columns for c in predictors):
        print(f"Regression '{name}' übersprungen: Variablen fehlen.")
        return None
    model_data = df[[target, *predictors, CLUSTER_SE_COLUMN]].replace([np.inf, -np.inf], np.nan).dropna()
    X = sm.add_constant(model_data[predictors].astype(float))
    y = model_data[target].astype(float)
    if cluster_se:
        groups = pd.factorize(model_data[CLUSTER_SE_COLUMN])[0]
        model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    else:
        model = sm.OLS(y, X).fit(cov_type="HC3")
    (OUT / f"regression_{name}.txt").write_text(model.summary().as_text(), encoding="utf-8")
    print(f"Regression {name}: n={int(model.nobs)}, R²={model.rsquared:.3f}, adj. R²={model.rsquared_adj:.3f}")
    return model, model_data


def coefficient_rows(model, name: str, target: str, cluster_se: bool) -> list[dict]:
    ci = model.conf_int()
    return [{
        "modell": name, "zielvariable": target, "term": term,
        "koeffizient": model.params[term], "std_fehler": model.bse[term],
        "ci_unten": ci.loc[term, 0], "ci_oben": ci.loc[term, 1], "p_wert": model.pvalues[term],
        "n": int(model.nobs), "r2": model.rsquared, "r2_adj": model.rsquared_adj,
        "standardfehler": f"Cluster ({CLUSTER_SE_COLUMN})" if cluster_se else "HC3",
    } for term in model.params.index if term != "const"]


def vif_rows(model_data: pd.DataFrame, predictors: list[str], name: str) -> list[dict]:
    """VIF korrekt mit Konstante und auf genau der Modellstichprobe."""
    if len(predictors) < 2:
        return []
    X = sm.add_constant(model_data[predictors].astype(float)).values
    return [{"modell": name, "feature": col, "VIF": variance_inflation_factor(X, i + 1)}
            for i, col in enumerate(predictors)]


def run_regressions(df: gpd.GeoDataFrame) -> dict:
    """Modell A: Lärm ~ Benachteiligung. Modell B: Miete ~ Lärm + Benachteiligung."""
    print("\n[5] Regressionsmodelle ...")
    noise = "laerm_gesamt_lden_db"
    rent = "angebotsmiete_median_eur_m2"
    index = "benachteiligungsindex"
    specs = [
        ("A1_laerm_einfach_HC3", noise, [index], False),
        ("A2_laerm_einfach_cluster", noise, [index], True),
        ("A3_laerm_kontrollen_cluster", noise, [index, *CONTROL_VARIABLES], True),
        ("A4_laerm_median_kontrollen_cluster", "laerm_gesamt_lden_median_db", [index, *CONTROL_VARIABLES], True),
        ("A5_anteil65_kontrollen_cluster", "anteil_fassaden_lden_ueber_65_prozent", [index, *CONTROL_VARIABLES], True),
        ("A6_strassenlaerm_kontrollen_cluster", "laerm_strassen_lden_db", [index, *CONTROL_VARIABLES], True),
        ("B1_miete_HC3", rent, [noise, index], False),
        ("B2_miete_kontrollen_cluster", rent, [noise, index, *CONTROL_VARIABLES], True),
    ]
    results, coefficients, vifs = {}, [], []
    for name, target, predictors, cluster_se in specs:
        fitted = fit_regression(df, target, predictors, name, cluster_se)
        if fitted is None:
            continue
        model, model_data = fitted
        results[name] = model
        coefficients += coefficient_rows(model, name, target, cluster_se)
        vifs += vif_rows(model_data, predictors, name)
    coefficients = pd.DataFrame(coefficients)
    coefficients.to_csv(OUT / "regression_uebersicht.csv", index=False)
    pd.DataFrame(vifs).to_csv(OUT / "vif_values.csv", index=False)
    print(coefficients.query("term in [@index, @noise]").round(4).to_string(index=False))

    # Robustheit Mietmodell: Mindestfallzahl und aktuellstes Mietjahr 2025
    robustness = []
    rent_predictors = [noise, index, *CONTROL_VARIABLES]
    variants = [(f"Mindestfallzahl {t}", "angebotsmiete_median_roh", "anzahl_mietinserate", t)
                for t in RENT_ROBUSTNESS_THRESHOLDS]
    variants.append(("Mieten 2025, Mindestfallzahl 21", "angebotsmiete_2025_median_roh",
                     "anzahl_mietinserate_2025", MIN_RENT_LISTINGS))
    for variant, rent_col, count_col, threshold in variants:
        sub = df.assign(_miete=df[rent_col].where(df[count_col] >= threshold))
        model_data = sub[["_miete", *rent_predictors, CLUSTER_SE_COLUMN]].dropna()
        model = sm.OLS(model_data["_miete"], sm.add_constant(model_data[rent_predictors].astype(float))).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(model_data[CLUSTER_SE_COLUMN])[0]})
        robustness.append({
            "variante": variant, "n": int(model.nobs), "r2": model.rsquared,
            "b_laerm": model.params[noise], "p_laerm": model.pvalues[noise],
            "b_benachteiligung": model.params[index], "p_benachteiligung": model.pvalues[index],
        })
    robustness = pd.DataFrame(robustness)
    robustness.to_csv(OUT / "regression_robustheit_miete.csv", index=False)
    print("\nRobustheit Mietmodell:")
    print(robustness.round(4).to_string(index=False))

    residuals = {
        name: pd.Series(results[name].resid, name=name)
        for name in ("A1_laerm_einfach_HC3", "A3_laerm_kontrollen_cluster") if name in results
    }
    return {"models": results, "coefficients": coefficients, "robustness": robustness, "residuals": residuals}


# ---------------------------------------------------------------------------
# 7. K-MEANS-CLUSTERING
# ---------------------------------------------------------------------------

def describe_level(z: float) -> str:
    return "hoch" if z > CLUSTER_LEVEL_THRESHOLD_Z else "niedrig" if z < -CLUSTER_LEVEL_THRESHOLD_Z else "mittel"


def run_clustering(df: gpd.GeoDataFrame) -> pd.Series:
    """K-Means mit Lärm, Benachteiligungsindex und Mieten (standardisiert)."""
    print("\n[6] K-Means-Clustering ...")
    X = df[CLUSTER_FEATURES].dropna()
    X_scaled = StandardScaler().fit_transform(X)

    scores = []
    for k in range(2, 8):
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        labels = km.fit_predict(X_scaled)
        scores.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(X_scaled, labels)})
    scores = pd.DataFrame(scores)
    scores.to_csv(OUT / "kmeans_model_selection.csv", index=False)
    best_k = N_CLUSTERS or int(scores.loc[scores["silhouette"].idxmax(), "k"])
    print(scores.round(3).to_string(index=False))
    print(f"Gewählte Clusterzahl k={best_k} ({'fest gesetzt' if N_CLUSTERS else 'höchster Silhouette-Score'})")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(scores["k"], scores["inertia"], marker="o")
    axes[0].set_title("Elbow-Methode")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inertia")
    axes[1].plot(scores["k"], scores["silhouette"], marker="o", color="darkorange")
    axes[1].axvline(best_k, color="grey", linestyle="--")
    axes[1].set_title("Silhouette-Score")
    axes[1].set_xlabel("k")
    fig.tight_layout()
    fig.savefig(OUT / "kmeans_model_selection.png", dpi=160)
    plt.close(fig)

    km = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=20)
    raw_labels = km.fit_predict(X_scaled)
    # Cluster nach mittlerem Lärm sortieren, damit die Nummerierung stabil und lesbar ist.
    order = pd.Series(X_scaled[:, 0]).groupby(raw_labels).mean().sort_values().index
    remap = {old: new for new, old in enumerate(order, start=1)}
    labels = np.array([remap[label_] for label_ in raw_labels])

    z_profile = pd.DataFrame(X_scaled, columns=CLUSTER_FEATURES).groupby(labels).mean()
    short = {"laerm_gesamt_lden_db": "Lärm", "benachteiligungsindex": "Benachteiligung",
             "angebotsmiete_median_eur_m2": "Miete"}
    names = {c: f"C{c}: " + " · ".join(f"{short[f]} {describe_level(z_profile.loc[c, f])}" for f in CLUSTER_FEATURES)
             for c in z_profile.index}

    profile = X.groupby(labels)[CLUSTER_FEATURES].mean()
    profile.insert(0, "anzahl_plr", pd.Series(labels).value_counts().sort_index().values)
    profile.insert(0, "clustername", [names[c] for c in profile.index])
    profile.index.name = "cluster"
    profile.to_csv(OUT / "kmeans_cluster_profiles.csv")
    print(profile.round(2).to_string())

    clusters = pd.Series([names[c] for c in labels], index=X.index, name="cluster")
    df.loc[X.index, ["plr_id", "plr_name"]].assign(cluster_nr=labels, cluster=clusters).to_csv(
        OUT / "kmeans_clusters.csv", index=False)

    pca_vis = PCA(n_components=2)
    components_vis = pca_vis.fit_transform(X_scaled)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    palette = cluster_palette(names.values())
    for name in names.values():
        mask = clusters.values == name
        ax.scatter(components_vis[mask, 0], components_vis[mask, 1], color=palette[name], alpha=0.7, s=16, label=name)
    ax.set_xlabel(f"PC1 ({pca_vis.explained_variance_ratio_[0]:.1%})")
    ax.set_ylabel(f"PC2 ({pca_vis.explained_variance_ratio_[1]:.1%})")
    ax.set_title(f"PCA-Projektion der K-Means-Cluster (k={best_k})")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "kmeans_clusters.png", dpi=170)
    plt.close(fig)
    return clusters


def cluster_palette(names) -> dict:
    names = sorted(names)
    return dict(zip(names, sns.color_palette("Set2", len(names))))


# ---------------------------------------------------------------------------
# 8. RÄUMLICHE AUTOKORRELATION: MORAN'S I
# ---------------------------------------------------------------------------

def run_morans_i(gdf: gpd.GeoDataFrame, residuals: dict[str, pd.Series]) -> pd.DataFrame:
    print("\n[7] Moran's I ...")
    if not HAS_PYSAL:
        print("Moran's I übersprungen. Installiert libpysal und esda.")
        return pd.DataFrame()

    series = {col: gdf[col] for col in ("laerm_gesamt_lden_db", "benachteiligungsindex", "angebotsmiete_median_eur_m2")
              if col in gdf.columns}
    file_names = {"A1_laerm_einfach_HC3": "residuals", "A3_laerm_kontrollen_cluster": "residuals_kontrollen"}
    series.update({file_names[name]: values for name, values in residuals.items()})

    rows = []
    for name, values in series.items():
        values = values.dropna()
        subset = gdf.loc[values.index, ["geometry"]]
        # Queen-Nachbarschaft; Inseln werden über w.islands sichtbar.
        weights = Queen.from_dataframe(subset, use_index=False)
        weights.transform = "r"
        np.random.seed(RANDOM_STATE)
        mi = Moran(values.values, weights, permutations=MORAN_PERMUTATIONS)
        rows.append({"variable": name, "n": len(values), "I": mi.I, "p_sim": mi.p_sim,
                     "z_sim": mi.z_sim, "inseln": len(weights.islands)})
        (OUT / f"morans_i_{name}.txt").write_text(
            f"Variable: {name}\nn: {len(values)}\nI: {mi.I}\np_sim: {mi.p_sim} "
            f"(kleinstmöglicher Wert bei {MORAN_PERMUTATIONS} Permutationen: {1 / (MORAN_PERMUTATIONS + 1)})\n"
            f"z_sim: {mi.z_sim}\nIslands: {weights.islands}\n", encoding="utf-8")
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "morans_i_uebersicht.csv", index=False)
    print(result.round(4).to_string(index=False))
    return result


# ---------------------------------------------------------------------------
# 9. KARTEN, ERGEBNISGRAFIK UND HAUPTPROGRAMM
# ---------------------------------------------------------------------------

def draw_districts(ax, gdf: gpd.GeoDataFrame, labels: bool = False) -> None:
    districts = gdf[["bez", "geometry"]].dissolve(by="bez")
    districts.boundary.plot(ax=ax, color="black", linewidth=0.7)
    if labels:
        for name, point in districts.representative_point().items():
            ax.annotate(name.split(" - ")[-1], (point.x, point.y), ha="center", fontsize=7,
                        bbox={"boxstyle": "round,pad=0.15", "fc": "white", "alpha": 0.6, "lw": 0})


def export_choropleths(gdf: gpd.GeoDataFrame) -> None:
    map_vars = [
        "laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent", "benachteiligungsindex",
        "angebotsmiete_median_eur_m2", *SOCIAL_INDICATORS,
    ]
    for col in map_vars:
        if col not in gdf.columns or gdf[col].notna().sum() == 0:
            continue
        fig, ax = plt.subplots(figsize=(10, 8.5))
        gdf.plot(column=col, cmap="magma_r" if "laerm" in col or "fassaden" in col else "viridis", legend=True,
                 edgecolor="white", linewidth=0.15, ax=ax, legend_kwds={"shrink": 0.6, "label": label(col)},
                 missing_kwds={"color": "lightgrey", "label": "Keine Daten"})
        draw_districts(ax, gdf)
        ax.set_title(f"Berlin nach Planungsräumen: {label(col)}")
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(OUT / f"map_{col}.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 8.5))
    status = gdf.assign(mss=gdf["mss_statusklasse"].map(lambda v: f"{int(v)} – {MSS_CLASS_LABELS[int(v)]}" if pd.notna(v) else None))
    status.plot(column="mss", categorical=True, cmap="RdYlGn_r", legend=True, edgecolor="white", linewidth=0.15, ax=ax,
                legend_kwds={"title": "MSS-Status", "loc": "lower left"},
                missing_kwds={"color": "lightgrey", "label": "Keine Daten"})
    draw_districts(ax, gdf)
    ax.set_title("Berlin nach Planungsräumen: MSS-Statusklasse 2023 (Stand 31.12.2022)")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(OUT / "map_mss_statusklasse.png", dpi=180)
    plt.close(fig)


def export_cluster_map(gdf: gpd.GeoDataFrame) -> None:
    names = sorted(gdf["cluster"].dropna().unique())
    palette = cluster_palette(names)
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf[gdf["cluster"].isna()].plot(ax=ax, color="#e0e0e0", edgecolor="white", linewidth=0.15)
    for name in names:
        gdf[gdf["cluster"] == name].plot(ax=ax, color=palette[name], edgecolor="white", linewidth=0.15)
    draw_districts(ax, gdf, labels=True)
    counts = gdf["cluster"].value_counts()
    handles = [plt.Rectangle((0, 0), 1, 1, color=palette[n]) for n in names]
    handles.append(plt.Rectangle((0, 0), 1, 1, color="#e0e0e0"))
    legend_labels = [f"{n} (n = {counts[n]})" for n in names]
    legend_labels.append(f"Nicht geclustert: Miete oder Sozialdaten fehlen (n = {gdf['cluster'].isna().sum()})")
    ax.legend(handles, legend_labels, loc="lower left", fontsize=8, title="Gebietstypen (K-Means)", title_fontsize=9)
    ax.set_title("Berlin: Gebietstypen nach Lärm, sozialer Benachteiligung und Angebotsmiete", fontsize=13)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(OUT / "map_kmeans_cluster.png", dpi=200)
    plt.close(fig)


def build_conclusion(df: gpd.GeoDataFrame, regression: dict, group_tests: pd.DataFrame,
                     moran: pd.DataFrame) -> list[str]:
    """Formuliert die Antwort auf die Leitfrage regelbasiert aus den berechneten Kennzahlen."""
    coef = regression["coefficients"].set_index(["modell", "term"])
    index = "benachteiligungsindex"
    a1 = coef.loc[("A1_laerm_einfach_HC3", index)]
    a3 = coef.loc[("A3_laerm_kontrollen_cluster", index)]
    a6 = coef.loc[("A6_strassenlaerm_kontrollen_cluster", index)]
    b2_noise = coef.loc[("B2_miete_kontrollen_cluster", "laerm_gesamt_lden_db")]
    b2_index = coef.loc[("B2_miete_kontrollen_cluster", index)]
    quintile_means = df.groupby("deprivationsquintil", observed=True)["laerm_gesamt_lden_db"].mean()
    kw = group_tests.query("gruppe == 'deprivationsquintil' and zielvariable == 'laerm_gesamt_lden_db'")["kruskal_p"].iloc[0]
    robust = a3["ci_unten"] > 0 or a3["ci_oben"] < 0
    q1_gap = quintile_means.iloc[1:].mean() - quintile_means.iloc[0]
    upper_range = quintile_means.iloc[1:].max() - quintile_means.iloc[1:].min()
    clusters = df["cluster"].dropna()
    loud_deprived = clusters[clusters.str.contains("Lärm hoch · Benachteiligung hoch", regex=False)]

    if robust and a3["koeffizient"] > 0:
        h1 = "H1 gestützt: Auch mit Kontrollen und räumlich geclusterten Fehlern ist mehr Benachteiligung mit mehr Lärm verbunden."
    elif a1["p_wert"] < SIGNIFICANCE_LEVEL:
        h1 = ("H1 nur schwach / nicht robust: Im einfachen Modell signifikant, aber nicht mehr nach Kontrolle von Dichte und "
              "Lage sowie räumlich geclusterten Standardfehlern.")
    else:
        h1 = "H1 nicht gestützt: Kein signifikanter linearer Zusammenhang zwischen Benachteiligung und Lärm."

    lines = [
        h1,
        f"Effekt (A1): {a1['koeffizient']:+.2f} dB pro SD Benachteiligung, R² = {a1['r2']:.3f}, {p_text(a1['p_wert'])}.",
        f"Mit Kontrollen (A3): {a3['koeffizient']:+.2f} dB [{a3['ci_unten']:+.2f}; {a3['ci_oben']:+.2f}], {p_text(a3['p_wert'])}.",
        "Mittlerer Lärm je Quintil: " + " | ".join(f"{v:.1f}" for v in quintile_means.values)
        + f" dB (Q1→Q5), Kruskal-Wallis {p_text(kw)}. Muster: Die am wenigsten benachteiligten Gebiete (Q1) "
        f"sind im Mittel {q1_gap:.1f} dB leiser; zwischen Q2 und Q5 liegen nur {upper_range:.1f} dB "
        "→ kein Gradient 'je benachteiligter, desto lauter'.",
        f"Nur Straßenlärm (A6): {a6['koeffizient']:+.2f} dB [{a6['ci_unten']:+.2f}; {a6['ci_oben']:+.2f}], {p_text(a6['p_wert'])}"
        + (" → beim Straßenverkehrslärm ist der Zusammenhang robust." if a6["ci_unten"] > 0 else "."),
        f"H2: Miete steigt um {b2_noise['koeffizient']:+.2f} EUR/m² pro dB ({p_text(b2_noise['p_wert'])}) und sinkt um "
        f"{-b2_index['koeffizient']:.2f} EUR/m² pro SD Benachteiligung ({p_text(b2_index['p_wert'])}) – Lageeffekt, keine Kausalität.",
    ]
    if len(loud_deprived):
        lines.append(f"H3: {clusters.nunique()} Gebietstypen; {len(loud_deprived)} von {len(clusters)} geclusterten PLR "
                     f"({len(loud_deprived) / len(clusters):.0%}) sind zugleich laut und benachteiligt (Mehrfachbelastung).")
    if not moran.empty:
        resid = moran.set_index("variable")
        lines.append(f"Räumlich: Lärm I = {resid.loc['laerm_gesamt_lden_db', 'I']:.2f}, Residuen A1 I = "
                     f"{resid.loc['residuals', 'I']:.2f}, A3 I = {resid.loc['residuals_kontrollen', 'I']:.2f} "
                     "→ Lärm ist stark räumlich geprägt, OLS erfasst das nicht vollständig.")
    return lines


def plot_final_result(df: gpd.GeoDataFrame, regression: dict, group_tests: pd.DataFrame, moran: pd.DataFrame) -> None:
    conclusion = build_conclusion(df, regression, group_tests, moran)
    (OUT / "ergebnis_zusammenfassung.txt").write_text("\n".join(conclusion) + "\n", encoding="utf-8")
    print("\nERGEBNIS ZUR LEITFRAGE:\n" + "\n".join(f"- {line}" for line in conclusion))

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    sub = df[["deprivationsquintil", "laerm_gesamt_lden_db"]].dropna()
    sns.boxplot(data=sub, x="deprivationsquintil", y="laerm_gesamt_lden_db", color="lightsteelblue", showfliers=False,
                ax=axes[0, 0])
    sns.pointplot(data=sub, x="deprivationsquintil", y="laerm_gesamt_lden_db", color="crimson", errorbar=("ci", 95),
                  seed=RANDOM_STATE, ax=axes[0, 0])
    axes[0, 0].set_title("A  Lärm nach sozialer Benachteiligung (rot: Mittelwert, 95%-KI)")
    axes[0, 0].set_xlabel("Quintile des Benachteiligungsindex")
    axes[0, 0].set_ylabel(label("laerm_gesamt_lden_db"))

    share = "anteil_fassaden_lden_ueber_65_prozent"
    if share in df.columns:
        sns.barplot(data=df, x="deprivationsquintil", y=share, color="darkorange", errorbar=("ci", 95),
                    seed=RANDOM_STATE, ax=axes[0, 1])
        axes[0, 1].set_title("B  Anteil Fassaden über 65 dB(A) LDEN (95%-KI)")
        axes[0, 1].set_xlabel("Quintile des Benachteiligungsindex")
        axes[0, 1].set_ylabel(label(share))
    for ax in axes[0]:
        ax.tick_params(axis="x", labelsize=8)

    coef = regression["coefficients"].query("term == 'benachteiligungsindex' and zielvariable != 'angebotsmiete_median_eur_m2'")
    model_labels = {
        "A1_laerm_einfach_HC3": "A1 LDEN energetisch\nOLS, HC3",
        "A2_laerm_einfach_cluster": "A2 LDEN energetisch\nCluster-SE (Prognoseraum)",
        "A3_laerm_kontrollen_cluster": "A3 LDEN energetisch\n+ Dichte & Innere Stadt",
        "A4_laerm_median_kontrollen_cluster": "A4 LDEN Median\n+ Dichte & Innere Stadt",
        "A6_strassenlaerm_kontrollen_cluster": "A6 nur Straßenlärm LDEN\n+ Dichte & Innere Stadt",
    }
    coef = coef[coef["modell"].isin(model_labels)].iloc[::-1]
    y_pos = np.arange(len(coef))
    for y, (_, row) in zip(y_pos, coef.iterrows()):
        color = "seagreen" if (row["ci_unten"] > 0 or row["ci_oben"] < 0) else "grey"
        axes[1, 0].errorbar(row["koeffizient"], y, xerr=[[row["koeffizient"] - row["ci_unten"]], [row["ci_oben"] - row["koeffizient"]]],
                            fmt="o", color=color, capsize=5, lw=2, markersize=7)
    axes[1, 0].axvline(0, color="black", linestyle="--", lw=1)
    axes[1, 0].set_yticks(y_pos, [model_labels[m] for m in coef["modell"]], fontsize=8)
    axes[1, 0].set_xlabel("Effekt auf Lärm [dB(A)] pro Standardabweichung Benachteiligung (95%-KI)")
    axes[1, 0].set_title("C  Regressionskoeffizient Benachteiligung → Lärm\n(grün: signifikant, grau: KI enthält 0)")

    axes[1, 1].set_axis_off()
    axes[1, 1].set_title("D  Antwort auf die Leitfrage", loc="left", fontweight="bold")
    text = "\n\n".join(textwrap.fill(line, 70) for line in conclusion)
    axes[1, 1].text(0, 0.98, text, va="top", ha="left", fontsize=9.5, transform=axes[1, 1].transAxes,
                    bbox={"boxstyle": "round", "fc": "#f7f7f7", "ec": "#bbbbbb"})

    fig.suptitle("Sind sozial benachteiligte Berliner Planungsräume stärker von Lärm betroffen?", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT / "ergebnis_leitfrage.png", dpi=200)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    print("=" * 72)
    print("BERLIN DATA SCIENCE: LÄRM · SOZIALE LAGE · MIETEN")
    print("=" * 72)

    try:
        data = load_all_data()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print("\nDATENIMPORT NOCH NICHT ABGESCHLOSSEN:")
        print(exc)
        return

    data = run_pca_benachteiligungsindex(data)
    data["deprivationsquintil"] = pd.qcut(
        data["benachteiligungsindex"], 5,
        labels=["Q1\ngeringste", "Q2", "Q3", "Q4", "Q5\nstärkste"],
    )
    run_eda(data)
    group_tests = run_group_comparison(data)
    regression = run_regressions(data)
    data["cluster"] = run_clustering(data)
    moran = run_morans_i(data, regression["residuals"])
    export_choropleths(data)
    export_cluster_map(data)
    plot_final_result(data, regression, group_tests, moran)
    save_merged(data)

    print("\nFertig! Ergebnisse liegen im Ordner 'outputs/'.")
    print("Wissenschaftlicher Hinweis: Ergebnisse sind Zusammenhänge auf Gebietsebene,")
    print("keine Aussagen über einzelne Personen und kein Kausalitätsnachweis.")


if __name__ == "__main__":
    main()
