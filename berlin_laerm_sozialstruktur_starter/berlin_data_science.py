"""
DATA SCIENCE: Lärm, soziale Lage und Angebotsmieten in Berlin (vereinfachte Version)
====================================================================================

Leitfrage:
Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von
Lärm betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

Räumliche Einheit: 542 LOR-Planungsräume (PLR). Alle Aussagen gelten für Gebiete,
nicht für Personen. Korrelation ist keine Kausalität.

Methoden (am Vorlesungsstoff orientiert):
1. Standardisierung und PCA -> Benachteiligungsindex
2. Deskriptive Statistik und ANOVA (Hypothesentest)
3. Multiple lineare Regression (mit räumlich geclusterten Standardfehlern)
4. K-Means-Clustering (Elbow-Methode)
5. Moran's I als Prüfung der räumlichen Abhängigkeit
6. Karten und Ergebnisgrafik

Quellen:
MSS 2025 Index-Tabellen (Tabelle 1, 2.1 und 3):
https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/
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
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

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

# MSS 2025. Die Tabellen werden über die achtstellige PLR-ID erkannt, nicht über
# feste Kopfzeilen. Werte = Spaltenposition in der jeweiligen Excel-Tabelle.
SOCIAL_STATUS_FILE = RAW / "sozialdaten.xlsx"                            # Tabelle 1
SOCIAL_INDICATOR_FILE = RAW / "mss2025_indexindikatoren_anteile_plr.xlsx"  # Tabelle 2.1
SOCIAL_ZVALUE_FILE = RAW / "mss2025_indexindikatoren_zwerte_plr.xlsx"      # Tabelle 3
SOCIAL_INDICATOR_COLUMNS = {
    "arbeitslosenanteil_prozent": 3,    # S1: Arbeitslose nach SGB II
    "alleinerziehende_prozent": 4,      # S2: Kinder in alleinerziehenden Haushalten
    "transferbezugsanteil_prozent": 5,  # S3: Transferbezug SGB II und XII
    "kinderarmut_prozent": 6,           # S4: Kinder unter 15 in SGB-II-Bedarfsgemeinschaften
}
SOCIAL_INDICATORS = list(SOCIAL_INDICATOR_COLUMNS)

# Mietdaten: IBB-Tabelle mit Planungsraum-ID (Spalte 1), Median (4) und Fallzahl (6).
RENT_FILE = RAW / "Mietdaten.xlsx"
RENT_SHEET = "Planungsräume_2025"

# Lärmdaten: aggregierte Fassadenpegel aus aggregate_noise.py
NOISE_CSV = PROCESSED / "laermdaten_aggregiert.csv"
NOISE_COLUMNS = ["laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent"]

# Kontrollvariablen der multiplen Regression
CONTROL_VARIABLES = ["log_einwohnerdichte", "innere_stadt"]

# Räumliche Korrektur der Standardfehler: Planungsräume desselben Prognoseraums
# (58 Gruppen) werden als ein "Cluster" behandelt, weil Nachbarn sich ähneln.
CLUSTER_SE_COLUMN = "pgr_id"

# IBB-Angebotsmieten mit sehr wenigen Inseraten sind instabil (IBB-Grenze: 21).
MIN_RENT_LISTINGS = 21

# K-Means: k=4 ergibt eine interpretierbare Typologie laut/leise x benachteiligt/
# wohlhabend; die Elbow-Kurve zeigt ab k=4 nur noch geringe Verbesserungen.
N_CLUSTERS = 4
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
    "laerm_gesamt_lden_db": "Gesamtlärm LDEN [dB(A)]",
    "anteil_fassaden_lden_ueber_65_prozent": "Fassaden > 65 dB(A) LDEN [%]",
    "arbeitslosenanteil_prozent": "S1 Arbeitslosigkeit [%]",
    "alleinerziehende_prozent": "S2 Alleinerziehende [%]",
    "transferbezugsanteil_prozent": "S3 Transferbezug [%]",
    "kinderarmut_prozent": "S4 Kinderarmut [%]",
    "benachteiligungsindex": "Benachteiligungsindex (PC1, z)",
    "angebotsmiete_median_eur_m2": "Median-Angebotsmiete [EUR/m²]",
    "einwohnerdichte": "Einwohnerdichte [EW/km²]",
    "log_einwohnerdichte": "log(1 + Einwohnerdichte)",
    "innere_stadt": "Innere Stadt (0/1)",
}


def label(col: str) -> str:
    return DEUTSCHE_BESCHRIFTUNG.get(col, col)


def p_text(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


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


def save_figure(fig, name: str, dpi: int = 170) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=dpi)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. DATENIMPORT UND ZUSAMMENFÜHRUNG
# ---------------------------------------------------------------------------

def load_boundaries() -> gpd.GeoDataFrame:
    if not BOUNDARIES_FILE.exists():
        raise FileNotFoundError(f"Planungsraum-Daten fehlen: {BOUNDARIES_FILE}")
    gdf = gpd.read_file(BOUNDARIES_FILE)
    if gdf.crs is None:
        raise ValueError("Die Planungsraum-Geodaten haben kein CRS. Koordinatensystem klären!")
    gdf["plr_id"] = normalize_plr_id(gdf["plr_id"])
    return gdf[BOUNDARY_COLUMNS].drop_duplicates("plr_id")


def load_social() -> pd.DataFrame:
    """MSS 2025: Einwohner (Tab. 1), Indikatoren S1-S4 (Tab. 2.1), amtlicher Status-Index (Tab. 3)."""
    status = read_plr_rows(SOCIAL_STATUS_FILE, 0, 0)
    social = pd.DataFrame({"plr_id": status[0], "einwohner": to_number(status[2])})

    indicator_rows = read_plr_rows(SOCIAL_INDICATOR_FILE, 0, 0)
    indicators = pd.DataFrame({"plr_id": indicator_rows[0]})
    for name, position in SOCIAL_INDICATOR_COLUMNS.items():
        indicators[name] = to_number(indicator_rows[position])

    zvalue_rows = read_plr_rows(SOCIAL_ZVALUE_FILE, 0, 0)
    official = pd.DataFrame({"plr_id": zvalue_rows[0], "mss_statusindex": to_number(zvalue_rows[8])})

    social = social.merge(indicators, on="plr_id", how="left", validate="one_to_one")
    return social.merge(official, on="plr_id", how="left", validate="one_to_one")


def load_rents() -> pd.DataFrame:
    """Liest IBB-Planungsraummieten (Median und Zahl der Inserate)."""
    rows = read_plr_rows(RENT_FILE, RENT_SHEET, 1)
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
    return noise[["plr_id", *NOISE_COLUMNS]]


def load_all_data() -> gpd.GeoDataFrame:
    print("\n[1] Lade Planungsräume, MSS-, Miet- und Lärmdaten ...")
    data = load_boundaries()
    for table in (load_social(), load_rents(), load_noise()):
        data = data.merge(table, on="plr_id", how="left", validate="one_to_one")

    # Namensabgleich: deckt vertauschte oder abweichende Zuordnungen in der IBB-Tabelle auf.
    name_check = data.loc[
        data["plr_name_ibb"].notna() & (data["plr_name"] != data["plr_name_ibb"]),
        ["plr_id", "plr_name", "plr_name_ibb"],
    ]
    name_check.to_csv(OUT / "pruefung_namensabweichungen_ibb.csv", index=False)

    # Abgeleitete Variablen
    data["einwohnerdichte"] = data["einwohner"] / (data.geometry.area / 1e6)
    data["log_einwohnerdichte"] = np.log1p(data["einwohnerdichte"])
    data["innere_stadt"] = (data["stadtraum_name"] == "Innere Stadt").astype(int)

    # Angebotsmieten mit zu geringer Fallzahl aus der Analyse nehmen (nicht imputieren).
    data["angebotsmiete_median_eur_m2"] = data["angebotsmiete_median_roh"].where(
        data["anzahl_mietinserate"] >= MIN_RENT_LISTINGS
    )

    quality_cols = [c for c in data.columns if c not in ("geometry", "plr_id", "plr_name", "plr_name_ibb")]
    quality = pd.DataFrame({"gueltig": data[quality_cols].notna().sum(), "fehlend": data[quality_cols].isna().sum()})
    quality.to_csv(OUT / "datenqualitaet.csv")
    print(f"Planungsräume: {len(data)}, mit Sozialdaten: {data['kinderarmut_prozent'].notna().sum()}, "
          f"mit Mietwert: {data['angebotsmiete_median_eur_m2'].notna().sum()}, IBB-Namensabweichungen: {len(name_check)}")
    return data


def save_merged(data: gpd.GeoDataFrame) -> None:
    out = data.copy()
    out["deprivationsquintil"] = out["deprivationsquintil"].astype("string")
    out.to_file(PROCESSED / "berlin_merged.gpkg", driver="GPKG")
    out.drop(columns="geometry").to_csv(PROCESSED / "berlin_merged.csv", index=False)


# ---------------------------------------------------------------------------
# 4. PCA: BENACHTEILIGUNGSINDEX AUS DEN MSS-STATUS-INDIKATOREN
# ---------------------------------------------------------------------------

def run_pca_benachteiligungsindex(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Standardisierung + PCA über S1-S4; PC1 wird der Benachteiligungsindex."""
    print("\n[2] PCA: Benachteiligungsindex aus S1-S4 ...")
    X = df[SOCIAL_INDICATORS].dropna()
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA()
    components = pca.fit_transform(X_scaled)
    names = [f"PC{i + 1}" for i in range(len(SOCIAL_INDICATORS))]

    pd.DataFrame({
        "component": names,
        "eigenvalue": pca.explained_variance_,
        "explained_variance_ratio": pca.explained_variance_ratio_,
    }).to_csv(OUT / "pca_explained_variance.csv", index=False)

    # Ladungen = Korrelation zwischen Indikator und Komponente
    loadings = pd.DataFrame(pca.components_.T * np.sqrt(pca.explained_variance_), index=SOCIAL_INDICATORS, columns=names)
    # Vorzeichen so festlegen, dass höhere Werte stärkere Benachteiligung bedeuten.
    sign = np.sign(loadings["PC1"].sum())
    loadings["PC1"] *= sign
    loadings.to_csv(OUT / "pca_loadings.csv")
    pc1 = sign * components[:, 0]

    df = df.copy()
    df.loc[X.index, "benachteiligungsindex"] = (pc1 - pc1.mean()) / pc1.std(ddof=1)

    valid = df[["benachteiligungsindex", "mss_statusindex"]].dropna()
    r_official = np.corrcoef(valid["benachteiligungsindex"], valid["mss_statusindex"])[0, 1]
    report = (
        f"PCA über {len(SOCIAL_INDICATORS)} MSS-Status-Indikatoren, n = {len(X)} Planungsräume\n"
        f"Eigenwerte: {np.round(pca.explained_variance_, 3).tolist()}\n"
        f"Erklärte Varianz PC1: {pca.explained_variance_ratio_[0]:.1%}\n\n"
        f"Ladungen PC1:\n{loadings['PC1'].round(3).to_string()}\n\n"
        f"Übereinstimmung mit dem amtlichen MSS-Status-Index: r = {r_official:.3f}\n"
        "Der Index ist z-standardisiert (Mittelwert 0, SD 1); höhere Werte = stärkere Benachteiligung.\n"
    )
    (OUT / "pca_bericht.txt").write_text(report, encoding="utf-8")
    print(report)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].bar(names, pca.explained_variance_ratio_ * 100, color="steelblue")
    axes[0].set_title("Scree-Plot")
    axes[0].set_ylabel("Erklärte Varianz [%]")
    loadings["PC1"].rename(index=label).sort_values().plot.barh(ax=axes[1], color="darkorange")
    axes[1].set_title(f"Ladungen PC1 ({pca.explained_variance_ratio_[0]:.1%} erklärte Varianz)")
    axes[1].set_xlim(0, 1)
    save_figure(fig, "pca_scree_ladungen.png")
    return df


