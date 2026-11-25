# Berlin Data Science: Lärm, soziale Lage und Mieten

## 1. Installation

Python 3.12 empfohlen (getestet).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Benötigte Daten in `data/raw/`

| Datei | Inhalt | Quelle |
|---|---|---|
| `planungsraeume.geojson` | 542 LOR-Planungsräume (Polygone, EPSG:25833) | [ODIS Berlin](https://daten.odis-berlin.de/) |
| `mss2023_gesamtindex_plr.xlsx` | MSS 2023 (Stand 31.12.2022), Tabelle 1: Einwohner, Status-/Dynamikklasse | [MSS 2023 Index-Tabellen](https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2023/tabellen-der-index-indikatoren/) |
| `mss2023_indexindikatoren_anteile_plr.xlsx` | MSS 2023, Tabelle 2.1: Indikatoren S1–S4 in % | wie oben |
| `mss2023_indexindikatoren_zwerte_plr.xlsx` | MSS 2023, Tabelle 3: z-Werte und amtlicher Status-Index (Validierung der PCA) | wie oben |
| `Mietdaten.xlsx` | IBB-Angebotsmieten nach Planungsräumen 2012–2025; verwendet wird das Blatt `Planungsräume_2022` | [IBB Wohnungsmarktbericht](https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html) |

Alle Daten beziehen sich auf das Jahr 2022 (Jahr der Lärmkarte). Die Dateien
`sozialdaten.xlsx` und `mss2025_*.xlsx` (Stand 31.12.2024) werden nicht mehr gelesen;
sie dienten nur zur Robustheitsprüfung (siehe `docs/02_daten.md`, Abschnitt 2.6).

Die Excel-Tabellen werden über die achtstellige PLR-ID erkannt; Titel- und
Fußnotenzeilen werden automatisch ignoriert. Die Spaltenpositionen stehen
oben in `berlin_data_science.py`.

## 3. Lärmdaten aggregieren

```bash
python aggregate_noise.py
```

Lädt alle ca. 3,8 Mio. Fassadenpegel des offiziellen WFS
`ua_stratlaerm_2022:aa_fp_gesamt2022` (Laufzeit mehrere Minuten, Internet nötig)
und schreibt `data/processed/laermdaten_aggregiert.csv` mit pro Planungsraum:

- `laerm_gesamt_lden_db`, `laerm_gesamt_ln_db`, `laerm_strassen_lden_db`, `laerm_strassen_ln_db`:
  energetischer Mittelwert \(10 \cdot \log_{10}(\operatorname{mean}(10^{L/10}))\)
- `laerm_gesamt_lden_median_db`, `laerm_gesamt_ln_median_db`: Median der Fassadenpegel
- `anteil_fassaden_lden_ueber_65_prozent`, `anteil_fassaden_ln_ueber_55_prozent`:
  Anteil der Fassadenpunkte über den Auslösewerten der Lärmaktionsplanung
- Anzahl der Fassadenpunkte

Der energetische Mittelwert wird stark von den lautesten Fassaden geprägt; Median
und Anteile sind robuster und werden als Robustheitscheck verwendet.

## 4. Analyse starten

```bash
python berlin_data_science.py
```

Vereinfachte Version (Branch `simplify-analysis`), an den Vorlesungsstoff angepasst.
Die ausführliche Version mit Robustheitschecks liegt auf `fix/pca-mss-analysis`.

| Schritt | Methode | Ausgaben |
|---|---|---|
| Datenqualität | Join über PLR-ID, Mietfilter, Namensabgleich | `datenqualitaet.csv`, `pruefung_namensabweichungen_ibb.csv` |
| PCA | S1–S4 standardisiert, PC1 = Benachteiligungsindex (z) | `pca_bericht.txt`, `pca_loadings.csv`, `pca_scree_ladungen.png` |
| Deskriptiv | Kennzahlen, Histogramme, Korrelationsmatrix | `descriptive_statistics.csv`, `histogramme.png`, `korrelationsmatrix.png` |
| Hypothesentest | ANOVA: Lärm nach Quintilen des Index | `anova_ergebnis.txt`, `anova_profile.csv` |
| Regression | Multiple lineare Regression (OLS), Standardfehler zusätzlich nach Prognoseraum geclustert | `regression_uebersicht.csv`, `regression_*.txt` |
| K-Means | Lärm, Benachteiligung, Miete (standardisiert), Elbow | `kmeans_*.csv`, `kmeans_elbow.png`, `map_kmeans_cluster.png` |
| Moran's I | Queen-Nachbarschaft, 999 Permutationen | `morans_i.csv` |
| Karten | Lärm, Index, Miete, Cluster | `map_*.png` |
| Ergebnis | Antwort auf die Leitfrage | `ergebnis_leitfrage.png`, `ergebnis_zusammenfassung.txt` |

## 5. Wissenschaftliche Hinweise

- Benachteiligungsindex = PC1 der MSS-Indikatoren S1–S4; höhere Werte = stärkere Benachteiligung.
- Regression: Modell A1 (Lärm ~ Index), A2 (+ Kontrollen), B (Miete ~ Lärm + Index + Kontrollen).
  Kontrollvariablen: log(1 + Einwohnerdichte) und Lage (Innere/Äußere Stadt laut LOR).
- Moran's I zeigt, dass benachbarte Planungsräume sich ähneln. Klassische p-Werte wären
  daher zu optimistisch; deshalb werden die Standardfehler nach den 58 Prognoseräumen
  geclustert. Diese räumlich korrigierten p-Werte sind maßgeblich.
- Ausführliche Dokumentation für Einsteiger: `../docs/README.md`.
- Mietgebiete mit weniger als 21 Inseraten werden auf fehlend gesetzt (IBB-Grenze).
- Mietfilter verzerrt die Stichprobe leicht: Gebiete mit hohem Status (wenige
  Mietinserate) sind im Mietmodell unterrepräsentiert.
- K-Means: k = 4 begründet gesetzt (Elbow + Interpretierbarkeit, siehe Konfiguration).
- Aggregierte PLR-Daten erlauben keine individuellen Aussagen (ökologischer Fehlschluss).
- Zeitstände einheitlich 2022: Lärm 2022, MSS 2023 (Daten 31.12.2022), Mieten 2022.
- Keine Kausalitätsaussagen aus Querschnittskorrelationen ableiten.
