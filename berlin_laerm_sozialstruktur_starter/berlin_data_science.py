"""
BERLIN DATA SCIENCE: Lärm, soziale Lage und Mieten (Einsteiger-Version)
=======================================================================

Leitfrage:
Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von
Lärm betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

So ist dieses Skript aufgebaut
------------------------------
Das Skript arbeitet in 9 Schritten. Jeder Schritt ist eine eigene Funktion.
Ganz unten in der Funktion main() steht, in welcher Reihenfolge die Schritte
aufgerufen werden. Am besten liest man das Skript also von unten (main) nach oben.

    Schritt 1: Daten laden und verknüpfen
    Schritt 2: PCA -> Benachteiligungsindex
    Schritt 3: Deskriptive Statistik
    Schritt 4: ANOVA (Hypothesentest)
    Schritt 5: Multiple lineare Regression (mit räumlicher Korrektur)
    Schritt 6: K-Means-Clustering
    Schritt 7: Moran's I (räumliche Abhängigkeit)
    Schritt 8: Karten
    Schritt 9: Ergebnisgrafik und Antwort auf die Leitfrage

Kleine Lesehilfe
----------------
- Ein "DataFrame" ist eine Tabelle (wie ein Excel-Blatt). Wir nennen sie meist "daten".
- Ein "GeoDataFrame" ist eine Tabelle mit einer zusätzlichen Spalte "geometry",
  in der die Umrisse der Planungsräume gespeichert sind.
- daten["spalte"] liest eine Spalte, daten["neue_spalte"] = ... legt eine neue an.
- Ausführliche Erklärungen zu allen Methoden stehen im Ordner docs/.

Quellen: siehe docs/02_daten.md
"""

import argparse
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
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from libpysal.weights import Queen
from esda.moran import Moran


# =============================================================================
# EINSTELLUNGEN
# Hier stehen alle Dateinamen und Parameter an einer Stelle.
# =============================================================================

# Ordner
ORDNER = Path(__file__).parent              # der Ordner, in dem dieses Skript liegt
ROHDATEN = ORDNER / "data" / "raw"
AUFBEREITET_BASIS = ORDNER / "data" / "processed"
AUSGABE_BASIS = ORDNER / "outputs"
AUFBEREITET = AUFBEREITET_BASIS
AUSGABE = AUSGABE_BASIS

# Eingabedateien
# Standardprofil: alle Daten aus dem Bezugsjahr 2022.
DATEI_PLANUNGSRAEUME = ROHDATEN / "planungsraeume.geojson"
DATEI_MSS_TABELLE_1 = ROHDATEN / "mss2023_gesamtindex_plr.xlsx"                # Einwohner
DATEI_MSS_TABELLE_2 = ROHDATEN / "mss2023_indexindikatoren_anteile_plr.xlsx"   # S1 bis S4
DATEI_MSS_TABELLE_3 = ROHDATEN / "mss2023_indexindikatoren_zwerte_plr.xlsx"    # amtlicher Status-Index
BLATT_MSS_TABELLE_1 = 0
BLATT_MSS_TABELLE_2 = 0
BLATT_MSS_TABELLE_3 = 0
DATEI_MIETEN = ROHDATEN / "Mietdaten.xlsx"
MIETEN_BLATT = "Planungsräume_2022"
DATEI_LAERM = AUFBEREITET / "laermdaten_aggregiert.csv"                       # erzeugt von aggregate_noise.py

DATENSTAND_KONFIGURATIONEN = {
    "2022": {
        "mss_tabelle_1": "mss2023_gesamtindex_plr.xlsx",
        "mss_blatt_1": 0,
        "mss_tabelle_2": "mss2023_indexindikatoren_anteile_plr.xlsx",
        "mss_blatt_2": 0,
        "mss_tabelle_3": "mss2023_indexindikatoren_zwerte_plr.xlsx",
        "mss_blatt_3": 0,
        "mieten_blatt": "Planungsräume_2022",
        "ordner": None,
    },
    "aktuell": {
        "mss_tabelle_1": "sozialdaten.xlsx",
        "mss_blatt_1": "1.SDI_PLR_MSS2025",
        "mss_tabelle_2": "mss2025_indexindikatoren_anteile_plr.xlsx",
        "mss_blatt_2": "2.1.IndexInd_Ant_PLR_MSS2025",
        "mss_tabelle_3": "mss2025_indexindikatoren_zwerte_plr.xlsx",
        "mss_blatt_3": "3.IndexInd_z_Werte_PLR_MSS2025",
        "mieten_blatt": "Planungsräume_2025",
        "ordner": "aktuell",
    },
}

# Parameter der Analyse
MINDEST_INSERATE = 21          # weniger Mietinserate gelten laut IBB als nicht repräsentativ
ANZAHL_CLUSTER = 4             # k für K-Means (Begründung: Elbow-Plot und Interpretierbarkeit)
CLUSTER_SCHWELLE = 0.25        # ab dieser Abweichung (in SD) heißt ein Clustermerkmal "hoch"/"niedrig"
ZUFALLSZAHL = 42               # fester Startwert, damit bei jedem Lauf dasselbe herauskommt
MORAN_PERMUTATIONEN = 999      # so oft werden die Werte beim Moran-Test zufällig gemischt
SIGNIFIKANZNIVEAU = 0.05

# Spaltennamen, die mehrfach gebraucht werden
INDIKATOREN = [
    "arbeitslosenanteil_prozent",    # S1 Arbeitslosigkeit
    "alleinerziehende_prozent",      # S2 Kinder in Alleinerziehenden-Haushalten
    "transferbezugsanteil_prozent",  # S3 Transferbezug
    "kinderarmut_prozent",           # S4 Kinderarmut
]
KONTROLLVARIABLEN = ["log_einwohnerdichte", "innere_stadt"]
CLUSTER_MERKMALE = ["laerm_gesamt_lden_db", "benachteiligungsindex", "angebotsmiete_median_eur_m2"]
QUINTIL_NAMEN = ["Q1\ngeringste", "Q2", "Q3", "Q4", "Q5\nstärkste"]

# Deutsche Beschriftungen für Grafiken
BESCHRIFTUNG = {
    "laerm_gesamt_lden_db": "Gesamtlärm LDEN [dB(A)]",
    "anteil_fassaden_lden_ueber_65_prozent": "Fassaden > 65 dB(A) LDEN [%]",
    "arbeitslosenanteil_prozent": "S1 Arbeitslosigkeit [%]",
    "alleinerziehende_prozent": "S2 Alleinerziehende [%]",
    "transferbezugsanteil_prozent": "S3 Transferbezug [%]",
    "kinderarmut_prozent": "S4 Kinderarmut [%]",
    "benachteiligungsindex": "Benachteiligungsindex (PC1, z)",
    "angebotsmiete_median_eur_m2": "Median-Angebotsmiete [EUR/m²]",
    "einwohnerdichte": "Einwohnerdichte [EW/km²]",
}