# ---------------------------------------------------------------------------
# 5. DESKRIPTIVE STATISTIK UND ANOVA
# ---------------------------------------------------------------------------

EDA_COLUMNS = [
    "laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent", "benachteiligungsindex",
    *SOCIAL_INDICATORS, "angebotsmiete_median_eur_m2", "einwohnerdichte",
]


def run_descriptive(df: gpd.GeoDataFrame) -> None:
    print("\n[3] Deskriptive Statistik ...")
    summary = df[EDA_COLUMNS].describe().T
    summary["variance"] = df[EDA_COLUMNS].var()
    summary.to_csv(OUT / "descriptive_statistics.csv")
    print(summary.round(2).to_string())

    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for ax, col in zip(axes.flat, EDA_COLUMNS):
        sns.histplot(df[col].dropna(), kde=True, ax=ax)
        ax.set_title(label(col), fontsize=9)
        ax.set_xlabel("")
    fig.suptitle("Verteilungen der Analysevariablen")
    save_figure(fig, "histogramme.png")

    corr = df[EDA_COLUMNS].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr.rename(index=label, columns=label), annot=True, cmap="vlag", center=0, fmt=".2f", ax=ax)
    ax.set_title("Korrelationsmatrix (Überblick)")
    save_figure(fig, "korrelationsmatrix.png")


