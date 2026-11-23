# Berlin Data-Science Starter: Lärm, soziale Lage und Mieten

## 1. Installation

Python 3.10 oder neuer empfohlen.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Daten herunterladen und ablegen

Legt die Rohdaten in `data/raw/` ab:

- `planungsraeume.gpkg`: LOR-Planungsraum-Polygone
- `sozialdaten.xlsx`: MSS-2025-Tabelle auf Ebene der 542 Planungsräume
- `mietdaten.xlsx`: IBB-Angebotsmieten nach Planungsräumen (Excel-Tabelle, sofern verfügbar)
- `laermdaten.csv` ODER `laerm_ld_en.tif` (optional zusätzlich `laerm_ln.tif`)

Offizielle Einstiegsseiten:

- MSS 2025 Index-Tabellen: https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/
- MSS 2025 Kontext-Tabellen: https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-kontext-indikatoren-zum-bericht-2025/
- Lärmkarten 2022: https://www.berlin.de/umweltatlas/verkehr-laerm/laermbelastung/2022/download/
- LOR-Geodaten: https://daten.odis-berlin.de/
- IBB Wohnungsmarktbericht 2025: https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html
- IBB Angebotsmieten (Planungsräume): https://www.ibb.de/media/dokumente/publikationen/berliner-wohnungsmarkt/wohnungsmarktbericht/2025/ibb-wohnungsmarktbericht-angebotsmieten_2012-2025.pdf

Wichtig: Die Lärmkarten-Downloadseite bietet Karten und Raster. Für dieses Skript wird
ein GeoTIFF benötigt, nicht die PDF-Karte. Die technische Beschreibung des Berliner
WFS-Datensatzes erläutert auch Fassadenpegel. Prüft, ob ihr ein Raster oder
Fassadenpegel verwenden wollt.

## 3. Spaltennamen anpassen

Öffnet die Excel-Dateien und prüft die exakten Spaltennamen. Ändert dann in
`berlin_data_science.py` die `SOCIAL_COLUMN_MAP`, `RENT_COLUMN_MAP`,
`PLR_ID_GEO` und `PLR_NAME_GEO`.

Die Zielspalten des Skripts lauten:

- `plr_id`: achtstellige Planungsraum-ID
- `arbeitslosenanteil_prozent`: Arbeitslosenanteil in Prozent
- `transferbezugsanteil_prozent`: Transferbezugsanteil in Prozent
- `kinderarmut_prozent`: Kinderarmut in Prozent
- `angebotsmiete_median_eur_m2`: Median der Angebotsmiete in EUR/m²
- `anzahl_mietinserate`: Anzahl der Mietinserate
- `laerm_gesamt_lden_db`: Gesamt-LDEN in dB(A)
- `laerm_gesamt_ln_db`: Gesamt-LN in dB(A)
- `laerm_strassen_lden_db`: Straßenverkehr-LDEN in dB(A)
- `laerm_strassen_ln_db`: Straßenverkehr-LN in dB(A)
- `benachteiligungsindex`: ordinale soziale Benachteiligung
- `sozialstatus_index`: numerischer MSS-Statuswert
- `sozialstatus_kategorie`: MSS-Statusklasse
- `sozialdynamik_kategorie`: MSS-Dynamikklasse

Die Quellspalten der MSS-Excel-Datei können je nach Tabelle anders heißen. Nutzt
die im Skript enthaltene Fehlermeldung, die alle gefundenen Spalten ausgibt.

## 4. Lärmdaten

Die Hauptdaten werden über den Berliner WFS geladen:

```bash
python aggregate_noise.py
```

Das Skript verwendet den Feature-Type
`ua_stratlaerm_2022:aa_fp_gesamt2022` und lädt die Fassadenpegel für Gesamt-LDEN
und Nachtlärm herunter. Die Dezibelwerte werden energetisch pro Planungsraum
gemittelt:

\[
10 \cdot \log_{10}\left(\operatorname{mean}(10^{dB/10})\right)
\]

Die erzeugte Datei `data/processed/laermdaten_aggregiert.csv` enthält
Gesamt-LDEN, Nachtlärm, Straßenlärm sowie Fallzahlen. Aktuell haben alle
542 Planungsräume einen Gesamt-LDEN-Wert.

## 5. Starten

```bash
python berlin_data_science.py
```

Ergebnisse und Diagramme werden im Ordner `outputs/` gespeichert.

## 6. Wissenschaftliche Hinweise

- Pearson und Spearman berichten; Ausreißer und Nichtlinearität prüfen.
- Regressionen nutzen HC3-robuste Standardfehler.
- Mietgebiete mit weniger als 21 Inseraten werden in der Hauptanalyse auf fehlend gesetzt.
- K-Means: Features standardisieren; k anhand Elbow und Silhouette prüfen.
- Decision Tree ist explorativ und nutzt Cross-Validation.
- Moran's I prüft räumliche Autokorrelation.
- Aggregierte PLR-Daten erlauben keine individuellen Aussagen (ökologischer Fehlschluss).
- Zeitstände dokumentieren: Lärm 2022, MSS 2025 (Daten bis 2024), Mieten 2025.
- Keine Kausalitätsaussagen aus Querschnittskorrelationen ableiten.