def datenstand_konfigurieren(datenstand):
    """Wählt die Quelldateien und getrennten Ausgabeordner eines Datenstands."""
    global DATEI_MSS_TABELLE_1, DATEI_MSS_TABELLE_2, DATEI_MSS_TABELLE_3
    global BLATT_MSS_TABELLE_1, BLATT_MSS_TABELLE_2, BLATT_MSS_TABELLE_3
    global MIETEN_BLATT, AUFBEREITET, AUSGABE, DATEI_LAERM

    if datenstand not in DATENSTAND_KONFIGURATIONEN:
        raise ValueError(f"Unbekannter Datenstand: {datenstand}")

    konfiguration = DATENSTAND_KONFIGURATIONEN[datenstand]
    DATEI_MSS_TABELLE_1 = ROHDATEN / konfiguration["mss_tabelle_1"]
    DATEI_MSS_TABELLE_2 = ROHDATEN / konfiguration["mss_tabelle_2"]
    DATEI_MSS_TABELLE_3 = ROHDATEN / konfiguration["mss_tabelle_3"]
    BLATT_MSS_TABELLE_1 = konfiguration["mss_blatt_1"]
    BLATT_MSS_TABELLE_2 = konfiguration["mss_blatt_2"]
    BLATT_MSS_TABELLE_3 = konfiguration["mss_blatt_3"]
    MIETEN_BLATT = konfiguration["mieten_blatt"]

    ordner = konfiguration["ordner"]
    if ordner is None:
        AUFBEREITET = AUFBEREITET_BASIS
        AUSGABE = AUSGABE_BASIS
    else:
        AUFBEREITET = AUFBEREITET_BASIS / ordner
        AUSGABE = AUSGABE_BASIS / ordner
    DATEI_LAERM = AUFBEREITET_BASIS / "laermdaten_aggregiert.csv"


# =============================================================================
# HILFSFUNKTIONEN
# Kleine Werkzeuge, die in mehreren Schritten benutzt werden.
# =============================================================================

def p_wert_text(p):
    """Macht aus einem p-Wert einen kurzen Text, z. B. 'p = 0.289' oder 'p < 0.001'."""
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def grafik_speichern(fig, dateiname, dpi=170):
    """Speichert eine Grafik als PNG im Ausgabeordner und schließt sie."""
    fig.tight_layout()
    fig.savefig(AUSGABE / dateiname, dpi=dpi)
    plt.close(fig)


def excel_zeilen_mit_plr_id(datei, blatt, id_spalte):
    """Liest eine Excel-Tabelle der Behörden und behält nur die Zeilen mit einer Planungsraum-ID.

    Die Tabellen haben Titel, Überschriften und Fußnoten. Statt die richtigen Zeilen
    von Hand abzuzählen, behalten wir einfach alle Zeilen, in denen in der ID-Spalte
    eine achtstellige Zahl steht (z. B. "01100101").
    """
    # header=None: Excel-Zeilen nicht als Spaltennamen benutzen. Die Spalten heißen dann 0, 1, 2, ...
    tabelle = pd.read_excel(datei, sheet_name=blatt, header=None, dtype={id_spalte: str})

    # ID-Spalte als Text vereinheitlichen: Leerzeichen weg, ".0" weg, auf 8 Stellen mit Nullen auffüllen
    ids = tabelle[id_spalte].astype(str).str.strip()
    ids = ids.str.replace(".0", "", regex=False)
    ids = ids.str.zfill(8)

    # Eine Zeile ist gültig, wenn die ID aus genau 8 Ziffern besteht
    ist_gueltig = ids.str.isdigit() & (ids.str.len() == 8)
    tabelle = tabelle[ist_gueltig].copy()
    tabelle[id_spalte] = ids[ist_gueltig]

    if tabelle[id_spalte].duplicated().any():
        raise ValueError(f"Doppelte Planungsraum-IDs in {datei.name}")
    return tabelle


def bezirksgrenzen_zeichnen(ax, daten, mit_namen=False):
    """Zeichnet die 12 Berliner Bezirksgrenzen als schwarze Linien in eine Karte."""
    # dissolve: alle Planungsräume eines Bezirks zu einer Fläche verschmelzen
    bezirke = daten[["bez", "geometry"]].dissolve(by="bez")
    bezirke.boundary.plot(ax=ax, color="black", linewidth=0.7)

    if mit_namen:
        for bezirk_name, flaeche in bezirke.geometry.items():
            punkt = flaeche.representative_point()     # ein Punkt sicher innerhalb der Fläche
            kurzname = bezirk_name.split(" - ")[-1]    # "08 - Neukölln" -> "Neukölln"
            ax.annotate(kurzname, (punkt.x, punkt.y), ha="center", fontsize=7,
                        bbox={"boxstyle": "round,pad=0.15", "fc": "white", "alpha": 0.6, "lw": 0})


# =============================================================================
# SCHRITT 1: DATEN LADEN UND VERKNÜPFEN
# =============================================================================