def run_anova(df: gpd.GeoDataFrame) -> float:
    """ANOVA: Unterscheidet sich der mittlere Lärm zwischen den Benachteiligungs-Quintilen?

    Anders als die Regression setzt die ANOVA keinen linearen Verlauf voraus.
    """
    print("\n[4] ANOVA: Lärm nach Quintilen des Benachteiligungsindex ...")
    sub = df[["deprivationsquintil", "laerm_gesamt_lden_db"]].dropna()
    groups = [g["laerm_gesamt_lden_db"] for _, g in sub.groupby("deprivationsquintil", observed=True)]
    anova = stats.f_oneway(*groups)
    profile = sub.groupby("deprivationsquintil", observed=True)["laerm_gesamt_lden_db"].agg(["count", "mean", "median", "std"])
    profile.to_csv(OUT / "anova_profile.csv")
    (OUT / "anova_ergebnis.txt").write_text(
        f"ANOVA Lärm (LDEN) ~ Quintil des Benachteiligungsindex\nF = {anova.statistic:.3f}, {p_text(anova.pvalue)}\n\n"
        f"{profile.round(2).to_string()}\n", encoding="utf-8")
    print(f"F = {anova.statistic:.2f}, {p_text(anova.pvalue)}")
    print(profile.round(2).to_string())
    return anova.pvalue


