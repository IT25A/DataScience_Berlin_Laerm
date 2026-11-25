# Environmental Justice in Berlin – Projekt-Rekapitulation

**Stand:** 24. November 2026 (überarbeitet nach Code- und Datenreview)

**Projekt:** Quantifying Environmental Justice: Eine räumliche Data-Science-Analyse von Verkehrslärm, sozialer Deprivation und Wohnkosten in Berlin

**Arbeitsverzeichnis:** `berlin_laerm_sozialstruktur_starter`

---

## 1. Projektidee und Ziel

Dieses Projekt untersucht, ob sozial benachteiligte Berliner Planungsräume tendenziell stärker von Lärm betroffen sind und wie Lärm, soziale Lage und Angebotsmieten räumlich zusammenhängen.

Die Hauptfrage lautet:

> Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von Lärmbelastung betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

Das Projekt soll nicht einzelne Personen oder Haushalte bewerten. Die räumliche Analyseebene sind die Berliner LOR-Planungsräume. Aussagen beziehen sich daher auf Gebiete und nicht auf einzelne Menschen.

Die zentrale Hypothese lautet:

- **H1:** Planungsräume mit einer ungünstigeren sozialen Lage weisen höhere Lärmwerte auf.
- **H2:** Lärm hängt mit Angebotsmieten zusammen.
- **H3:** Planungsräume lassen sich anhand von Lärm, sozialer Lage und Mietniveau in interpretierbare Gebietstypen gruppieren.

Das Projekt ist als Querschnittanalyse aufgebaut. Alle Daten stammen aus dem Bezugsjahr 2022:

- Lärm: 2022
- Soziale Lage: MSS 2023, Datenstand 31.12.2022
- Mieten: IBB 2022

Alle Daten beziehen sich damit auf das Jahr der Lärmkarte (2022). Eine Prüfung mit neueren Daten (MSS Stand 31.12.2024, Mieten 2025) ergibt dieselben Aussagen.

Eine zeitlich exakte Längsschnittanalyse wäre deshalb nicht möglich. Die Ergebnisse beschreiben räumliche Zusammenhänge zum jeweiligen Datenstand.

---

## 2. Wissenschaftlicher Ansatz

Der Analyseablauf ist bewusst mehrstufig aufgebaut:

1. Datenbeschaffung
2. Daten- und Geometrieprüfung (inkl. Namensabgleich)
3. Vereinheitlichung der LOR-Planungsraum-ID
4. Verknüpfung von Lärm, sozialer Lage und Mietdaten
5. **PCA** über die vier MSS-Status-Indikatoren → Benachteiligungsindex
6. Deskriptive Statistik
7. Korrelationsmatrix (Überblick)
8. ANOVA (Hypothesentest)
9. Multiple lineare Regression
10. K-Means-Clustering
11. Räumliche Autokorrelation nach Moran
12. Karten und Ergebnisgrafik

Die Kombination dieser Methoden entspricht dem Umfang eines Data-Science-Moduls:

- Erwartungswert, Median, Varianz und Standardabweichung
- Verteilungen und Ausreißer
- Standardisierung und Hauptkomponentenanalyse
- Hypothesentests (ANOVA)
- multiple lineare Regression
- K-Means-Clustering (Elbow-Methode)
- räumliche Abhängigkeit (Moran's I)
- Kartendarstellung

Der wissenschaftliche Kern liegt nicht in der Anzahl der Algorithmen, sondern darin, dass Datenqualität, räumliche Einheit, Aggregation und Limitationen sauber dokumentiert werden.

---

## 3. Verwendete Datenpakete

## 3.1 Berliner LOR-Planungsräume

**Datei:** `data/raw/planungsraeume.geojson` (ODIS Berlin / Geoportal Berlin)

- 542 Planungsräume, Polygone, achtstellige LOR-ID, CRS EPSG:25833
- 542 gültige und eindeutige Geometrien
- Gebietsstand laut Datei: 2021; MSS nutzt LOR 01/2023 – alle 542 IDs und Namen stimmen überein
- enthält zusätzlich Prognoseraum (`pgr_id`, 58 Gruppen), Bezirk und `stadtraum_name` (Innere/Äußere Stadt)

---

## 3.2 Strategische Lärmkarte 2022

**Offizieller WFS:** https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022, Feature-Type `ua_stratlaerm_2022:aa_fp_gesamt2022`

- 3.799.746 Fassadenpegelpunkte, davon 3.799.712 per räumlichem Join den 542 PLR zugeordnet (34 liegen exakt auf Grenzen)
- Felder `ges_den`, `ges_n` (Gesamt), `str_den`, `str_n` (Straße), `sch_*` (Tram/U-Bahn oberirdisch), `flg_*` (Flug)
- Aggregation wurde im Review stichprobenartig direkt gegen den WFS nachgerechnet und exakt reproduziert

**Kennzahlen pro Planungsraum** (`data/processed/laermdaten_aggregiert.csv`):

| Kennzahl | Mittelwert | Min | Max |
|---|---:|---:|---:|
| LDEN energetisch gemittelt | 57,3 dB | 46,4 | 73,2 |
| LDEN Median der Fassaden | 47,3 dB | 34,9 | 68,5 |
| Anteil Fassaden > 65 dB LDEN | 6,5 % | 0 | 100 |

Energetische Mittelung:

\[
L_{\text{PLR}} = 10 \cdot \log_{10}\left(\frac{1}{n}\sum_{i=1}^{n}10^{L_i/10}\right)
\]

**Wichtig:** Über verschiedene Fassaden gemittelt wird der energetische Mittelwert von den lautesten Fassaden dominiert (Beispiel Hansaviertel: energetisch 73,0 dB, Median 63,8 dB). Deshalb werden Median und der Anteil der Fassaden über dem Auslösewert der Lärmaktionsplanung (65 dB LDEN) als Robustheitsmaße mitgeführt. Fassadenpunkte sind kein bevölkerungsgewichtetes Expositionsmaß; sie liegen auch an Nicht-Wohngebäuden (z. B. Pankower Tor mit 0 Einwohnern).

---

## 3.3 MSS-Sozialdaten 2023 (Stand 31.12.2022)

**Quelle:** https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2023/tabellen-der-index-indikatoren/

| Datei | Tabelle | Inhalt |
|---|---|---|
| `mss2023_gesamtindex_plr.xlsx` | 1 | Einwohner, Status-Klasse (1–4), Dynamik-Klasse |
| `mss2023_indexindikatoren_anteile_plr.xlsx` | 2.1 | S1 Arbeitslosigkeit, S2 Alleinerziehende, S3 Transferbezug, S4 Kinderarmut (in %) |
| `mss2023_indexindikatoren_zwerte_plr.xlsx` | 3 | z-Werte und stetiger amtlicher Status-Index (nur zur Validierung) |

**Korrektur gegenüber der früheren Fassung:** Die Einzelindikatoren sind offiziell verfügbar (Tabelle 2.1). Der frühere ordinale Score (1–4) wurde durch einen PCA-Index ersetzt.

- 536 PLR mit Werten; 6 PLR ohne Werte sind vom MSS ausgeschlossen (0–1.320 Einwohner, z. B. Pankower Tor, Gewerbegebiet Bitterfelder Straße) – korrekt

---

## 3.4 IBB-Angebotsmieten

**Datei:** `data/raw/Mietdaten.xlsx`, Blatt `Planungsräume_2022` (gleiches Jahr wie die Lärmkarte)
**Quelle:** https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html

- 518 PLR mit Median, 24 ohne Inserate („keine Daten“)
- 177 PLR mit < 21 Inseraten → auf fehlend gesetzt (IBB-eigene Repräsentativitätsgrenze) → **341 PLR**
- **Selektionseffekt:** Von den 86 PLR mit hohem Status fehlen 52 im Mietmodell (Einfamilienhausgebiete mit wenigen Inseraten); Anteil sinkt von 16 % auf 10 %
- Mieten 2025 (434 PLR mit Mietwert) ergeben dieselben Aussagen (Robustheitsprüfung)
- **Datenauffälligkeit:** Bei `12500926` / `12500930` sind „Wittenau Mitte“ und „Wittenau Süd“ gegenüber Geometrie und MSS vertauscht benannt (`outputs/pruefung_namensabweichungen_ibb.csv`); drei weitere Abweichungen sind reine Schreibvarianten

**Limitation:** Angebotsmieten ≠ tatsächlich gezahlte Bestandsmieten.

---

## 3.5 Nicht verwendete Daten

- `strassenverteilung.csv`, `laerm_strassen_lden.geojson`: keine dB-Werte
- `data/raw/laerm_fassadenpegel2022.geojson`: enthält trotz Namens **Wohngebäude-Polygone** (`ab_wohngebaeude2022`), keine Pegel; wird nicht verwendet (könnte für eine Bevölkerungsgewichtung genutzt werden)
- `data/current/`: ältere Kopien

---

## 4. Datenverknüpfung

Alle Datensätze werden über die achtstellige PLR-ID mit `validate="one_to_one"` verknüpft. Excel-Zeilen werden über ein Muster `\d{8}` erkannt, sodass Kopf- und Fußnotenzeilen ignoriert werden.

- 542 Planungsräume, 542 Lärmwerte
- 536 vollständige Lärm-/Sozial-Fälle
- 341 vollständige Lärm-/Sozial-/Miet-Fälle

Ausgaben: `data/processed/berlin_merged.csv`, `berlin_merged.gpkg` (inkl. Index, Quintil, Cluster), `outputs/datenqualitaet.csv`

---

## 5. PCA: Benachteiligungsindex

- Eingangsvariablen: S1–S4, z-standardisiert, n = 536
- Eigenwerte: 3,25 / 0,66 / 0,06 / 0,03 → eine dominierende Komponente
- **PC1 erklärt 81,2 %** der Varianz
- Ladungen PC1: Kinderarmut 0,97, Arbeitslosigkeit 0,97, Transferbezug 0,97, Alleinerziehende 0,66
- **Validierung:** Korrelation r = 0,998 mit dem amtlichen MSS-Status-Index
- Index z-standardisiert (Mittel 0, SD 1); höhere Werte = stärkere Benachteiligung

Ausgaben: `pca_bericht.txt`, `pca_loadings.csv`, `pca_explained_variance.csv`, `pca_scree_ladungen.png`

---

## 6. Deskriptive Statistik und Korrelationsmatrix

Kennzahlen (Mittelwert, Median, Quartile, Varianz) und Histogramme aller Analysevariablen; die Korrelationsmatrix dient nur als Überblick (z. B. Miete–Lärm r = 0,42, Benachteiligung–Miete r = −0,51, Benachteiligung–Lärm r = 0,08).

Ausgaben: `descriptive_statistics.csv`, `histogramme.png`, `korrelationsmatrix.png`

---

## 7. ANOVA: Lärm nach Benachteiligungs-Quintilen

| Gruppe | Q1 (geringste) | Q2 | Q3 | Q4 | Q5 (stärkste) |
|---|---:|---:|---:|---:|---:|
| Mittlerer LDEN [dB] | 55,3 | 58,8 | 57,7 | 57,4 | 57,3 |

- ANOVA: F = 14,27, p < 0,001 → die Quintile unterscheiden sich
- **Muster:** Die am wenigsten benachteiligten Gebiete sind rund 2,5 dB leiser. Zwischen Q2 und Q5 gibt es kaum Unterschiede (1,5 dB) und keinen ansteigenden Verlauf

Ausgaben: `anova_ergebnis.txt`, `anova_profile.csv`

---

## 8. Multiple lineare Regression

Kontrollvariablen: log(1 + Einwohnerdichte), Innere Stadt (0/1). Koeffizient des Index = Effekt pro Standardabweichung Benachteiligung. Die Standardfehler werden zusätzlich nach den 58 Prognoseräumen geclustert (räumliche Korrektur, siehe §10); diese p-Werte sind maßgeblich.

| Modell | Zielvariable | b Benachteiligung | p (OLS) | p (räumlich korrigiert) | b Lärm | p (korrigiert) | R² | n |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | Lärm | +0,29 dB | 0,068 | **0,318** | – | – | 0,006 | 536 |
| A2 | Lärm (+ Kontrollen) | +0,27 dB | 0,086 | **0,215** | – | – | 0,225 | 536 |
| B | Miete 2022 (+ Kontrollen) | −1,77 EUR/m² | < 0,001 | **< 0,001** | +0,27 EUR/m² pro dB | < 0,001 | 0,512 | 341 |

- **A1/A2:** Kein signifikanter linearer Effekt der Benachteiligung auf Lärm. Ohne räumliche Korrektur läge A1 knapp an der Grenze (p = 0,068) – mit Korrektur bleibt davon nichts. Die Lage (Innere Stadt: +3,6 dB, p < 0,001) erklärt den Großteil der Lärmunterschiede.
- **B:** Lärm und Benachteiligung hängen beide hochsignifikant mit der Miete zusammen; die Innere Stadt ist +3,2 EUR/m² teurer. Lageeffekt, nicht kausal. Mit Mieten 2025: +0,24 EUR/m² pro dB, −1,98 EUR/m² pro SD.

Ausgaben: `regression_uebersicht.csv`, `regression_A1_laerm_einfach.txt`, `regression_A2_laerm_kontrollen.txt`, `regression_B_miete.txt`

---

## 9. K-Means-Clustering

Merkmale (standardisiert): LDEN, Benachteiligungsindex, Angebotsmiete 2022; n = 341.

**Gewählt: k = 4** (Elbow-Plot `kmeans_elbow.png`): Die Inertia sinkt bis k = 4 deutlich (1023 → 629 → 480 → 387) und danach nur noch langsam. k = 4 liefert zudem eine interpretierbare Typologie aus laut/leise und benachteiligt/wohlhabend.

| Cluster | n | LDEN | Index | Miete | Typische Lage |
|---|---:|---:|---:|---:|---|
| C1 Lärm niedrig · Benachteiligung hoch · Miete niedrig | 74 | 54,6 | +1,15 | 7,6 | Großsiedlungen: Marzahn-Hellersdorf (20), Lichtenberg (12), Neukölln-Süd (12), Spandau (11), z. B. Gropiusstadt, Neu-Hohenschönhausen, Märkisches Viertel |
| C2 Lärm niedrig · Benachteiligung niedrig · Miete mittel | 90 | 55,6 | −0,69 | 11,7 | Äußere Stadt: Pankow (19), Steglitz-Zehlendorf (16), Treptow-Köpenick (14) |
| C3 Lärm hoch · Benachteiligung hoch · Miete niedrig | 88 | 59,9 | +0,82 | 10,2 | Mitte/Wedding (17), Tempelhof-Schöneberg (12), Spandau (10), Treptow-Köpenick (10), z. B. Osloer Straße, Moabit-West, Spandau-Mitte |
| C4 Lärm hoch · Benachteiligung niedrig · Miete hoch | 89 | 60,5 | −0,51 | 16,8 | Charlottenburg-Wilmersdorf (24), Pankow/Prenzlauer Berg (17), Mitte (16), Friedrichshain-Kreuzberg (14) |

26 % der geclusterten PLR (C3) sind zugleich laut und benachteiligt (**Mehrfachbelastung**).

Ausgaben: `map_kmeans_cluster.png`, `kmeans_cluster_profiles.csv`, `kmeans_clusters.csv`, `kmeans_elbow.png`

---

## 10. Moran's I (Queen, 999 Permutationen, Seed 42)

| Variable | I | p_sim |
|---|---:|---:|
| LDEN | 0,46 | ≤ 0,001 |
| Benachteiligungsindex | 0,43 | ≤ 0,001 |
| Residuen A1 | 0,47 | ≤ 0,001 |
| Residuen A2 (mit Kontrollen) | 0,31 | ≤ 0,001 |

Lärm und Benachteiligung sind stark räumlich geclustert: Benachbarte Planungsräume ähneln sich. Auch die Residuen der Regression sind räumlich abhängig (die Kontrollvariablen senken I von 0,47 auf 0,31). Die Beobachtungen sind also nicht völlig unabhängig, und klassische OLS-p-Werte wären zu optimistisch. **Korrektur:** Die Standardfehler werden nach den 58 Prognoseräumen geclustert. Dadurch steigen sie (A1: 0,16 → 0,29), die p-Werte werden größer (A1: 0,068 → 0,318). Die Aussagen bleiben gleich: H1 nicht signifikant, H2 hochsignifikant.

---

## 11. Karten und Visualisierung

- `ergebnis_leitfrage.png`: Quintil-Boxplot (ANOVA), Anteil > 65 dB, Regressions-Scatterplot und Antworttext
- `map_kmeans_cluster.png`: Berlin-Karte der Gebietstypen mit Bezirksgrenzen
- `map_laerm_gesamt_lden_db.png`, `map_benachteiligungsindex.png`, `map_angebotsmiete_median_eur_m2.png`
- `histogramme.png`, `korrelationsmatrix.png`, `pca_scree_ladungen.png`, `kmeans_elbow.png`

---

## 12. Stärken und Schwächen

**Stärken**
- Offizielle, verifizierte Quellen; Lärmaggregation unabhängig reproduziert
- Benachteiligungsindex per PCA gebildet und gegen den amtlichen Index validiert
- Methoden am Vorlesungsstoff orientiert und vollständig erklärbar
- Räumliche Abhängigkeit mit Moran's I geprüft und in den Standardfehlern korrigiert

**Schwächen**
- Querschnitt (Bezugsjahr 2022, nicht der neueste Stand; neuere Daten ergeben dieselben Aussagen)
- Mietdaten 2022 nur für 341 PLR verlässlich
- Fassadenpunkte nicht bevölkerungsgewichtet
- Mietfilter unterrepräsentiert Gebiete mit hohem Status
- Wittenau-Namensvertauschung in der IBB-Tabelle ungeklärt
- Residuen räumlich abhängig (korrigiert über geclusterte Standardfehler; die ANOVA ist nicht räumlich korrigiert)
- Keine Robustheitschecks mit alternativen Lärmmaßen oder Mietschwellen (nur in der ausführlichen Version)

---

## 13. Technischer Stand

```text
aggregate_noise.py  -> WFS (3,8 Mio. Punkte) -> laermdaten_aggregiert.csv
berlin_data_science.py -> Join -> PCA -> Deskriptiv -> ANOVA -> Regression
                        -> K-Means -> Moran -> Karten -> ergebnis_leitfrage.png
```

```bash
cd berlin_laerm_sozialstruktur_starter
python aggregate_noise.py      # optional, mehrere Minuten
python berlin_data_science.py  # ca. 1 Minute
```

Getestet mit Python 3.12 und den in `requirements.txt` gepinnten Versionen. Die Ergebnisse sind reproduzierbar (feste Seeds).

---

## 14. Aufräumliste

Erledigt am 24.11.2026: `data/current/`, `laerm_strassen_lden.geojson`, `laerm_fassadenpegel2022.geojson`, `laerm_capabilities.xml` und veraltete Outputs wurden gelöscht.

**Unbedingt behalten** (werden vom Skript gelesen):
- `data/raw/planungsraeume.geojson`, `mss2023_gesamtindex_plr.xlsx`, `mss2023_indexindikatoren_anteile_plr.xlsx`, `mss2023_indexindikatoren_zwerte_plr.xlsx`, `Mietdaten.xlsx`
- Optional zur Robustheitsprüfung: `sozialdaten.xlsx`, `mss2025_*.xlsx` (Stand 31.12.2024)
- `data/processed/laermdaten_aggregiert.csv`

---

## 15. Mögliche Erweiterungen (optional)

1. Fassadenpunkte auf Wohngebäude beschränken (Bevölkerungsbezug)
2. LISA-Karte für lokale Hot-/Coldspots
3. Räumliches Regressionsmodell (Spatial Error/Lag) als Ausblick

---

## 16. Endgültiges Projektfazit

**Antwort auf die Leitfrage:**

- **H1 nicht gestützt:** In Berlin gibt es auf Ebene der Planungsräume **keinen signifikanten linearen Zusammenhang** zwischen sozialer Benachteiligung und Lärm (+0,27 dB pro SD; mit Kontrollvariablen und räumlicher Korrektur p = 0,22).
- **Nichtlineares Muster (ANOVA p < 0,001):** Die am wenigsten benachteiligten Gebiete sind etwa 2,5 dB leiser. Darüber hinaus gilt „je ärmer, desto lauter“ nicht, denn die am stärksten benachteiligten Großsiedlungen am Stadtrand sind vergleichsweise leise.
- **H2 gestützt:** Lauter ist teurer (+0,27 EUR/m² pro dB), benachteiligt ist günstiger (−1,77 EUR/m² pro SD; Mieten 2022). Das ist ein Lageeffekt und keine Kausalität.
- **H3 gestützt:** Vier interpretierbare Gebietstypen. **26 % der PLR sind zugleich laut und benachteiligt** (v. a. Wedding, Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte). Umweltungerechtigkeit ist also kein stadtweiter Trend, sondern ein **räumlich konzentriertes Problem bestimmter innenstadtnaher Quartiere**.
- **Bezugsjahr:** Alle Daten aus 2022 (Jahr der Lärmkarte). Mit Sozialdaten 2024 und Mieten 2025 ergeben sich dieselben Aussagen.
- Lärm und Benachteiligung sind stark räumlich geclustert (Moran's I ≈ 0,4–0,5). Das wird über geclusterte Standardfehler berücksichtigt; an den Aussagen ändert die Korrektur nichts.