def daten_laden():
    print("\n[1] Daten laden und verknüpfen ...")

    # --- 1a) Planungsräume (Gebietsgrenzen) -----------------------------------
    daten = gpd.read_file(DATEI_PLANUNGSRAEUME)
    daten["plr_id"] = daten["plr_id"].astype(str).str.zfill(8)
    daten = daten[["plr_id", "plr_name", "pgr_id", "bez", "stadtraum_name", "geometry"]]

    # --- 1b) Sozialdaten aus den drei MSS-Tabellen ----------------------------
    # Tabelle 1: Spalte 0 = ID, Spalte 2 = Einwohner
    tabelle1 = excel_zeilen_mit_plr_id(DATEI_MSS_TABELLE_1, BLATT_MSS_TABELLE_1, 0)
    einwohner = pd.DataFrame()
    einwohner["plr_id"] = tabelle1[0]
    einwohner["einwohner"] = pd.to_numeric(tabelle1[2], errors="coerce")

    # Tabelle 2.1: Spalten 3 bis 6 = Indikatoren S1 bis S4 (in Prozent)
    tabelle2 = excel_zeilen_mit_plr_id(DATEI_MSS_TABELLE_2, BLATT_MSS_TABELLE_2, 0)
    indikatoren = pd.DataFrame()
    indikatoren["plr_id"] = tabelle2[0]
    indikatoren["arbeitslosenanteil_prozent"] = pd.to_numeric(tabelle2[3], errors="coerce")
    indikatoren["alleinerziehende_prozent"] = pd.to_numeric(tabelle2[4], errors="coerce")
    indikatoren["transferbezugsanteil_prozent"] = pd.to_numeric(tabelle2[5], errors="coerce")
    indikatoren["kinderarmut_prozent"] = pd.to_numeric(tabelle2[6], errors="coerce")

    # Tabelle 3: Spalte 8 = amtlicher Status-Index (nur zur Kontrolle der PCA)
    tabelle3 = excel_zeilen_mit_plr_id(DATEI_MSS_TABELLE_3, BLATT_MSS_TABELLE_3, 0)
    amtlicher_index = pd.DataFrame()
    amtlicher_index["plr_id"] = tabelle3[0]
    amtlicher_index["mss_statusindex"] = pd.to_numeric(tabelle3[8], errors="coerce")

    # --- 1c) Mietdaten der IBB --------------------------------------------------
    # Spalte 1 = ID, Spalte 2 = Name, Spalte 4 = Median-Miete, Spalte 6 = Anzahl Inserate
    tabelle_mieten = excel_zeilen_mit_plr_id(DATEI_MIETEN, MIETEN_BLATT, 1)
    mieten = pd.DataFrame()
    mieten["plr_id"] = tabelle_mieten[1]
    mieten["plr_name_ibb"] = tabelle_mieten[2].astype(str).str.strip()
    mieten["angebotsmiete_median_roh"] = pd.to_numeric(tabelle_mieten[4], errors="coerce")
    mieten["anzahl_mietinserate"] = pd.to_numeric(tabelle_mieten[6], errors="coerce")

    # --- 1d) Lärmdaten (von aggregate_noise.py vorbereitet) --------------------
    laerm = pd.read_csv(DATEI_LAERM, dtype={"plr_id": str})
    laerm["plr_id"] = laerm["plr_id"].str.zfill(8)
    laerm = laerm[["plr_id", "laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent"]]

    # --- 1e) Alles über die Planungsraum-ID verknüpfen --------------------------
    # how="left": alle 542 Planungsräume bleiben erhalten, auch wenn Werte fehlen.
    # validate="one_to_one": Abbruch, falls eine ID doppelt vorkommt.
    daten = daten.merge(einwohner, on="plr_id", how="left", validate="one_to_one")
    daten = daten.merge(indikatoren, on="plr_id", how="left", validate="one_to_one")
    daten = daten.merge(amtlicher_index, on="plr_id", how="left", validate="one_to_one")
    daten = daten.merge(mieten, on="plr_id", how="left", validate="one_to_one")
    daten = daten.merge(laerm, on="plr_id", how="left", validate="one_to_one")

    # --- 1f) Kontrolle: Stimmen die Gebietsnamen der IBB mit den offiziellen überein? ---
    hat_ibb_namen = daten["plr_name_ibb"].notna()
    name_anders = daten["plr_name"] != daten["plr_name_ibb"]
    abweichungen = daten.loc[hat_ibb_namen & name_anders, ["plr_id", "plr_name", "plr_name_ibb"]]
    abweichungen.to_csv(AUSGABE / "pruefung_namensabweichungen_ibb.csv", index=False)

    # --- 1g) Neue Variablen berechnen ------------------------------------------
    # Fläche in km²: Die Geometrie ist in Metern, also m² / 1.000.000
    flaeche_km2 = daten.geometry.area / 1_000_000
    daten["einwohnerdichte"] = daten["einwohner"] / flaeche_km2
    # Logarithmus staucht sehr große Dichtewerte; +1 verhindert log(0) bei unbewohnten Gebieten
    daten["log_einwohnerdichte"] = np.log1p(daten["einwohnerdichte"])
    # 1 = Innere Stadt, 0 = Äußere Stadt
    daten["innere_stadt"] = (daten["stadtraum_name"] == "Innere Stadt").astype(int)

    # Miete nur übernehmen, wenn genug Inserate vorhanden sind, sonst fehlender Wert (NaN)
    genug_inserate = daten["anzahl_mietinserate"] >= MINDEST_INSERATE
    daten["angebotsmiete_median_eur_m2"] = daten["angebotsmiete_median_roh"].where(genug_inserate)

    # --- 1h) Qualitätsbericht: Wie viele gültige und fehlende Werte hat jede Spalte? ---
    spalten = []
    for spalte in daten.columns:
        if spalte not in ["geometry", "plr_id", "plr_name", "plr_name_ibb"]:
            spalten.append(spalte)
    qualitaet = pd.DataFrame()
    qualitaet["gueltig"] = daten[spalten].notna().sum()
    qualitaet["fehlend"] = daten[spalten].isna().sum()
    qualitaet.to_csv(AUSGABE / "datenqualitaet.csv")

    print("Planungsräume:", len(daten))
    print("mit Sozialdaten:", daten["kinderarmut_prozent"].notna().sum())
    print("mit Mietwert:", daten["angebotsmiete_median_eur_m2"].notna().sum())
    print("IBB-Namensabweichungen:", len(abweichungen))
    return daten


def daten_speichern(daten):
    """Speichert den fertigen Datensatz (mit Index, Quintil und Cluster) in data/processed/."""
    kopie = daten.copy()
    # Das GeoPackage-Format kennt keine Kategorien, deshalb das Quintil als Text speichern
    kopie["deprivationsquintil"] = kopie["deprivationsquintil"].astype("string")
    kopie.to_file(AUFBEREITET / "berlin_merged.gpkg", driver="GPKG")
    kopie.drop(columns="geometry").to_csv(AUFBEREITET / "berlin_merged.csv", index=False)


# =============================================================================
# SCHRITT 2: PCA -> BENACHTEILIGUNGSINDEX
# =============================================================================

def pca_benachteiligungsindex(daten):
    print("\n[2] PCA: Benachteiligungsindex aus S1-S4 ...")

    # Nur Gebiete mit allen vier Indikatoren (2022: 536, aktuell: 535)
    indikator_daten = daten[INDIKATOREN].dropna()

    # 2a) Standardisieren: jede Spalte bekommt Mittelwert 0 und Standardabweichung 1
    z_werte = StandardScaler().fit_transform(indikator_daten)

    # 2b) PCA berechnen
    pca = PCA()
    hauptkomponenten = pca.fit_transform(z_werte)   # Werte jedes Gebiets auf PC1 bis PC4
    eigenwerte = pca.explained_variance_
    erklaerte_varianz = pca.explained_variance_ratio_

    varianz_tabelle = pd.DataFrame()
    varianz_tabelle["component"] = ["PC1", "PC2", "PC3", "PC4"]
    varianz_tabelle["eigenvalue"] = eigenwerte
    varianz_tabelle["explained_variance_ratio"] = erklaerte_varianz
    varianz_tabelle.to_csv(AUSGABE / "pca_explained_variance.csv", index=False)

    # 2c) Ladungen = Korrelation zwischen Indikator und Hauptkomponente (Eigenvektor * Wurzel(Eigenwert))
    ladungen = pd.DataFrame(pca.components_.T * np.sqrt(eigenwerte),
                            index=INDIKATOREN, columns=["PC1", "PC2", "PC3", "PC4"])

    # 2d) Das Vorzeichen einer PCA ist zufällig. Wir drehen es so, dass hohe Werte = mehr Benachteiligung.
    pc1 = hauptkomponenten[:, 0]          # erste Spalte = PC1
    if ladungen["PC1"].sum() < 0:
        ladungen["PC1"] = -ladungen["PC1"]
        pc1 = -pc1
    ladungen.to_csv(AUSGABE / "pca_loadings.csv")

    # 2e) PC1 noch einmal standardisieren (Mittelwert 0, SD 1) und als neue Spalte speichern
    index = (pc1 - pc1.mean()) / pc1.std(ddof=1)
    daten.loc[indikator_daten.index, "benachteiligungsindex"] = index

    # 2f) Kontrolle: Wie stark stimmt unser Index mit dem amtlichen Index überein?
    vergleich = daten[["benachteiligungsindex", "mss_statusindex"]].dropna()
    r = np.corrcoef(vergleich["benachteiligungsindex"], vergleich["mss_statusindex"])[0, 1]

    bericht = (
        f"PCA über {len(INDIKATOREN)} MSS-Status-Indikatoren, n = {len(indikator_daten)} Planungsräume\n"
        f"Eigenwerte: {np.round(eigenwerte, 3).tolist()}\n"
        f"Erklärte Varianz PC1: {erklaerte_varianz[0]:.1%}\n\n"
        f"Ladungen PC1:\n{ladungen['PC1'].round(3).to_string()}\n\n"
        f"Übereinstimmung mit dem amtlichen MSS-Status-Index: r = {r:.3f}\n"
        "Der Index ist z-standardisiert (Mittelwert 0, SD 1); höhere Werte = stärkere Benachteiligung.\n"
    )
    (AUSGABE / "pca_bericht.txt").write_text(bericht, encoding="utf-8")
    print(bericht)

    # 2g) Grafik: links Scree-Plot, rechts Ladungen von PC1
    fig, (ax_links, ax_rechts) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax_links.bar(["PC1", "PC2", "PC3", "PC4"], erklaerte_varianz * 100, color="steelblue")
    ax_links.set_title("Scree-Plot")
    ax_links.set_ylabel("Erklärte Varianz [%]")

    ladungen_pc1 = ladungen["PC1"].rename(index=BESCHRIFTUNG).sort_values()
    ax_rechts.barh(ladungen_pc1.index, ladungen_pc1.values, color="darkorange")
    ax_rechts.set_title(f"Ladungen PC1 ({erklaerte_varianz[0]:.1%} erklärte Varianz)")
    ax_rechts.set_xlim(0, 1)
    grafik_speichern(fig, "pca_scree_ladungen.png")
    return daten