# ---------------------------------------------------------------------------
# 6. MULTIPLE LINEARE REGRESSION
# ---------------------------------------------------------------------------

def run_regressions(df: gpd.GeoDataFrame) -> dict:
    """A1: Lärm ~ Benachteiligung. A2: zusätzlich Dichte und Lage. B: Miete ~ Lärm + Benachteiligung + Kontrollen.

    Jedes Modell wird zweimal geschätzt: mit klassischen OLS-Standardfehlern und mit
    nach Prognoseraum geclusterten Standardfehlern. Die Koeffizienten sind identisch,
    nur die Unsicherheit (Standardfehler, p-Wert) unterscheidet sich. Für die
    Interpretation sind die geclusterten Werte maßgeblich.
    """
    print("\n[5] Multiple lineare Regression ...")
    noise, rent, index = "laerm_gesamt_lden_db", "angebotsmiete_median_eur_m2", "benachteiligungsindex"
    specs = {
        "A1_laerm_einfach": (noise, [index]),
        "A2_laerm_kontrollen": (noise, [index, *CONTROL_VARIABLES]),
        "B_miete": (rent, [noise, index, *CONTROL_VARIABLES]),
    }
    models, rows = {"ols": {}, "cluster": {}}, []
    for name, (target, predictors) in specs.items():
        model_data = df[[target, *predictors, CLUSTER_SE_COLUMN]].dropna()
        y = model_data[target]
        X = sm.add_constant(model_data[predictors].astype(float))
        groups = pd.factorize(model_data[CLUSTER_SE_COLUMN])[0]
        ols = sm.OLS(y, X).fit()
        clustered = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        models["ols"][name], models["cluster"][name] = ols, clustered
        (OUT / f"regression_{name}.txt").write_text(
            "STANDARDFEHLER NACH PROGNOSERAUM GECLUSTERT (maßgeblich)\n"
            f"{clustered.summary().as_text()}\n\n\n"
            "KLASSISCHE OLS-STANDARDFEHLER (zum Vergleich)\n"
            f"{ols.summary().as_text()}\n", encoding="utf-8")
        rows += [{"modell": name, "zielvariable": target, "term": term, "koeffizient": ols.params[term],
                  "std_fehler_ols": ols.bse[term], "p_wert_ols": ols.pvalues[term],
                  "std_fehler_cluster": clustered.bse[term], "p_wert_cluster": clustered.pvalues[term],
                  "n": int(ols.nobs), "r2": ols.rsquared}
                 for term in predictors]
    overview = pd.DataFrame(rows)
    overview.to_csv(OUT / "regression_uebersicht.csv", index=False)
    print(overview.round(4).to_string(index=False))
    return models


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

    inertia = {k: KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20).fit(X_scaled).inertia_ for k in range(1, 9)}
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(list(inertia), list(inertia.values()), marker="o")
    ax.axvline(N_CLUSTERS, color="grey", linestyle="--", label=f"gewählt: k = {N_CLUSTERS}")
    ax.set_title("Elbow-Methode")
    ax.set_xlabel("Anzahl Cluster k")
    ax.set_ylabel("Inertia (Summe quadrierter Abstände)")
    ax.legend()
    save_figure(fig, "kmeans_elbow.png", dpi=160)

    raw_labels = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=20).fit_predict(X_scaled)
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
    df.loc[X.index, ["plr_id", "plr_name"]].assign(cluster=clusters).to_csv(OUT / "kmeans_clusters.csv", index=False)
    return clusters


