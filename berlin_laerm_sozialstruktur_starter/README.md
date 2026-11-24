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
| `sozialdaten.xlsx` | MSS 2025, Tabelle 1: Einwohner, Status-/Dynamikklasse | [MSS 2025 Index-Tabellen](https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/) |
| `mss2025_indexindikatoren_anteile_plr.xlsx` | MSS 2025, Tabelle 2.1: Indikatoren S1–S4 in % | wie oben |
| `mss2025_indexindikatoren_zwerte_plr.xlsx` | MSS 2025, Tabelle 3: z-Werte und amtlicher Status-Index (Validierung der PCA) | wie oben |
| `Mietdaten.xlsx` | IBB-Angebotsmieten nach Planungsräumen 2012–2025 | [IBB Wohnungsmarktbericht 2025](https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html) |

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

Ablauf und wichtigste Ausgaben in `outputs/`:

| Schritt | Methode | Ausgaben |
|---|---|---|
| Datenqualität | Join über PLR-ID, Mietfilter, Namensabgleich | `datenqualitaet.csv`, `pruefung_namensabweichungen_ibb.csv` |
| PCA | S1–S4 standardisiert, PC1 = Benachteiligungsindex (z) | `pca_bericht.txt`, `pca_loadings.csv`, `pca_scree_ladungen.png` |
| EDA | Deskriptive Statistik, Pearson/Spearman | `descriptive_statistics.csv`, `correlation_heatmap_*.png`, `pairwise_correlations.csv` |
| Gruppenvergleich | Kruskal-Wallis, ANOVA nach Statusklasse/Quintil | `gruppenvergleich_*.csv`, `boxplot_laerm_nach_sozialer_lage.png` |
| Regression | OLS mit HC3- und geclusterten SE (Prognoseraum) | `regression_uebersicht.csv`, `regression_*.txt`, `vif_values.csv`, `regression_robustheit_miete.csv` |
| K-Means | Lärm, Benachteiligung, Miete (standardisiert) | `kmeans_*.csv`, `kmeans_*.png`, `map_kmeans_cluster.png` |
| Moran's I | Queen-Nachbarschaft, 999 Permutationen | `morans_i_uebersicht.csv` |
| Ergebnis | Antwort auf die Leitfrage | `ergebnis_leitfrage.png`, `ergebnis_zusammenfassung.txt` |

## 5. Wissenschaftliche Hinweise

- Benachteiligungsindex = PC1 der MSS-Indikatoren S1–S4; höhere Werte = stärkere Benachteiligung.
- Regressionen: HC3 korrigiert nur Heteroskedastizität. Da Lärm und Residuen räumlich
  autokorreliert sind (Moran's I), werden zusätzlich nach Prognoseraum geclusterte
  Standardfehler berichtet; diese sind für die Interpretation maßgeblich.
- Kontrollvariablen: log(1 + Einwohnerdichte) und Lage (Innere/Äußere Stadt laut LOR).
- Mietgebiete mit weniger als 21 Inseraten werden auf fehlend gesetzt (IBB-Grenze);
  Robustheit mit 10/21/30 Inseraten und Mietjahr 2022 wird geprüft.
- Mietfilter verzerrt die Stichprobe leicht: Gebiete mit hohem Status (wenige
  Mietinserate) sind im Mietmodell unterrepräsentiert.
- K-Means: k = 4 begründet gesetzt (siehe Kommentar in der Konfiguration).
- Aggregierte PLR-Daten erlauben keine individuellen Aussagen (ökologischer Fehlschluss).
- Zeitstände: Lärm 2022, MSS 2025 (Daten 31.12.2024), Mieten 2025.
- Keine Kausalitätsaussagen aus Querschnittskorrelationen ableiten.