# =============================================================================
# SCHRITT 3: DESKRIPTIVE STATISTIK
# =============================================================================

def deskriptive_statistik(daten):
    print("\n[3] Deskriptive Statistik ...")
    spalten = [
        "laerm_gesamt_lden_db", "anteil_fassaden_lden_ueber_65_prozent", "benachteiligungsindex",
        "arbeitslosenanteil_prozent", "alleinerziehende_prozent", "transferbezugsanteil_prozent",
        "kinderarmut_prozent", "angebotsmiete_median_eur_m2", "einwohnerdichte",
    ]

    # 3a) Kennzahlen: Anzahl, Mittelwert, Standardabweichung, Minimum, Quartile, Maximum, Varianz
    kennzahlen = daten[spalten].describe().T
    kennzahlen["variance"] = daten[spalten].var()
    kennzahlen.to_csv(AUSGABE / "descriptive_statistics.csv")
    print(kennzahlen.round(2).to_string())

    # 3b) Histogramme: 9 Variablen in einem Raster aus 3 x 3 Feldern
    fig, achsen = plt.subplots(3, 3, figsize=(13, 10))
    achsen = achsen.flatten()                     # aus dem 3x3-Raster eine einfache Liste machen
    for i in range(len(spalten)):
        spalte = spalten[i]
        ax = achsen[i]
        sns.histplot(daten[spalte].dropna(), kde=True, ax=ax)
        ax.set_title(BESCHRIFTUNG[spalte], fontsize=9)
        ax.set_xlabel("")
    fig.suptitle("Verteilungen der Analysevariablen")
    grafik_speichern(fig, "histogramme.png")

    # 3c) Korrelationsmatrix als farbige Tabelle (Heatmap)
    korrelation = daten[spalten].corr()
    korrelation = korrelation.rename(index=BESCHRIFTUNG, columns=BESCHRIFTUNG)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(korrelation, annot=True, cmap="vlag", center=0, fmt=".2f", ax=ax)
    ax.set_title("Korrelationsmatrix (Überblick)")
    grafik_speichern(fig, "korrelationsmatrix.png")


# =============================================================================
# SCHRITT 4: ANOVA
# Unterscheidet sich der mittlere Lärm zwischen den fünf Benachteiligungs-Quintilen?
# =============================================================================

def anova(daten):
    print("\n[4] ANOVA: Lärm nach Quintilen des Benachteiligungsindex ...")

    # 4a) Für jedes Quintil die Lärmwerte als eigene Gruppe sammeln
    gruppen = []
    for quintil in QUINTIL_NAMEN:
        ist_im_quintil = daten["deprivationsquintil"] == quintil
        laerm_werte = daten.loc[ist_im_quintil, "laerm_gesamt_lden_db"].dropna()
        gruppen.append(laerm_werte)

    # 4b) ANOVA (scipy): vergleicht die Streuung zwischen den Gruppen mit der Streuung innerhalb
    ergebnis = stats.f_oneway(gruppen[0], gruppen[1], gruppen[2], gruppen[3], gruppen[4])
    f_wert = ergebnis.statistic
    p_wert = ergebnis.pvalue

    # 4c) Kennzahlen je Quintil
    profil = daten.groupby("deprivationsquintil", observed=True)["laerm_gesamt_lden_db"].agg(
        ["count", "mean", "median", "std"])
    profil.to_csv(AUSGABE / "anova_profile.csv")

    text = (f"ANOVA Lärm (LDEN) ~ Quintil des Benachteiligungsindex\n"
            f"F = {f_wert:.3f}, {p_wert_text(p_wert)}\n\n{profil.round(2).to_string()}\n")
    (AUSGABE / "anova_ergebnis.txt").write_text(text, encoding="utf-8")
    print(f"F = {f_wert:.2f}, {p_wert_text(p_wert)}")
    print(profil.round(2).to_string())
    return p_wert


# =============================================================================
# SCHRITT 5: MULTIPLE LINEARE REGRESSION
# =============================================================================

def regression_rechnen(daten, zielvariable, einflussvariablen):
    """Schätzt ein Regressionsmodell zweimal: klassisch und mit räumlich korrigierten Standardfehlern.

    Die Koeffizienten sind in beiden Fällen gleich. Unterschiedlich ist nur, wie unsicher
    sie eingeschätzt werden (Standardfehler, p-Wert).
    """
    # Nur Gebiete ohne fehlende Werte in den benötigten Spalten
    spalten = [zielvariable] + einflussvariablen + ["pgr_id"]
    modell_daten = daten[spalten].dropna()

    y = modell_daten[zielvariable]
    X = sm.add_constant(modell_daten[einflussvariablen].astype(float))   # Konstante = Achsenabschnitt

    # Klassische OLS-Regression
    modell_klassisch = sm.OLS(y, X).fit()

    # Räumlich korrigiert: Planungsräume im selben Prognoseraum werden als Gruppe behandelt.
    # factorize macht aus den Prognoseraum-IDs einfache Gruppennummern 0, 1, 2, ...
    prognoseraum_nummer = pd.factorize(modell_daten["pgr_id"])[0]
    modell_korrigiert = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": prognoseraum_nummer})

    return modell_klassisch, modell_korrigiert