# ---------------------------------------------------------------------------
# 8. RÄUMLICHE ABHÄNGIGKEIT: MORAN'S I
# ---------------------------------------------------------------------------

def run_morans_i(gdf: gpd.GeoDataFrame, models: dict) -> pd.DataFrame:
    """Moran's I: Ähneln sich benachbarte Planungsräume stärker als zufällig?

    Für die Regressionsresiduen bedeutet ein hohes I, dass die Beobachtungen nicht
    unabhängig sind; klassische p-Werte wären dann zu optimistisch. Deshalb nutzt
    run_regressions() zusätzlich geclusterte Standardfehler.
    """
    print("\n[7] Moran's I ...")
    if not HAS_PYSAL:
        print("Moran's I übersprungen. Installiert libpysal und esda.")
        return pd.DataFrame()
    series = {
        "laerm_gesamt_lden_db": gdf["laerm_gesamt_lden_db"],
        "benachteiligungsindex": gdf["benachteiligungsindex"],
        "residuen_A1": models["ols"]["A1_laerm_einfach"].resid,
        "residuen_A2": models["ols"]["A2_laerm_kontrollen"].resid,
    }
    rows = []
    for name, values in series.items():
        values = values.dropna()
        # Queen-Nachbarschaft: Planungsräume mit gemeinsamer Grenze oder Ecke sind Nachbarn.
        weights = Queen.from_dataframe(gdf.loc[values.index, ["geometry"]], use_index=False)
        weights.transform = "r"
        np.random.seed(RANDOM_STATE)
        mi = Moran(values.values, weights, permutations=MORAN_PERMUTATIONS)
        rows.append({"variable": name, "n": len(values), "I": mi.I, "p_sim": mi.p_sim})
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "morans_i.csv", index=False)
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


