"""
DATA-SCIENCE-STARTER: Lärm, soziale Lage und Angebotsmieten in Berlin
======================================================================

WICHTIG:
- Dieses Skript enthält die Analysepipeline, aber NICHT die kompletten amtlichen
  Rohdaten. Die amtlichen Geodaten sind teils groß und werden separat heruntergeladen.
- Legt die Dateien unter data/raw/ ab und passt unten die Dateinamen sowie ggf.
  die Spaltenzuordnung an.
- Alle Analysen sind zunächst explorativ. Korrelation ist keine Kausalität.

Empfohlene räumliche Einheit: Berliner LOR-Planungsräume (PLR).
Achtet darauf, dass alle Datensätze dieselbe LOR-Gebietsabgrenzung verwenden.
Das MSS 2025 nutzt LOR-Grenzen mit Stand 01/2023.

Quellen (Downloadseiten):
MSS 2025 Index-Tabellen:
https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/
MSS 2025 Kontext-Tabellen:
https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-kontext-indikatoren-zum-bericht-2025/
Lärmkarten Berlin 2022:
https://www.berlin.de/umweltatlas/verkehr-laerm/laermbelastung/2022/download/
Technische Beschreibung Lärm-WFS:
https://fbinter.stadt-berlin.de/fb_daten/beschreibung/umweltatlas/datenformatbeschreibung/Datenformatbeschreibung_Laerm_2022.pdf
IBB Wohnungsmarktbericht 2025:
https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html
IBB Angebotsmieten nach Planungsräumen (Tabelle im Bericht / Tabellenband):
https://www.ibb.de/media/dokumente/publikationen/berliner-wohnungsmarkt/wohnungsmarktbericht/2025/ibb-wohnungsmarktbericht-angebotsmieten_2012-2025.pdf
LOR-Geodaten / Planungsräume:
https://daten.odis-berlin.de/

Datenformat, das dieses Skript nach der Aufbereitung erwartet:
1) planungsraeume.gpkg (Layer mit Polygonen; Attribut mit PLR-ID)
2) sozialdaten.xlsx oder .csv (PLR-ID, Arbeitslosigkeit, Transferbezug, Kinderarmut)
3) mietdaten.xlsx oder .csv (PLR-ID, Median-Angebotsmiete, Zahl der Inserate)
4) laerm_ld_en.tif (optional laerm_ln.tif), Raster mit dB-Werten
   Alternativ kann eine bereits aggregierte laermdaten.csv genutzt werden.

Für die Analyse sollten die Rohdaten zunächst geprüft werden. Dieses Skript druckt
daher die Spaltennamen der Excel-Dateien aus, wenn die automatische Zuordnung noch
nicht konfiguriert ist.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import silhouette_score, classification_report
from sklearn.inspection import permutation_importance

# Optional für Raster-Aggregation und räumliche Statistik:
try:
    from rasterstats import zonal_stats
    HAS_RASTERSTATS = True
except ImportError:
    HAS_RASTERSTATS = False

try:
    from libpysal.weights import Queen
    from esda.moran import Moran, Moran_Local
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
BOUNDARIES_LAYER = None  # z.B. "lor_planungsraeume"; None = Standard-Layer
PLR_ID_GEO = "plr_id"    # ggf. an tatsächlichen Spaltennamen anpassen
PLR_NAME_GEO = "plr_name"  # optional; falls nicht vorhanden, bleibt der Name leer

# Sozialdaten: Excel oder CSV, idealerweise MSS 2025 auf PLR-Ebene.
SOCIAL_FILE = RAW / "sozialdaten.xlsx"
SOCIAL_SHEET = "1.SDI_PLR_MSS2025"
SOCIAL_HEADER_ROW = 5
# Links/Rechts: Standardname im Skript -> tatsächlicher Name in eurer Quelldatei.
# Erst SOCIAL_FILE herunterladen, dann Excel-Spaltennamen prüfen und hier eintragen.
SOCIAL_COLUMN_MAP = {
    "plr_id": "PLR_ID",
    "arbeitslosenanteil_prozent": "Arbeitslosigkeit",  # Anteil Arbeitslosigkeit in Prozent
    "transferbezugsanteil_prozent": "Transferbezug",         # Anteil Transferbezug in Prozent
    "kinderarmut_prozent": "Kinderarmut",      # Anteil Kinderarmut in Prozent
    # Optional:
    # "low_income_employment_pct": "K20",
}

# Mietdaten: IBB-Tabelle mit Planungsraum-ID, Median und Fallzahl.
RENT_FILE = RAW / "mietdaten.xlsx"
RENT_SHEET = "Planungsräume_2025"
RENT_HEADER_ROW = 9
RENT_COLUMN_MAP = {
    "plr_id": "PLR_ID",
    "angebotsmiete_median_eur_m2": "Median 2025",
    "anzahl_mietinserate": "Fallzahlen",
}

# Lärmdaten:
# Variante A (empfohlen): bereits aggregierte CSV mit PLR_ID und laerm_gesamt_lden_db.
NOISE_CSV = PROCESSED / "laermdaten_aggregiert.csv"
NOISE_CSV_COLUMN_MAP = {
    "plr_id": "plr_id",
    "laerm_gesamt_lden_db": "laerm_gesamt_lden_db",
    # Wenn eure CSV auch eine Nachtlärm-Spalte enthält, ergänzt:
    # "laerm_gesamt_ln_db": "L_N",
}
# Variante B: Lärmraster (GeoTIFF). Falls vorhanden, wird es pro PLR aggregiert.
NOISE_LDEN_TIF = RAW / "laerm_ld_en.tif"
NOISE_LN_TIF = RAW / "laerm_ln.tif"

# Weitere Kontrollvariablen können später ergänzt werden.
# Wichtig: Nicht blind alle verfügbaren Variablen in ein Modell aufnehmen.
CONTROL_VARIABLES = ["population_density", "green_space_pct"]

# IBB-Angebotsmieten mit sehr wenigen Inseraten sind instabil.
MIN_RENT_LISTINGS = 21

# Reproduzierbarkeit
RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 2. HILFSFUNKTIONEN
# ---------------------------------------------------------------------------

def ensure_dirs() -> None:
    for folder in (RAW, PROCESSED, OUT):
        folder.mkdir(parents=True, exist_ok=True)


def normalize_plr_id(series: pd.Series) -> pd.Series:
    """PLR-ID als achtstellige Zeichenkette vereinheitlichen."""
    s = series.astype("string").str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    return s.str.zfill(8)


def read_table(path: Path, sheet=0, header=None) -> pd.DataFrame:
    """Liest CSV oder Excel und zeigt bei Bedarf die Spaltennamen."""
    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet, header=header)
    elif suffix == ".csv":
        # sep=None erkennt häufig Komma/Semikolon automatisch.
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    else:
        raise ValueError(f"Nicht unterstütztes Tabellenformat: {suffix}")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def mapped_table(
    path: Path,
    sheet,
    column_map: dict,
    dataset_name: str,
    header=None,
) -> pd.DataFrame:
    """Wählt Spalten anhand der oben definierten Zuordnung aus."""
    raw = read_table(path, sheet, header=header)
    missing = [source for source in column_map.values() if source not in raw.columns]
    if missing:
        print(f"\n[SPALTEN-CHECK] {dataset_name}:")
        print("Gefundene Spalten:")
        print(list(raw.columns))
        raise KeyError(
            f"Diese Quellspalten fehlen: {missing}\n"
            f"Bitte {dataset_name.upper()}_COLUMN_MAP oben anpassen."
        )
    df = raw[list(column_map.values())].copy()
    df.columns = list(column_map.keys())
    df["plr_id"] = normalize_plr_id(df["plr_id"])
    for col in df.columns:
        if col != "plr_id":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_social_status() -> pd.DataFrame:
    """Liest den MSS-Gesamtstatus aus der vorbereiteten Excel-Tabelle."""
    raw = read_table(
        SOCIAL_FILE,
        SOCIAL_SHEET,
        header=SOCIAL_HEADER_ROW,
    )
    if raw.shape[1] < 8:
        raise KeyError("MSS-Tabelle hat weniger als die erwarteten 8 Spalten.")

    social = pd.DataFrame({
        "plr_id": normalize_plr_id(raw.iloc[:, 0]),
        "sozialstatus_index": pd.to_numeric(raw.iloc[:, 3], errors="coerce"),
        "sozialstatus_kategorie": raw.iloc[:, 4].astype("string").str.strip(),
        "sozialdynamik_kategorie": raw.iloc[:, 6].astype("string").str.strip(),
    })

    # Reihenfolge von "hoch" zu "sehr niedrig" als ordinalen Deprivationsscore.
    deprivation_map = {
        "hoch": 1.0,
        "mittel": 2.0,
        "niedrig": 3.0,
        "sehr niedrig": 4.0,
    }
    social["benachteiligungsindex"] = (
        social["sozialstatus_kategorie"].str.lower().map(deprivation_map)
    )
    return social.dropna(subset=["plr_id"]).drop_duplicates("plr_id")


def load_rents() -> pd.DataFrame:
    """Liest IBB-Planungsraummieten aus dem Blatt Planungsräume_2025."""
    raw = read_table(
        RENT_FILE,
        RENT_SHEET,
        header=RENT_HEADER_ROW,
    )
    if raw.shape[1] < 7:
        raise KeyError("Miettabelle hat weniger als die erwarteten 7 Spalten.")

    rents = pd.DataFrame({
        "plr_id": normalize_plr_id(raw.iloc[:, 1]),
        "angebotsmiete_median_eur_m2": pd.to_numeric(raw.iloc[:, 4], errors="coerce"),
        "anzahl_mietinserate": pd.to_numeric(raw.iloc[:, 6], errors="coerce"),
    })
    return rents.dropna(subset=["plr_id"]).drop_duplicates("plr_id")


def load_boundaries() -> gpd.GeoDataFrame:
    if not BOUNDARIES_FILE.exists():
        raise FileNotFoundError(
            f"Planungsraum-Daten fehlen: {BOUNDARIES_FILE}\n"
            "Bitte LOR-Planungsräume herunterladen und ablegen."
        )

    suffix = BOUNDARIES_FILE.suffix.lower()

    # CSV ohne Geometrie -> DataFrame ohne räumliche Funktionen
    if suffix == ".csv":
        df = pd.read_csv(BOUNDARIES_FILE)
        if PLR_ID_GEO not in df.columns:
            raise KeyError(f"PLR-ID-Spalte '{PLR_ID_GEO}' nicht gefunden. Vorhanden: {list(df.columns)}")
        df = df.copy()
        df["plr_id"] = normalize_plr_id(df[PLR_ID_GEO])
        if PLR_NAME_GEO in df.columns:
            df["plr_name"] = df[PLR_NAME_GEO].astype(str)
        else:
            df["plr_name"] = df["plr_id"]
        print("WARNUNG: CSV ohne Geometrie geladen. Räumliche Analysen (Karten, Moran's I) nicht möglich.")
        # Als GeoDataFrame ohne Geometrie zurückgeben (für andere Funktionen)
        gdf = gpd.GeoDataFrame(df, geometry=None)
        return gdf[["plr_id", "plr_name"]].drop_duplicates("plr_id")

    # Geodaten mit Geometrie
    if BOUNDARIES_LAYER:
        gdf = gpd.read_file(BOUNDARIES_FILE, layer=BOUNDARIES_LAYER)
    else:
        gdf = gpd.read_file(BOUNDARIES_FILE)
    if PLR_ID_GEO not in gdf.columns:
        raise KeyError(f"PLR-ID-Spalte '{PLR_ID_GEO}' nicht gefunden. Vorhanden: {list(gdf.columns)}")
    gdf = gdf.copy()
    gdf["plr_id"] = normalize_plr_id(gdf[PLR_ID_GEO])
    if PLR_NAME_GEO in gdf.columns:
        gdf["plr_name"] = gdf[PLR_NAME_GEO].astype(str)
    else:
        gdf["plr_name"] = gdf["plr_id"]
    if gdf.crs is None:
        raise ValueError("Die Planungsraum-Geodaten haben kein CRS. Koordinatensystem klären!")
    return gdf[["plr_id", "plr_name", "geometry"]].drop_duplicates("plr_id")


def aggregate_noise_raster(gdf: gpd.GeoDataFrame, raster_path: Path, output_column: str) -> pd.DataFrame:
    """Aggregiert ein Lärmraster pro Planungsraum (Zonal Mean).

    Der einfache Flächenmittelwert ist NICHT bevölkerungsgewichtet. Für eine
    bessere Expositionsmessung wären Fassadenpegel oder Bevölkerungsraster
    geeigneter. Raster und Polygone müssen räumlich korrekt referenziert sein.
    """
    if not HAS_RASTERSTATS:
        raise ImportError("Für Raster-Aggregation bitte 'rasterstats' installieren.")
    if not raster_path.exists():
        raise FileNotFoundError(raster_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = zonal_stats(
            gdf,
            str(raster_path),
            stats=["mean", "median"],
            nodata=None,
            all_touched=False,
        )
    out = pd.DataFrame({
        "plr_id": gdf["plr_id"].values,
        output_column: [x.get("mean") if x else np.nan for x in result],
    })
    return out


# ---------------------------------------------------------------------------
# 3. DATENIMPORT UND ZUSAMMENFÜHRUNG
# ---------------------------------------------------------------------------

def load_all_data() -> gpd.GeoDataFrame:
    print("\n[1/7] Lade Planungsräume ...")
    areas = load_boundaries()

    print("[2/7] Lade Sozialdaten ...")
    social = load_social_status()

    print("[3/7] Lade Mietdaten ...")
    rents = load_rents()

    print("[4/7] Lade Lärmdaten ...")
    if NOISE_CSV.exists():
        noise = mapped_table(NOISE_CSV, 0, NOISE_CSV_COLUMN_MAP, "Lärmdaten")
    elif NOISE_LDEN_TIF.exists():
        noise = aggregate_noise_raster(areas, NOISE_LDEN_TIF, "laerm_gesamt_lden_db")
        if NOISE_LN_TIF.exists():
            noise_night = aggregate_noise_raster(areas, NOISE_LN_TIF, "laerm_gesamt_ln_db")
            noise = noise.merge(noise_night, on="plr_id", how="left")
    else:
        raise FileNotFoundError(
            "Keine Lärmdaten gefunden. Lege laermdaten.csv oder laerm_ld_en.tif "
            "in data/raw/ ab."
        )

    print("[5/7] Führe Daten über PLR-ID zusammen ...")
    data = areas.merge(social, on="plr_id", how="left", validate="one_to_one")
    data = data.merge(rents, on="plr_id", how="left", validate="one_to_one")
    data = data.merge(noise, on="plr_id", how="left", validate="one_to_one")

    # Datenqualitätsbericht
    print("\nDatenqualität nach dem Join:")
    print(f"Planungsräume: {len(data)}")
    for col in data.columns:
        if col not in ("geometry",):
            print(f"  {col:26s} fehlend: {data[col].isna().sum():4d}")

    # Angebotsmieten mit zu geringer Fallzahl kennzeichnen und aus Hauptanalyse nehmen.
    if "anzahl_mietinserate" in data.columns:
        data.loc[data["anzahl_mietinserate"] < MIN_RENT_LISTINGS, "angebotsmiete_median_eur_m2"] = np.nan

    output = PROCESSED / "berlin_merged.gpkg"
    data.to_file(output, driver="GPKG")
    data.drop(columns="geometry").to_csv(PROCESSED / "berlin_merged.csv", index=False)
    print(f"Zusammengeführter Datensatz gespeichert: {output}")
    return data


# ---------------------------------------------------------------------------
# 4. EDA: DESKRIPTIVE STATISTIK UND VISUALISIERUNGEN
# ---------------------------------------------------------------------------

def get_analysis_columns(df: pd.DataFrame) -> list[str]:
    preferred = [
        "laerm_gesamt_lden_db", "laerm_gesamt_ln_db", "arbeitslosenanteil_prozent",
        "transferbezugsanteil_prozent", "kinderarmut_prozent", "angebotsmiete_median_eur_m2",
        "population_density", "green_space_pct",
    ]
    return [c for c in preferred if c in df.columns and df[c].notna().sum() > 2]


DEUTSCHE_BESCHRIFTUNG = {
    "laerm_gesamt_lden_db": "Gesamt-Lärmbelastung LDEN [dB(A)]",
    "laerm_gesamt_ln_db": "Nacht-Lärmbelastung LN [dB(A)]",
    "arbeitslosenanteil_prozent": "Arbeitslosenanteil [%]",
    "transferbezugsanteil_prozent": "Transferbezugsanteil [%]",
    "kinderarmut_prozent": "Kinderarmut [%]",
    "angebotsmiete_median_eur_m2": "Median-Angebotsmiete [EUR/m²]",
    "benachteiligungsindex": "Soziale Benachteiligung",
    "population_density": "Bevölkerungsdichte",
    "green_space_pct": "Grünflächenanteil [%]",
}


def run_eda(df: gpd.GeoDataFrame) -> None:
    print("\n[6/7] Explorative Datenanalyse ...")
    cols = get_analysis_columns(df)
    if not cols:
        print("Keine numerischen Analysevariablen gefunden.")
        return

    summary = df[cols].describe().T
    summary["variance"] = df[cols].var()
    summary.to_csv(OUT / "descriptive_statistics.csv")
    print("\nDeskriptive Statistik:")
    print(summary.round(3))

    # Histogramme
    for col in cols:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(df[col].dropna(), kde=True, ax=ax)
        ax.set_title(f"Verteilung: {DEUTSCHE_BESCHRIFTUNG.get(col, col)}")
        ax.set_xlabel(DEUTSCHE_BESCHRIFTUNG.get(col, col))
        fig.tight_layout()
        fig.savefig(OUT / f"hist_{col}.png", dpi=160)
        plt.close(fig)

    # Boxplots
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=df[cols], orient="h", ax=ax)
    ax.set_title("Boxplots der Analysevariablen")
    fig.tight_layout()
    fig.savefig(OUT / "boxplots.png", dpi=160)
    plt.close(fig)

    # Korrelationsmatrix
    corr = df[cols].corr(method="pearson")
    corr.to_csv(OUT / "correlation_matrix_pearson.csv")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="vlag", center=0, fmt=".2f", ax=ax)
    ax.set_title("Pearson-Korrelationsmatrix")
    fig.tight_layout()
    fig.savefig(OUT / "correlation_heatmap.png", dpi=180)
    plt.close(fig)

    # Paarweise Pearson-/Spearman-Tests
    pairs = [
        ("benachteiligungsindex", "laerm_gesamt_lden_db"),
        ("arbeitslosenanteil_prozent", "laerm_gesamt_lden_db"),
        ("transferbezugsanteil_prozent", "laerm_gesamt_lden_db"),
        ("kinderarmut_prozent", "laerm_gesamt_lden_db"),
        ("angebotsmiete_median_eur_m2", "laerm_gesamt_lden_db"),
        ("arbeitslosenanteil_prozent", "angebotsmiete_median_eur_m2"),
        ("benachteiligungsindex", "angebotsmiete_median_eur_m2"),
    ]
    rows = []
    for x, y in pairs:
        if x not in df or y not in df:
            continue
        pair = df[[x, y]].dropna()
        if len(pair) < 3:
            continue
        pearson = stats.pearsonr(pair[x], pair[y])
        spearman = stats.spearmanr(pair[x], pair[y])
        rows.append({
            "x": x, "y": y, "n": len(pair),
            "pearson_r": pearson.statistic, "pearson_p": pearson.pvalue,
            "spearman_rho": spearman.statistic, "spearman_p": spearman.pvalue,
        })
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        sns.regplot(
            data=pair,
            x=x,
            y=y,
            lowess=(x != "benachteiligungsindex"),
            scatter_kws={"alpha": 0.55},
            ax=ax,
        )
        ax.set_title(
            f"{DEUTSCHE_BESCHRIFTUNG.get(x, x)} vs. "
            f"{DEUTSCHE_BESCHRIFTUNG.get(y, y)}"
        )
        ax.set_xlabel(DEUTSCHE_BESCHRIFTUNG.get(x, x))
        ax.set_ylabel(DEUTSCHE_BESCHRIFTUNG.get(y, y))
        fig.tight_layout()
        fig.savefig(OUT / f"scatter_{x}_vs_{y}.png", dpi=170)
        plt.close(fig)
    pd.DataFrame(rows).to_csv(OUT / "pairwise_correlations.csv", index=False)


# ---------------------------------------------------------------------------
# 5. REGRESSIONEN
# ---------------------------------------------------------------------------

def fit_regression(df: pd.DataFrame, target: str, predictors: list[str], label: str) -> None:
    available = [c for c in predictors if c in df.columns]
    if target not in df.columns or not available:
        print(f"Regression '{label}' übersprungen: Ziel/Prädiktoren fehlen.")
        return
    model_data = df[[target] + available].replace([np.inf, -np.inf], np.nan).dropna()
    if len(model_data) <= len(available) + 5:
        print(f"Regression '{label}' übersprungen: zu wenige vollständige Fälle ({len(model_data)}).")
        return

    X = sm.add_constant(model_data[available])
    y = model_data[target]
    model = sm.OLS(y, X).fit(cov_type="HC3")  # heteroskedastizitätsrobuste Standardfehler
    with open(OUT / f"regression_{label}.txt", "w", encoding="utf-8") as f:
        f.write(model.summary().as_text())
    pd.DataFrame({
        "coefficient": model.params,
        "std_error_HC3": model.bse,
        "p_value": model.pvalues,
        "ci_lower": model.conf_int()[0],
        "ci_upper": model.conf_int()[1],
    }).to_csv(OUT / f"regression_{label}_coefficients.csv")
    print(f"\nRegression {label}: n={int(model.nobs)}, R²={model.rsquared:.3f}, adj. R²={model.rsquared_adj:.3f}")
    print(model.summary())


def run_regressions(df: pd.DataFrame) -> dict:
    """Regressionen mit Deprivationsindex statt einzelnen sozialen Variablen."""
    print("\n[7/7] Regressionsmodelle ...")

    results = {}

    # Modell A: Lärm erklärt durch Deprivation (Hauptforschungsfrage)
    predictors_noise = ["benachteiligungsindex"]
    if "population_density" in df.columns:
        predictors_noise.append("population_density")
    if "green_space_pct" in df.columns:
        predictors_noise.append("green_space_pct")

    fit_regression(df, "laerm_gesamt_lden_db", predictors_noise, "laerm_erklart")

    # Modell B: Miete erklärt durch Lärm und Deprivation
    predictors_rent = ["laerm_gesamt_lden_db", "benachteiligungsindex"]
    if "population_density" in df.columns:
        predictors_rent.append("population_density")
    if "green_space_pct" in df.columns:
        predictors_rent.append("green_space_pct")

    fit_regression(df, "angebotsmiete_median_eur_m2", predictors_rent, "angebotsmiete_erklart")

    # VIF-Werte prüfen (Multikollinearität)
    if "benachteiligungsindex" in df.columns and "laerm_gesamt_lden_db" in df.columns:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        vif_data = df[["benachteiligungsindex", "laerm_gesamt_lden_db"]].dropna()
        if len(vif_data) > 0:
            vif_df = pd.DataFrame()
            vif_df["feature"] = ["benachteiligungsindex", "laerm_gesamt_lden_db"]
            vif_df["VIF"] = [
                variance_inflation_factor(vif_data.values, i)
                for i in range(len(vif_data.columns))
            ]
            vif_df.to_csv(OUT / "vif_values.csv", index=False)
            print("\nVIF-Werte:")
            print(vif_df.to_string(index=False))

    return results


# ---------------------------------------------------------------------------
# 6. K-MEANS UND PCA
# ---------------------------------------------------------------------------

def run_pca_benachteiligungsindex(df: pd.DataFrame) -> pd.DataFrame:
    """PCA ausschließlich für soziale Indikatoren, um Deprivationsindex zu bilden."""
    social_features = ["arbeitslosenanteil_prozent", "transferbezugsanteil_prozent", "kinderarmut_prozent"]
    social_features = [c for c in social_features if c in df.columns]
    if len(social_features) < 2:
        print("PCA übersprungen: weniger als zwei soziale Indikatoren vorhanden.")
        return df

    X = df[social_features].replace([np.inf, -np.inf], np.nan)
    valid = X.notna().all(axis=1)
    X = X.loc[valid]
    if len(X) < 10:
        print("PCA übersprungen: zu wenige vollständige Beobachtungen.")
        return df

    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    X_scaled = prep.fit_transform(X)

    pca = PCA()
    components = pca.fit_transform(X_scaled)

    # Erklärte Varianz
    explained = pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(len(social_features))],
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "cumulative_variance": np.cumsum(pca.explained_variance_ratio_),
    })
    explained.to_csv(OUT / "pca_explained_variance.csv", index=False)

    # Faktorladungen
    loadings = pd.DataFrame(
        pca.components_.T,
        index=social_features,
        columns=[f"PC{i+1}" for i in range(len(social_features))]
    )
    loadings.to_csv(OUT / "pca_loadings.csv")

    # PC1 als Deprivationsindex übernehmen (sofern positiv korreliert mit Deprivation)
    df_copy = df.copy()
    df_copy.loc[valid, "benachteiligungsindex"] = components[:, 0]

    # Prüfen: positive Ladungen bedeuten höhere Deprivation
    print("\nPCA - Faktorladungen (PC1):")
    print(loadings["PC1"].to_string())
    print(f"\nErklärte Varianz PC1: {pca.explained_variance_ratio_[0]:.1%}")

    # Wenn PC1 negativ mit Deprivation korreliert, invertieren
    pc1_loadings = loadings["PC1"].values
    if np.mean(pc1_loadings) < 0:
        print("PC1-Korrelation invertiert (höhere Werte = stärkere Deprivation)")
        df_copy.loc[valid, "benachteiligungsindex"] = -components[:, 0]

    return df_copy


def run_clustering(df: pd.DataFrame) -> None:
    """K-Means mit Lärm, Deprivationsindex und Mieten."""
    features = ["laerm_gesamt_lden_db", "benachteiligungsindex", "angebotsmiete_median_eur_m2"]
    features = [c for c in features if c in df.columns]
    if len(features) < 2:
        print("Clustering übersprungen: weniger als zwei Features verfügbar.")
        return

    X = df[features].replace([np.inf, -np.inf], np.nan)
    valid = X.notna().all(axis=1)
    X = X.loc[valid]
    if len(X) < 10:
        print("Clustering übersprungen: zu wenige vollständige Beobachtungen.")
        return

    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    X_scaled = prep.fit_transform(X)

    # Elbow-Werte und Silhouette-Scores
    scores = []
    for k in range(2, min(8, len(X) - 1)):
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        labels = km.fit_predict(X_scaled)
        scores.append({
            "k": k,
            "inertia": km.inertia_,
            "silhouette": silhouette_score(X_scaled, labels),
        })
    pd.DataFrame(scores).to_csv(OUT / "kmeans_model_selection.csv", index=False)

    # k basierend auf Elbow und Silhouette auswählen
    print("\nK-Means Modellwahl:")
    print(pd.DataFrame(scores).to_string(index=False))

    # Automatische Auswahl: hoher Silhouette Score, aber nicht trivial (k=2)
    silhouette_scores = {s["k"]: s["silhouette"] for s in scores}
    best_k = max(silhouette_scores, key=silhouette_scores.get)

    # Falls k=2, zweitbesten wählen
    if best_k == 2 and len(silhouette_scores) > 1:
        sorted_k = sorted(silhouette_scores.items(), key=lambda x: x[1], reverse=True)
        best_k = sorted_k[1][0]

    print(f"\nGewählte Clusterzahl k={best_k}")

    km = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=20)
    labels = km.fit_predict(X_scaled)
    cluster_df = df.loc[X.index, ["plr_id", "plr_name"]].copy()
    cluster_df["cluster"] = labels
    cluster_df.to_csv(OUT / "kmeans_clusters.csv", index=False)
    profile = df.loc[X.index].assign(cluster=labels).groupby("cluster")[features].mean()
    profile.to_csv(OUT / "kmeans_cluster_profiles.csv")

    # PCA für Visualisierung
    pca_vis = PCA(n_components=2)
    components_vis = pca_vis.fit_transform(X_scaled)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(components_vis[:, 0], components_vis[:, 1], c=labels, alpha=0.7)
    ax.set_xlabel(f"PC1 ({pca_vis.explained_variance_ratio_[0]:.1%})")
    ax.set_ylabel(f"PC2 ({pca_vis.explained_variance_ratio_[1]:.1%})")
    ax.set_title(f"PCA-Projektion (k={best_k} Cluster)")
    fig.tight_layout()
    fig.savefig(OUT / "kmeans_clusters.png", dpi=170)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. DECISION TREE (explorativ, mit Cross-Validation)
# ---------------------------------------------------------------------------

def run_decision_tree(df: pd.DataFrame) -> None:
    target = "laerm_gesamt_lden_db"
    features = [
        "arbeitslosenanteil_prozent", "transferbezugsanteil_prozent", "kinderarmut_prozent",
        "angebotsmiete_median_eur_m2", "population_density", "green_space_pct",
    ]
    features = [c for c in features if c in df.columns]
    if target not in df.columns or len(features) < 2:
        print("Decision Tree übersprungen: benötigte Variablen fehlen.")
        return

    work = df[[target] + features].dropna().copy()
    if len(work) < 30:
        print("Decision Tree übersprungen: weniger als 30 vollständige Fälle.")
        return

    # Binäres Ziel: oberes Quartil = hohe Lärmbelastung.
    threshold = work[target].quantile(0.75)
    y = (work[target] >= threshold).astype(int)
    if y.value_counts().min() < 5:
        print("Decision Tree übersprungen: zu wenige Fälle in einer Klasse.")
        return

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        DecisionTreeClassifier(
            max_depth=3, min_samples_leaf=10,
            class_weight="balanced", random_state=RANDOM_STATE
        )
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(model, work[features], y, cv=cv, scoring="f1")
    model.fit(work[features], y)
    tree = model[-1]

    with open(OUT / "decision_tree_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Schwelle oberes Quartil: {threshold:.3f} dB\n")
        f.write(f"5-fold CV F1: Mittel={scores.mean():.3f}, SD={scores.std():.3f}\n")
        f.write("\nFeature Importances:\n")
        for name, value in sorted(zip(features, tree.feature_importances_), key=lambda z: z[1], reverse=True):
            f.write(f"{name}: {value:.4f}\n")

    fig, ax = plt.subplots(figsize=(18, 8))
    plot_tree(tree, feature_names=features, class_names=["nicht hoch", "hoch"],
              filled=True, rounded=True, ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / "decision_tree.png", dpi=180)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. RÄUMLICHE AUTOKORRELATION: MORAN'S I
# ---------------------------------------------------------------------------

def run_morans_i(gdf: gpd.GeoDataFrame, regression_residuals: Optional[pd.Series] = None) -> None:
    if not HAS_PYSAL:
        print("Moran's I übersprungen. Installiert libpysal und esda.")
        return

    variables_to_check = []
    if "laerm_gesamt_lden_db" in gdf.columns:
        variables_to_check.append("laerm_gesamt_lden_db")
    if "benachteiligungsindex" in gdf.columns:
        variables_to_check.append("benachteiligungsindex")

    for variable in variables_to_check:
        if variable not in gdf.columns:
            continue
        subset = gdf[["geometry", variable]].dropna().copy()
        if len(subset) < 10:
            continue
        # Queen-Nachbarschaft; Inseln werden über w.islands sichtbar.
        weights = Queen.from_dataframe(subset, use_index=False)
        weights.transform = "r"
        mi = Moran(subset[variable].values, weights, permutations=999)
        print(
            f"Moran's I {variable}: I={mi.I:.4f}, p_sim={mi.p_sim:.4f}, "
            f"z_sim={mi.z_sim:.3f}, Inseln={len(weights.islands)}"
        )
        with open(OUT / f"morans_i_{variable}.txt", "w", encoding="utf-8") as f:
            f.write(f"Variable: {variable}\nI: {mi.I}\np_sim: {mi.p_sim}\nz_sim: {mi.z_sim}\n")
            f.write(f"Islands: {weights.islands}\n")

    # Moran's I für Regressionsresiduen (falls übergeben)
    if regression_residuals is not None and len(regression_residuals) > 10:
        residuals_df = gdf.copy()
        residuals_df["residuals"] = regression_residuals
        subset = residuals_df[["geometry", "residuals"]].dropna().copy()
        if len(subset) >= 10:
            weights = Queen.from_dataframe(subset, use_index=False)
            weights.transform = "r"
            mi_resid = Moran(subset["residuals"].values, weights, permutations=999)
            print(
                f"Moran's I (Regressionsresiduen): I={mi_resid.I:.4f}, p_sim={mi_resid.p_sim:.4f}, "
                f"z_sim={mi_resid.z_sim:.3f}"
            )
            with open(OUT / "morans_i_residuals.txt", "w", encoding="utf-8") as f:
                f.write(f"Variable: Regression Residuals\nI: {mi_resid.I}\np_sim: {mi_resid.p_sim}\nz_sim: {mi_resid.z_sim}\n")


# ---------------------------------------------------------------------------
# 9. KARTEN-EXPORT UND HAUPTPROGRAMM
# ---------------------------------------------------------------------------

def export_choropleths(gdf: gpd.GeoDataFrame) -> None:
    map_vars = [
        "laerm_gesamt_lden_db", "benachteiligungsindex", "angebotsmiete_median_eur_m2",
        "arbeitslosenanteil_prozent", "transferbezugsanteil_prozent", "kinderarmut_prozent",
    ]
    for col in map_vars:
        if col not in gdf.columns or gdf[col].notna().sum() == 0:
            continue
        fig, ax = plt.subplots(figsize=(9, 9))
        gdf.plot(column=col, cmap="viridis", legend=True, edgecolor="white",
                 linewidth=0.15, missing_kwds={"color": "lightgrey", "label": "Keine Daten"}, ax=ax)
        ax.set_title(f"Berlin nach Planungsräumen: {col}")
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(OUT / f"map_{col}.png", dpi=180)
        plt.close(fig)


def main() -> None:
    ensure_dirs()
    print("=" * 72)
    print("BERLIN DATA SCIENCE: LÄRM · SOZIALE LAGE · MIETEN")
    print("=" * 72)

    try:
        data = load_all_data()
    except (FileNotFoundError, KeyError, ValueError, ImportError) as exc:
        print("\nDATENIMPORT NOCH NICHT ABGESCHLOSSEN:")
        print(exc)
        print("\nNächster Schritt:")
        print("1. Rohdaten in data/raw/ ablegen.")
        print("2. Spaltennamen in SOCIAL_COLUMN_MAP / RENT_COLUMN_MAP prüfen.")
        print("3. Skript erneut starten.")
        return

    # EDA
    run_eda(data)

    # PCA für Deprivationsindex
    data_with_index = run_pca_benachteiligungsindex(data)

    # Regressionen mit Deprivationsindex
    regression_results = run_regressions(data_with_index)

    # K-Means mit Lärm, Deprivationsindex und Mieten
    run_clustering(data_with_index)

    # Decision Tree (optional - auskommentiert, da nicht zentral für Forschungsfrage)
    # run_decision_tree(data_with_index)

    # Moran's I (nur wenn Geometrie vorhanden)
    if data_with_index.geometry is not None and data_with_index.geometry.notna().any():
        residual_source = data_with_index[
            ["laerm_gesamt_lden_db", "benachteiligungsindex"]
        ].replace([np.inf, -np.inf], np.nan).dropna()
        residuals = None
        if len(residual_source) > len(["benachteiligungsindex"]) + 5:
            residual_X = sm.add_constant(residual_source[["benachteiligungsindex"]])
            residual_model = sm.OLS(
                residual_source["laerm_gesamt_lden_db"],
                residual_X,
            ).fit(cov_type="HC3")
            residuals = pd.Series(residual_model.resid, index=residual_source.index)
        run_morans_i(data_with_index, residuals)
    else:
        print("Moran's I übersprungen: Keine Geometrie vorhanden.")

    # Karten (nur wenn Geometrie vorhanden)
    if data_with_index.geometry is not None and data_with_index.geometry.notna().any():
        export_choropleths(data_with_index)
    else:
        print("Kartenexport übersprungen: Keine Geometrie vorhanden.")

    print("\nFertig! Ergebnisse liegen im Ordner 'outputs/'.")
    print("Wissenschaftlicher Hinweis: Ergebnisse sind Zusammenhänge auf Gebietsebene,")
    print("keine Aussagen über einzelne Personen und kein Kausalitätsnachweis.")


if __name__ == "__main__":
    main()