def regressionen(daten):
    print("\n[5] Multiple lineare Regression ...")
    index = ["benachteiligungsindex"]

    # Die drei Modelle: Name, Zielvariable, Einflussvariablen
    modell_liste = [
        ("A1_laerm_einfach", "laerm_gesamt_lden_db", index),
        ("A2_laerm_kontrollen", "laerm_gesamt_lden_db", index + KONTROLLVARIABLEN),
        ("B_miete", "angebotsmiete_median_eur_m2", ["laerm_gesamt_lden_db"] + index + KONTROLLVARIABLEN),
    ]

    modelle = {}          # hier werden alle geschätzten Modelle gesammelt
    zeilen = []           # hier werden die Zeilen der Übersichtstabelle gesammelt

    for name, zielvariable, einflussvariablen in modell_liste:
        klassisch, korrigiert = regression_rechnen(daten, zielvariable, einflussvariablen)
        modelle[name + "_klassisch"] = klassisch
        modelle[name + "_korrigiert"] = korrigiert

        # Vollständige Ergebnistabellen als Textdatei (korrigierte zuerst)
        text = ("STANDARDFEHLER NACH PROGNOSERAUM GECLUSTERT (maßgeblich)\n"
                + korrigiert.summary().as_text() + "\n\n\n"
                + "KLASSISCHE OLS-STANDARDFEHLER (zum Vergleich)\n"
                + klassisch.summary().as_text() + "\n")
        (AUSGABE / f"regression_{name}.txt").write_text(text, encoding="utf-8")

        # Eine Zeile pro Einflussvariable für die Übersicht
        for variable in einflussvariablen:
            zeilen.append({
                "modell": name,
                "zielvariable": zielvariable,
                "term": variable,
                "koeffizient": klassisch.params[variable],
                "std_fehler_ols": klassisch.bse[variable],
                "p_wert_ols": klassisch.pvalues[variable],
                "std_fehler_cluster": korrigiert.bse[variable],
                "p_wert_cluster": korrigiert.pvalues[variable],
                "n": int(klassisch.nobs),
                "r2": klassisch.rsquared,
            })

    uebersicht = pd.DataFrame(zeilen)
    uebersicht.to_csv(AUSGABE / "regression_uebersicht.csv", index=False)
    print(uebersicht.round(4).to_string(index=False))
    return modelle


# =============================================================================
# SCHRITT 6: K-MEANS-CLUSTERING
# =============================================================================

def stufe(z_wert):
    """Übersetzt einen standardisierten Mittelwert in 'hoch', 'mittel' oder 'niedrig'."""
    if z_wert > CLUSTER_SCHWELLE:
        return "hoch"
    if z_wert < -CLUSTER_SCHWELLE:
        return "niedrig"
    return "mittel"


def kmeans_clustering(daten):
    print("\n[6] K-Means-Clustering ...")

    # 6a) Nur Gebiete mit allen drei Merkmalen (2022: 341, aktuell: 434)
    cluster_daten = daten[CLUSTER_MERKMALE].dropna().copy()
    z_werte = StandardScaler().fit_transform(cluster_daten)

    # 6b) Elbow-Methode: K-Means für k = 1 bis 8 rechnen und die Inertia notieren
    k_werte = []
    inertia_werte = []
    for k in range(1, 9):
        kmeans = KMeans(n_clusters=k, random_state=ZUFALLSZAHL, n_init=20)
        kmeans.fit(z_werte)
        k_werte.append(k)
        inertia_werte.append(kmeans.inertia_)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(k_werte, inertia_werte, marker="o")
    ax.axvline(ANZAHL_CLUSTER, color="grey", linestyle="--", label=f"gewählt: k = {ANZAHL_CLUSTER}")
    ax.set_title("Elbow-Methode")
    ax.set_xlabel("Anzahl Cluster k")
    ax.set_ylabel("Inertia (Summe quadrierter Abstände)")
    ax.legend()
    grafik_speichern(fig, "kmeans_elbow.png", dpi=160)

    # 6c) Endgültiges K-Means mit k = 4
    kmeans = KMeans(n_clusters=ANZAHL_CLUSTER, random_state=ZUFALLSZAHL, n_init=20)
    roh_nummern = kmeans.fit_predict(z_werte)

    # 6d) Cluster nach mittlerem Lärm sortieren (C1 = leisester), damit die Nummern immer gleich sind
    z_tabelle = pd.DataFrame(z_werte, columns=CLUSTER_MERKMALE)
    z_tabelle["roh_nummer"] = roh_nummern
    laerm_je_cluster = z_tabelle.groupby("roh_nummer")["laerm_gesamt_lden_db"].mean().sort_values()

    neue_nummer = {}
    nummer = 1
    for alte_nummer in laerm_je_cluster.index:
        neue_nummer[alte_nummer] = nummer
        nummer = nummer + 1
    z_tabelle["cluster_nr"] = z_tabelle["roh_nummer"].map(neue_nummer)

    # 6e) Cluster benennen, z. B. "C3: Lärm hoch · Benachteiligung hoch · Miete niedrig"
    kurzname = {"laerm_gesamt_lden_db": "Lärm", "benachteiligungsindex": "Benachteiligung",
                "angebotsmiete_median_eur_m2": "Miete"}
    z_mittelwerte = z_tabelle.groupby("cluster_nr")[CLUSTER_MERKMALE].mean()
    clustername = {}
    for nr in z_mittelwerte.index:
        teile = []
        for merkmal in CLUSTER_MERKMALE:
            teile.append(kurzname[merkmal] + " " + stufe(z_mittelwerte.loc[nr, merkmal]))
        clustername[nr] = f"C{nr}: " + " · ".join(teile)

    # 6f) Clusterprofile in Originaleinheiten (dB, Index, EUR/m²) speichern
    cluster_daten["cluster_nr"] = z_tabelle["cluster_nr"].values
    profil = cluster_daten.groupby("cluster_nr")[CLUSTER_MERKMALE].mean()
    profil.insert(0, "anzahl_plr", cluster_daten["cluster_nr"].value_counts().sort_index().values)
    profil.insert(0, "clustername", profil.index.map(clustername))
    profil.index.name = "cluster"
    profil.to_csv(AUSGABE / "kmeans_cluster_profiles.csv")
    print(profil.round(2).to_string())

    # 6g) Zuordnung jedes Gebiets zu seinem Cluster speichern
    cluster_spalte = cluster_daten["cluster_nr"].map(clustername)
    zuordnung = daten.loc[cluster_daten.index, ["plr_id", "plr_name"]].copy()
    zuordnung["cluster"] = cluster_spalte
    zuordnung.to_csv(AUSGABE / "kmeans_clusters.csv", index=False)
    return cluster_spalte


# =============================================================================
# SCHRITT 7: MORAN'S I
# Ähneln sich benachbarte Planungsräume stärker, als es zufällig zu erwarten wäre?
# =============================================================================