def export_maps(gdf: gpd.GeoDataFrame) -> None:
    for col, cmap in (("laerm_gesamt_lden_db", "magma_r"), ("benachteiligungsindex", "viridis"),
                      ("angebotsmiete_median_eur_m2", "viridis")):
        fig, ax = plt.subplots(figsize=(10, 8.5))
        gdf.plot(column=col, cmap=cmap, legend=True, edgecolor="white", linewidth=0.15, ax=ax,
                 legend_kwds={"shrink": 0.6, "label": label(col)},
                 missing_kwds={"color": "lightgrey", "label": "Keine Daten"})
        draw_districts(ax, gdf)
        ax.set_title(f"Berlin nach Planungsräumen: {label(col)}")
        ax.set_axis_off()
        save_figure(fig, f"map_{col}.png", dpi=180)

    names = sorted(gdf["cluster"].dropna().unique())
    palette = dict(zip(names, sns.color_palette("Set2", len(names))))
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf[gdf["cluster"].isna()].plot(ax=ax, color="#e0e0e0", edgecolor="white", linewidth=0.15)
    for name in names:
        gdf[gdf["cluster"] == name].plot(ax=ax, color=palette[name], edgecolor="white", linewidth=0.15)
    draw_districts(ax, gdf, labels=True)
    counts = gdf["cluster"].value_counts()
    handles = [plt.Rectangle((0, 0), 1, 1, color=palette[n]) for n in names] + [plt.Rectangle((0, 0), 1, 1, color="#e0e0e0")]
    legend_labels = [f"{n} (n = {counts[n]})" for n in names]
    legend_labels.append(f"Nicht geclustert: Miete oder Sozialdaten fehlen (n = {gdf['cluster'].isna().sum()})")
    ax.legend(handles, legend_labels, loc="lower left", fontsize=8, title="Gebietstypen (K-Means)", title_fontsize=9)
    ax.set_title("Berlin: Gebietstypen nach Lärm, sozialer Benachteiligung und Angebotsmiete", fontsize=13)
    ax.set_axis_off()
    save_figure(fig, "map_kmeans_cluster.png", dpi=200)


def build_conclusion(df: gpd.GeoDataFrame, models: dict, anova_p: float, moran: pd.DataFrame) -> list[str]:
    """Formuliert die Antwort auf die Leitfrage regelbasiert aus den berechneten Kennzahlen."""
    index, noise = "benachteiligungsindex", "laerm_gesamt_lden_db"
    a1, a2, b = (models["cluster"][name] for name in ("A1_laerm_einfach", "A2_laerm_kontrollen", "B_miete"))
    a1_ols, a2_ols = models["ols"]["A1_laerm_einfach"], models["ols"]["A2_laerm_kontrollen"]
    quintile_means = df.groupby("deprivationsquintil", observed=True)[noise].mean()
    q1_gap = quintile_means.iloc[1:].mean() - quintile_means.iloc[0]
    upper_range = quintile_means.iloc[1:].max() - quintile_means.iloc[1:].min()
    clusters = df["cluster"].dropna()
    loud_deprived = clusters[clusters.str.contains("Lärm hoch · Benachteiligung hoch", regex=False)]

    if a2.pvalues[index] < SIGNIFICANCE_LEVEL and a2.params[index] > 0:
        h1 = "H1 gestützt: Mehr Benachteiligung geht auch mit Kontrollvariablen mit mehr Lärm einher."
    else:
        h1 = "H1 nicht gestützt: Kein signifikanter linearer Zusammenhang zwischen Benachteiligung und Lärm."
    lines = [
        h1,
        f"A1: {a1.params[index]:+.2f} dB pro SD Benachteiligung, R² = {a1.rsquared:.3f}, {p_text(a1.pvalues[index])} "
        f"(räumlich korrigiert; ohne Korrektur {p_text(a1_ols.pvalues[index])}). "
        f"A2 (mit Dichte und Lage): {a2.params[index]:+.2f} dB, {p_text(a2.pvalues[index])} "
        f"(ohne Korrektur {p_text(a2_ols.pvalues[index])}).",
        "Mittlerer Lärm je Quintil: " + " | ".join(f"{v:.1f}" for v in quintile_means.values)
        + f" dB (Q1→Q5), ANOVA {p_text(anova_p)}. Die am wenigsten benachteiligten Gebiete (Q1) sind "
        f"{q1_gap:.1f} dB leiser; zwischen Q2 und Q5 liegen nur {upper_range:.1f} dB → kein Gradient "
        "'je benachteiligter, desto lauter'.",
        f"H2: Miete steigt um {b.params[noise]:+.2f} EUR/m² pro dB ({p_text(b.pvalues[noise])}) und sinkt um "
        f"{-b.params[index]:.2f} EUR/m² pro SD Benachteiligung ({p_text(b.pvalues[index])}) – Lageeffekt, keine Kausalität.",
        f"H3: {clusters.nunique()} Gebietstypen; {len(loud_deprived)} von {len(clusters)} PLR "
        f"({len(loud_deprived) / len(clusters):.0%}) sind zugleich laut und benachteiligt (Mehrfachbelastung).",
    ]
    if not moran.empty:
        mi = moran.set_index("variable")["I"]
        lines.append(f"Räumlich: Lärm I = {mi['laerm_gesamt_lden_db']:.2f}, Residuen A2 I = {mi['residuen_A2']:.2f} "
                     "→ benachbarte Gebiete ähneln sich. Deshalb werden die Standardfehler nach "
                     "Prognoseraum geclustert; alle p-Werte oben sind räumlich korrigiert.")
    return lines