def moran_berechnen(daten, werte):
    """Berechnet Moran's I für eine Spalte (oder Residuen) mit Queen-Nachbarschaft."""
    werte = werte.dropna()
    gebiete = daten.loc[werte.index, ["geometry"]]

    # Queen-Nachbarschaft: Nachbarn sind Gebiete mit gemeinsamer Grenze oder gemeinsamer Ecke
    nachbarn = Queen.from_dataframe(gebiete, use_index=False)
    nachbarn.transform = "r"         # zeilenstandardisiert: Durchschnitt der Nachbarn

    np.random.seed(ZUFALLSZAHL)      # damit die 999 Zufallsmischungen jedes Mal gleich sind
    return Moran(werte.values, nachbarn, permutations=MORAN_PERMUTATIONEN)


def morans_i(daten, modelle):
    print("\n[7] Moran's I ...")
    # Für die Residuen (Fehler der Regression) nehmen wir die klassischen Modelle;
    # die Residuen sind in beiden Varianten identisch.
    pruefungen = [
        ("laerm_gesamt_lden_db", daten["laerm_gesamt_lden_db"]),
        ("benachteiligungsindex", daten["benachteiligungsindex"]),
        ("residuen_A1", modelle["A1_laerm_einfach_klassisch"].resid),
        ("residuen_A2", modelle["A2_laerm_kontrollen_klassisch"].resid),
    ]

    zeilen = []
    for name, werte in pruefungen:
        ergebnis = moran_berechnen(daten, werte)
        zeilen.append({"variable": name, "n": len(werte.dropna()), "I": ergebnis.I, "p_sim": ergebnis.p_sim})

    tabelle = pd.DataFrame(zeilen)
    tabelle.to_csv(AUSGABE / "morans_i.csv", index=False)
    print(tabelle.round(4).to_string(index=False))
    return tabelle


# =============================================================================
# SCHRITT 8: KARTEN
# =============================================================================

def karte_zeichnen(daten, spalte, farbschema):
    """Zeichnet eine Berlin-Karte, in der jeder Planungsraum nach seinem Wert eingefärbt ist."""
    fig, ax = plt.subplots(figsize=(10, 8.5))
    daten.plot(column=spalte, cmap=farbschema, legend=True, edgecolor="white", linewidth=0.15, ax=ax,
               legend_kwds={"shrink": 0.6, "label": BESCHRIFTUNG[spalte]},
               missing_kwds={"color": "lightgrey", "label": "Keine Daten"})
    bezirksgrenzen_zeichnen(ax, daten)
    ax.set_title("Berlin nach Planungsräumen: " + BESCHRIFTUNG[spalte])
    ax.set_axis_off()
    grafik_speichern(fig, f"map_{spalte}.png", dpi=180)


def cluster_karte_zeichnen(daten):
    """Zeichnet die Berlin-Karte der K-Means-Gebietstypen."""
    namen = sorted(daten["cluster"].dropna().unique())
    farben = sns.color_palette("Set2", len(namen))
    anzahl = daten["cluster"].value_counts()

    fig, ax = plt.subplots(figsize=(12, 10))

    # Erst die nicht geclusterten Gebiete in Grau ...
    ohne_cluster = daten[daten["cluster"].isna()]
    ohne_cluster.plot(ax=ax, color="#e0e0e0", edgecolor="white", linewidth=0.15)

    # ... dann jeden Cluster in seiner Farbe, und dabei die Legende aufbauen
    legenden_kaestchen = []
    legenden_texte = []
    for i in range(len(namen)):
        name = namen[i]
        daten[daten["cluster"] == name].plot(ax=ax, color=farben[i], edgecolor="white", linewidth=0.15)
        legenden_kaestchen.append(plt.Rectangle((0, 0), 1, 1, color=farben[i]))
        legenden_texte.append(f"{name} (n = {anzahl[name]})")
    legenden_kaestchen.append(plt.Rectangle((0, 0), 1, 1, color="#e0e0e0"))
    legenden_texte.append(f"Nicht geclustert: Miete oder Sozialdaten fehlen (n = {len(ohne_cluster)})")

    bezirksgrenzen_zeichnen(ax, daten, mit_namen=True)
    ax.legend(legenden_kaestchen, legenden_texte, loc="lower left", fontsize=8,
              title="Gebietstypen (K-Means)", title_fontsize=9)
    ax.set_title("Berlin: Gebietstypen nach Lärm, sozialer Benachteiligung und Angebotsmiete", fontsize=13)
    ax.set_axis_off()
    grafik_speichern(fig, "map_kmeans_cluster.png", dpi=200)


# =============================================================================
# SCHRITT 9: ERGEBNISGRAFIK UND ANTWORT AUF DIE LEITFRAGE
# =============================================================================

def ergebnis_text(daten, modelle, anova_p, moran_tabelle):
    """Formuliert die Antwort auf die Leitfrage aus den berechneten Zahlen (kein fester Text)."""
    a1 = modelle["A1_laerm_einfach_korrigiert"]
    a2 = modelle["A2_laerm_kontrollen_korrigiert"]
    b = modelle["B_miete_korrigiert"]
    a1_klassisch = modelle["A1_laerm_einfach_klassisch"]
    a2_klassisch = modelle["A2_laerm_kontrollen_klassisch"]
    index = "benachteiligungsindex"
    laerm = "laerm_gesamt_lden_db"

    # Mittlerer Lärm je Quintil
    laerm_je_quintil = daten.groupby("deprivationsquintil", observed=True)[laerm].mean()
    abstand_q1 = laerm_je_quintil.iloc[1:].mean() - laerm_je_quintil.iloc[0]          # Q2-Q5 im Mittel minus Q1
    spannweite_q2_q5 = laerm_je_quintil.iloc[1:].max() - laerm_je_quintil.iloc[1:].min()
    quintil_werte = []
    for wert in laerm_je_quintil.values:
        quintil_werte.append(f"{wert:.1f}")
    quintil_text = " | ".join(quintil_werte)

    # Anteil der Gebiete, die laut UND benachteiligt sind
    cluster = daten["cluster"].dropna()
    laut_und_benachteiligt = cluster[cluster.str.contains("Lärm hoch · Benachteiligung hoch", regex=False)]
    anteil = len(laut_und_benachteiligt) / len(cluster)

    # H1 entscheiden: signifikant positiver Effekt in Modell A2 (räumlich korrigiert)?
    if a2.pvalues[index] < SIGNIFIKANZNIVEAU and a2.params[index] > 0:
        h1 = "H1 gestützt: Mehr Benachteiligung geht auch mit Kontrollvariablen mit mehr Lärm einher."
    else:
        h1 = "H1 nicht gestützt: Kein signifikanter linearer Zusammenhang zwischen Benachteiligung und Lärm."

    zeilen = [
        h1,
        f"A1: {a1.params[index]:+.2f} dB pro SD Benachteiligung, R² = {a1.rsquared:.3f}, {p_wert_text(a1.pvalues[index])} "
        f"(räumlich korrigiert; ohne Korrektur {p_wert_text(a1_klassisch.pvalues[index])}). "
        f"A2 (mit Dichte und Lage): {a2.params[index]:+.2f} dB, {p_wert_text(a2.pvalues[index])} "
        f"(ohne Korrektur {p_wert_text(a2_klassisch.pvalues[index])}).",
        f"Mittlerer Lärm je Quintil: {quintil_text} dB (Q1→Q5), ANOVA {p_wert_text(anova_p)}. "
        f"Die am wenigsten benachteiligten Gebiete (Q1) sind {abstand_q1:.1f} dB leiser; zwischen Q2 und Q5 "
        f"liegen nur {spannweite_q2_q5:.1f} dB → kein Gradient 'je benachteiligter, desto lauter'.",
        f"H2: Miete steigt um {b.params[laerm]:+.2f} EUR/m² pro dB ({p_wert_text(b.pvalues[laerm])}) und sinkt um "
        f"{-b.params[index]:.2f} EUR/m² pro SD Benachteiligung ({p_wert_text(b.pvalues[index])}) – Lageeffekt, keine Kausalität.",
        f"H3: {cluster.nunique()} Gebietstypen; {len(laut_und_benachteiligt)} von {len(cluster)} PLR "
        f"({anteil:.0%}) sind zugleich laut und benachteiligt (Mehrfachbelastung).",
    ]

    moran_laerm = moran_tabelle.loc[moran_tabelle["variable"] == "laerm_gesamt_lden_db", "I"].iloc[0]
    moran_residuen = moran_tabelle.loc[moran_tabelle["variable"] == "residuen_A2", "I"].iloc[0]
    zeilen.append(f"Räumlich: Lärm I = {moran_laerm:.2f}, Residuen A2 I = {moran_residuen:.2f} "
                  "→ benachbarte Gebiete ähneln sich. Deshalb werden die Standardfehler nach "
                  "Prognoseraum geclustert; alle p-Werte oben sind räumlich korrigiert.")
    return zeilen


def ergebnisgrafik(daten, modelle, anova_p, moran_tabelle):
    print("\n[9] Ergebnis ...")
    zeilen = ergebnis_text(daten, modelle, anova_p, moran_tabelle)
    (AUSGABE / "ergebnis_zusammenfassung.txt").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    print("ERGEBNIS ZUR LEITFRAGE:")
    for zeile in zeilen:
        print("-", zeile)

    laerm = "laerm_gesamt_lden_db"
    index = "benachteiligungsindex"
    fig, achsen = plt.subplots(2, 2, figsize=(15, 11))
    feld_a = achsen[0, 0]
    feld_b = achsen[0, 1]
    feld_c = achsen[1, 0]
    feld_d = achsen[1, 1]

    # Feld A: Boxplot Lärm je Quintil + rote Linie mit den Mittelwerten
    quintil_daten = daten[["deprivationsquintil", laerm]].dropna()
    sns.boxplot(data=quintil_daten, x="deprivationsquintil", y=laerm, color="lightsteelblue",
                showfliers=False, ax=feld_a)
    mittelwerte = quintil_daten.groupby("deprivationsquintil", observed=True)[laerm].mean()
    feld_a.plot(range(len(mittelwerte)), mittelwerte.values, color="crimson", marker="o", lw=2, label="Mittelwert")
    feld_a.legend()
    feld_a.set_title(f"A  Lärm nach sozialer Benachteiligung (ANOVA {p_wert_text(anova_p)})")
    feld_a.set_xlabel("Quintile des Benachteiligungsindex")
    feld_a.set_ylabel(BESCHRIFTUNG[laerm])
    feld_a.tick_params(axis="x", labelsize=8)

    # Feld B: Balken mit dem mittleren Anteil stark belasteter Fassaden je Quintil
    anteil_spalte = "anteil_fassaden_lden_ueber_65_prozent"
    sns.barplot(data=daten, x="deprivationsquintil", y=anteil_spalte, color="darkorange", errorbar=None, ax=feld_b)
    feld_b.set_title("B  Mittlerer Anteil Fassaden über 65 dB(A) LDEN")
    feld_b.set_xlabel("Quintile des Benachteiligungsindex")
    feld_b.set_ylabel(BESCHRIFTUNG[anteil_spalte])
    feld_b.tick_params(axis="x", labelsize=8)

    # Feld C: Streudiagramm mit Regressionsgerade aus Modell A1
    a1 = modelle["A1_laerm_einfach_korrigiert"]
    a2 = modelle["A2_laerm_kontrollen_korrigiert"]
    punkte = daten[[index, laerm]].dropna()
    feld_c.scatter(punkte[index], punkte[laerm], alpha=0.4, s=12, color="steelblue")
    x_linie = np.linspace(punkte[index].min(), punkte[index].max(), 50)
    y_linie = a1.params["const"] + a1.params[index] * x_linie        # Geradengleichung y = b0 + b1 * x
    feld_c.plot(x_linie, y_linie, color="crimson", lw=2,
                label=f"A1: b = {a1.params[index]:+.2f} dB, {p_wert_text(a1.pvalues[index])}")
    feld_c.plot([], [], " ", label=f"A2 (mit Kontrollen): b = {a2.params[index]:+.2f} dB, {p_wert_text(a2.pvalues[index])}")
    feld_c.legend(fontsize=9, title="p-Werte räumlich korrigiert", title_fontsize=8)
    feld_c.set_title("C  Regression: Lärm ~ Benachteiligung")
    feld_c.set_xlabel(BESCHRIFTUNG[index])
    feld_c.set_ylabel(BESCHRIFTUNG[laerm])

    # Feld D: Antworttext (jede Zeile auf 70 Zeichen umgebrochen)
    umgebrochen = []
    for zeile in zeilen:
        umgebrochen.append(textwrap.fill(zeile, 70))
    feld_d.set_axis_off()
    feld_d.set_title("D  Antwort auf die Leitfrage", loc="left", fontweight="bold")
    feld_d.text(0, 0.98, "\n\n".join(umgebrochen), va="top", ha="left", fontsize=9.5,
                transform=feld_d.transAxes, bbox={"boxstyle": "round", "fc": "#f7f7f7", "ec": "#bbbbbb"})

    fig.suptitle("Sind sozial benachteiligte Berliner Planungsräume stärker von Lärm betroffen?",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(AUSGABE / "ergebnis_leitfrage.png", dpi=200)
    plt.close(fig)


# =============================================================================
# HAUPTPROGRAMM
# =============================================================================

def analyse_ausfuehren(datenstand):
    datenstand_konfigurieren(datenstand)
    print(f"\nDatenstand: {datenstand}")

    AUFBEREITET.mkdir(parents=True, exist_ok=True)
    AUSGABE.mkdir(parents=True, exist_ok=True)

    daten = daten_laden()
    daten = pca_benachteiligungsindex(daten)

    # Gebiete nach dem Index in 5 gleich große Gruppen (Quintile) einteilen
    daten["deprivationsquintil"] = pd.qcut(daten["benachteiligungsindex"], 5, labels=QUINTIL_NAMEN)

    deskriptive_statistik(daten)
    anova_p = anova(daten)
    modelle = regressionen(daten)
    daten["cluster"] = kmeans_clustering(daten)
    moran_tabelle = morans_i(daten, modelle)

    print("\n[8] Karten ...")
    karte_zeichnen(daten, "laerm_gesamt_lden_db", "magma_r")
    karte_zeichnen(daten, "benachteiligungsindex", "viridis")
    karte_zeichnen(daten, "angebotsmiete_median_eur_m2", "viridis")
    cluster_karte_zeichnen(daten)

    ergebnisgrafik(daten, modelle, anova_p, moran_tabelle)
    daten_speichern(daten)

    print(f"\nFertig! Ergebnisse für {datenstand} liegen in '{AUSGABE}'.")
    print("Hinweis: Beide Datenstände verwenden die Lärmkarte 2022.")
    print("Die Ergebnisse sind Zusammenhänge auf Gebietsebene,")
    print("keine Aussagen über einzelne Personen und kein Kausalitätsnachweis.")


def datenstaende_korrelieren():
    """Vergleicht gleichnamige Variablen aus beiden Läufen auf gemeinsamen Planungsräumen."""
    datei_2022 = AUFBEREITET_BASIS / "berlin_merged.csv"
    datei_aktuell = AUFBEREITET_BASIS / "aktuell" / "berlin_merged.csv"
    daten_2022 = pd.read_csv(datei_2022, dtype={"plr_id": str})
    daten_aktuell = pd.read_csv(datei_aktuell, dtype={"plr_id": str})

    vergleich = daten_2022.merge(
        daten_aktuell,
        on="plr_id",
        how="inner",
        suffixes=("_2022", "_aktuell"),
        validate="one_to_one",
    )
    variablen = [
        ("benachteiligungsindex", "Benachteiligungsindex (PCA)"),
        ("arbeitslosenanteil_prozent", "Arbeitslosenanteil S1 (%)"),
        ("alleinerziehende_prozent", "Alleinerziehendenanteil S2 (%)"),
        ("transferbezugsanteil_prozent", "Transferbezugsanteil S3 (%)"),
        ("kinderarmut_prozent", "Kinderarmut S4 (%)"),
        ("angebotsmiete_median_eur_m2", "Angebotsmiete (EUR/m²)"),
        ("einwohner", "Einwohnerzahl"),
        ("einwohnerdichte", "Einwohnerdichte (EW/km²)"),
    ]

    zeilen = []
    for spalte, bezeichnung in variablen:
        werte = vergleich[[f"{spalte}_2022", f"{spalte}_aktuell"]].apply(
            pd.to_numeric, errors="coerce"
        ).dropna()
        if len(werte) < 2:
            raise ValueError(f"Zu wenige gemeinsame Werte für die Korrelation von {bezeichnung}.")

        zeilen.append({
            "variable": bezeichnung,
            "n_planungsraeume": len(werte),
            "pearson_r": stats.pearsonr(werte.iloc[:, 0], werte.iloc[:, 1])[0],
            "spearman_rho": stats.spearmanr(werte.iloc[:, 0], werte.iloc[:, 1])[0],
        })

    tabelle = pd.DataFrame(zeilen)
    AUSGABE_BASIS.mkdir(parents=True, exist_ok=True)
    datei_ergebnis = AUSGABE_BASIS / "vergleich_zeitraeume.csv"
    tabelle.to_csv(datei_ergebnis, index=False)
    datenstaende_plotten(tabelle)
    print("\nKorrelation der Datenstände (gleiche Planungsraum-IDs):")
    print(tabelle.round(3).to_string(index=False))
    print(f"Vergleich gespeichert: {datei_ergebnis}")


def datenstaende_plotten(tabelle):
    """Zeichnet Pearson- und Spearman-Korrelationen der beiden Datenstände."""
    zeilen = np.arange(len(tabelle))
    balkenhoehe = 0.36
    beschriftungen = []
    for i in range(len(tabelle)):
        variable = tabelle.loc[i, "variable"]
        anzahl = tabelle.loc[i, "n_planungsraeume"]
        beschriftungen.append(f"{variable} (n={anzahl})")

    fig, ax = plt.subplots(figsize=(12, 7))
    pearson_balken = ax.barh(
        zeilen - balkenhoehe / 2,
        tabelle["pearson_r"],
        balkenhoehe,
        label="Pearson r",
        color="steelblue",
    )
    spearman_balken = ax.barh(
        zeilen + balkenhoehe / 2,
        tabelle["spearman_rho"],
        balkenhoehe,
        label="Spearman ρ",
        color="darkorange",
    )

    for balkenreihe in [pearson_balken, spearman_balken]:
        for balken in balkenreihe:
            wert = balken.get_width()
            if wert >= 0:
                position = wert + 0.015
                ausrichtung = "left"
            else:
                position = wert - 0.015
                ausrichtung = "right"
            ax.text(
                position,
                balken.get_y() + balken.get_height() / 2,
                f"{wert:.3f}",
                va="center",
                ha=ausrichtung,
                fontsize=8,
            )

    ax.set_yticks(zeilen, beschriftungen)
    ax.invert_yaxis()
    ax.set_xlim(-1.12, 1.12)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Korrelation zwischen den Werten je Planungsraum (2022 vs. neuester Stand)")
    ax.set_title(
        "Ähnlichkeit der Datenstände\n"
        "Sozialdaten: 2022 vs. 2024 · Angebotsmieten: 2022 vs. 2025"
    )
    ax.legend(loc="upper left")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(AUSGABE_BASIS / "vergleich_zeitraeume.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Analysiert Berliner Lärm, soziale Lage und Angebotsmieten."
    )
    parser.add_argument(
        "--datenstand",
        choices=["2022", "aktuell", "beide"],
        default="beide",
        help="2022, neueste verfügbare Daten oder beide (Standard: beide)",
    )
    argumente = parser.parse_args()

    if argumente.datenstand == "beide":
        datenstaende = ["2022", "aktuell"]
    else:
        datenstaende = [argumente.datenstand]

    for datenstand in datenstaende:
        datenstand_konfigurieren(datenstand)
        benoetigte_dateien = [
            DATEI_PLANUNGSRAEUME,
            DATEI_MSS_TABELLE_1,
            DATEI_MSS_TABELLE_2,
            DATEI_MSS_TABELLE_3,
            DATEI_MIETEN,
            DATEI_LAERM,
        ]
        fehlende_dateien = [datei for datei in benoetigte_dateien if not datei.exists()]
        if fehlende_dateien:
            print(f"Fehlende Eingabedateien für den Datenstand '{datenstand}':")
            for datei in fehlende_dateien:
                print("-", datei)
            print("Für Lärmdaten zuerst aggregate_noise.py ausführen.")
            return 1

    print("=" * 72)
    print("BERLIN DATA SCIENCE: LÄRM · SOZIALE LAGE · MIETEN")
    print("=" * 72)

    for datenstand in datenstaende:
        analyse_ausfuehren(datenstand)

    if argumente.datenstand == "beide":
        datenstaende_korrelieren()

    return 0


# Dieser Block sorgt dafür, dass main() nur startet, wenn man die Datei direkt ausführt
if __name__ == "__main__":
    raise SystemExit(main())