def plot_final_result(df: gpd.GeoDataFrame, models: dict, anova_p: float, moran: pd.DataFrame) -> None:
    conclusion = build_conclusion(df, models, anova_p, moran)
    (OUT / "ergebnis_zusammenfassung.txt").write_text("\n".join(conclusion) + "\n", encoding="utf-8")
    print("\nERGEBNIS ZUR LEITFRAGE:\n" + "\n".join(f"- {line}" for line in conclusion))

    noise, index = "laerm_gesamt_lden_db", "benachteiligungsindex"
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    sub = df[["deprivationsquintil", noise]].dropna()
    sns.boxplot(data=sub, x="deprivationsquintil", y=noise, color="lightsteelblue", showfliers=False, ax=axes[0, 0])
    means = sub.groupby("deprivationsquintil", observed=True)[noise].mean()
    axes[0, 0].plot(range(len(means)), means.values, color="crimson", marker="o", lw=2, label="Mittelwert")
    axes[0, 0].legend()
    axes[0, 0].set_title(f"A  Lärm nach sozialer Benachteiligung (ANOVA {p_text(anova_p)})")
    axes[0, 0].set_xlabel("Quintile des Benachteiligungsindex")
    axes[0, 0].set_ylabel(label(noise))

    share = "anteil_fassaden_lden_ueber_65_prozent"
    sns.barplot(data=df, x="deprivationsquintil", y=share, color="darkorange", errorbar=None, ax=axes[0, 1])
    axes[0, 1].set_title("B  Mittlerer Anteil Fassaden über 65 dB(A) LDEN")
    axes[0, 1].set_xlabel("Quintile des Benachteiligungsindex")
    axes[0, 1].set_ylabel(label(share))
    for ax in axes[0]:
        ax.tick_params(axis="x", labelsize=8)

    a1, a2 = models["cluster"]["A1_laerm_einfach"], models["cluster"]["A2_laerm_kontrollen"]
    pair = df[[index, noise]].dropna()
    axes[1, 0].scatter(pair[index], pair[noise], alpha=0.4, s=12, color="steelblue")
    x_line = np.linspace(pair[index].min(), pair[index].max(), 50)
    axes[1, 0].plot(x_line, a1.params["const"] + a1.params[index] * x_line, color="crimson", lw=2,
                    label=f"A1: b = {a1.params[index]:+.2f} dB, {p_text(a1.pvalues[index])}")
    axes[1, 0].plot([], [], " ", label=f"A2 (mit Kontrollen): b = {a2.params[index]:+.2f} dB, {p_text(a2.pvalues[index])}")
    axes[1, 0].legend(fontsize=9, title="p-Werte räumlich korrigiert", title_fontsize=8)
    axes[1, 0].set_title("C  Regression: Lärm ~ Benachteiligung")
    axes[1, 0].set_xlabel(label(index))
    axes[1, 0].set_ylabel(label(noise))

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
    for folder in (RAW, PROCESSED, OUT):
        folder.mkdir(parents=True, exist_ok=True)
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
    run_descriptive(data)
    anova_p = run_anova(data)
    models = run_regressions(data)
    data["cluster"] = run_clustering(data)
    moran = run_morans_i(data, models)
    export_maps(data)
    plot_final_result(data, models, anova_p, moran)
    save_merged(data)

    print("\nFertig! Ergebnisse liegen im Ordner 'outputs/'.")
    print("Wissenschaftlicher Hinweis: Ergebnisse sind Zusammenhänge auf Gebietsebene,")
    print("keine Aussagen über einzelne Personen und kein Kausalitätsnachweis.")


if __name__ == "__main__":
    main()
