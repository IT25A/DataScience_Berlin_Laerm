# Environmental Justice in Berlin – Projekt-Rekapitulation (ausführliche Version)

**Stand:** 25. November 2026 · **Branch:** `fix/pca-mss-analysis` (mit allen Robustheitsprüfungen)

**Projekt:** Quantifying Environmental Justice: Eine räumliche Data-Science-Analyse von Verkehrslärm, sozialer Deprivation und Wohnkosten in Berlin

---

## 1. Leitfrage und Hypothesen

> Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von Lärmbelastung betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

- **H1:** Benachteiligte Planungsräume weisen höhere Lärmwerte auf.
- **H2:** Lärm hängt mit Angebotsmieten zusammen.
- **H3:** Planungsräume lassen sich nach Lärm, Benachteiligung und Miete in interpretierbare Gebietstypen gruppieren.

Analyseeinheit: 542 LOR-Planungsräume (PLR). Aussagen gelten für Gebiete, nicht für Personen.

## 2. Bezugsjahr 2022

Alle Daten beziehen sich auf das Jahr der Lärmkarte (erscheint nur alle 5 Jahre; nächste 2027):

| Datensatz | Verwendet | Robustheitsprüfung |
|---|---|---|
| Lärm | Strategische Lärmkarte 2022 (WFS, 3,8 Mio. Fassadenpunkte) | – |
| Soziale Lage | MSS 2023, Stand **31.12.2022** (Tabellen 1, 2.1, 3) | MSS 2025 (Stand 31.12.2024): gleiche Aussagen |
| Mieten | IBB **2022** (Blatt `Planungsräume_2022`) | IBB 2025: siehe §7 |

Stabilität: Sozialindex Ende 2022 vs. Ende 2024 r = 0,988; Mieten 2022 vs. 2025 Rangkorrelation 0,84 (Niveau +37 %).

## 3. Daten und Aufbereitung

- **Gebietsgrenzen:** `planungsraeume.geojson` (542 PLR, EPSG:25833, Prognoseraum, Innere/Äußere Stadt)
- **Lärm:** `aggregate_noise.py` – energetischer Mittelwert LDEN pro PLR (Mittel 57,3 dB, 46,4–73,2), Median, Anteil Fassaden > 65 dB; stichprobenartig gegen den WFS reproduziert
- **MSS 2023:** S1 Arbeitslosigkeit, S2 Alleinerziehende, S3 Transferbezug, S4 Kinderarmut; 536 PLR mit Werten (6 vom MSS ausgeschlossen, 0–1.320 Einwohner)
- **IBB 2022:** 518 PLR mit Median, 24 ohne Inserate, 177 mit < 21 Inseraten → **341 PLR** mit Mietwert. Selektionseffekt: Von 86 PLR mit hohem Status fehlen 52 (Anteil 16 % → 10 %)
- **Namensabgleich:** 5 Abweichungen in der IBB-Tabelle, darunter Wittenau Mitte/Süd vertauscht (`pruefung_namensabweichungen_ibb.csv`)
- Verknüpfung über achtstellige PLR-ID mit `validate="one_to_one"`; Kontrollvariablen log(1 + Einwohnerdichte) und Innere Stadt (0/1)

## 4. PCA: Benachteiligungsindex

- n = 536; Bartlett-Test Chi² = 2933, p < 0,001; Eigenwerte 3,25 / 0,66 / 0,06 / 0,03
- **PC1 erklärt 81,2 %**; Ladungen: Kinderarmut 0,97, Arbeitslosigkeit 0,97, Transferbezug 0,97, Alleinerziehende 0,66
- Validierung: r = 0,998 mit amtlichem MSS-Status-Index; ρ = 0,84 mit Statusklasse
- Index z-standardisiert; höher = stärker benachteiligt

## 5. Korrelationen und Gruppenvergleich

| Paar | n | Pearson r | p | Spearman ρ | p |
|---|---:|---:|---:|---:|---:|
| Benachteiligung – LDEN | 536 | 0,08 | 0,068 | 0,15 | 0,001 |
| Benachteiligung – Straßenlärm | 536 | 0,19 | < 0,001 | 0,22 | < 0,001 |
| Benachteiligung – LDEN Median | 536 | −0,09 | 0,047 | −0,08 | 0,058 |
| Benachteiligung – Anteil > 65 dB | 536 | 0,09 | 0,039 | 0,16 | < 0,001 |
| Miete – LDEN | 341 | 0,42 | < 0,001 | 0,41 | < 0,001 |
| Benachteiligung – Miete | 341 | −0,51 | < 0,001 | −0,56 | < 0,001 |

Diese p-Werte berücksichtigen keine räumliche Abhängigkeit und sind zu optimistisch.

| Quintil | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---:|---:|---:|---:|---:|
| Mittlerer LDEN [dB] | 55,3 | 58,8 | 57,7 | 57,4 | 57,3 |

Kruskal-Wallis und ANOVA p < 0,001 (Quintile und MSS-Klasse). Q1 ist 2,5 dB leiser, Q2–Q5 liegen innerhalb von 1,5 dB. Nach MSS-Klasse: hoch 55,1 · mittel 57,9 · niedrig 57,6 · sehr niedrig 57,0 dB.

## 6. Regression Lärm (Effekt pro SD Benachteiligung)

| Modell | Ziel | Koeff. | 95 %-KI | p | R² |
|---|---|---:|---|---:|---:|
| A1 | LDEN, HC3 | +0,29 | [−0,02; 0,59] | 0,067 | 0,006 |
| A2 | LDEN, Cluster-SE (Prognoseraum) | +0,29 | [−0,27; 0,84] | 0,318 | 0,006 |
| A3 | LDEN + Kontrollen | +0,27 | [−0,16; 0,69] | 0,215 | 0,225 |
| A4 | Median-LDEN + Kontrollen | +0,24 | [−0,13; 0,61] | 0,196 | 0,101 |
| A5 | Anteil > 65 dB + Kontrollen | +0,49 %-Pkt. | [−0,12; 1,09] | 0,116 | 0,250 |
| A6 | Straßenlärm + Kontrollen | +0,42 | [−0,03; 0,88] | 0,067 | 0,229 |

Innere Stadt (A3): +3,6 dB [2,3; 4,9], p < 0,001. **Kein Modell zeigt einen signifikanten Effekt der Benachteiligung.** Mit HC3 allein (A1) und beim Straßenlärm (A6) liegt p knapp über 0,05 – mit räumlich geclusterten Standardfehlern verschwindet diese scheinbare Tendenz (A2: p = 0,318). VIF aller Modelle < 1,8.

## 7. Regression Miete

| Modell | b Lärm [EUR/m² pro dB] | b Benachteiligung [EUR/m² pro SD] | R² | n |
|---|---:|---:|---:|---:|
| B1 (HC3) | +0,46 (p < 0,001) | −2,00 (p < 0,001) | 0,41 | 341 |
| B2 (+ Kontrollen, Cluster-SE) | +0,27 (p < 0,001) | −1,77 (p < 0,001) | 0,51 | 341 |

Innere Stadt (B2): +3,2 EUR/m². **Robustheit (B2):**

| Variante | n | b Lärm | b Benachteiligung | R² |
|---|---:|---:|---:|---:|
| Mindestfallzahl 10 | 464 | +0,22 | −1,75 | 0,48 |
| Mindestfallzahl 21 (Haupt) | 341 | +0,27 | −1,77 | 0,51 |
| Mindestfallzahl 30 | 257 | +0,28 | −1,79 | 0,54 |
| **Mieten 2025**, Mindestfallzahl 21 | 434 | +0,24 | −1,98 | 0,53 |

Alle p < 0,001 – das Ergebnis ist stabil. Euro-Beträge gelten jeweils für ihr Mietjahr.

## 8. K-Means (k = 4)

Merkmale (standardisiert): LDEN, Index, Miete 2022; n = 341. Silhouette k = 2…7: 0,344 / 0,306 / 0,300 / 0,291 / 0,272 / 0,281. k = 2 trennt nur „benachteiligt/günstig“ von „wohlhabend/teuer“; k = 4 (Silhouette 0,30) ergibt eine interpretierbare Typologie.

| Cluster | n | LDEN | Index | Miete | Typische Lage |
|---|---:|---:|---:|---:|---|
| C1 Lärm niedrig · Benachteiligung hoch · Miete niedrig | 74 | 54,6 | +1,15 | 7,6 | Großsiedlungen: Marzahn-Hellersdorf, Neu-Hohenschönhausen, Gropiusstadt, Märkisches Viertel |
| C2 Lärm niedrig · Benachteiligung niedrig · Miete mittel | 90 | 55,6 | −0,69 | 11,7 | Äußere Stadt: Pankow, Steglitz-Zehlendorf, Treptow-Köpenick |
| C3 Lärm hoch · Benachteiligung hoch · Miete niedrig | 88 | 59,9 | +0,82 | 10,2 | Wedding, Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte |
| C4 Lärm hoch · Benachteiligung niedrig · Miete hoch | 89 | 60,5 | −0,51 | 16,8 | Charlottenburg, Mitte, Prenzlauer Berg, Friedrichshain |

26 % der geclusterten PLR sind zugleich laut und benachteiligt.

## 9. Moran's I (Queen, 999 Permutationen)

| Variable | n | I | p_sim |
|---|---:|---:|---:|
| LDEN | 542 | 0,46 | ≤ 0,001 |
| Benachteiligungsindex | 536 | 0,43 | ≤ 0,001 |
| Miete 2022 | 341 | 0,49 | ≤ 0,001 |
| Residuen A1 | 536 | 0,47 | ≤ 0,001 |
| Residuen A3 | 536 | 0,31 | ≤ 0,001 |

Starke räumliche Clusterung → geclusterte Standardfehler sind maßgeblich. (Bei der Miete entstehen durch fehlende Gebiete 5 Inseln ohne Nachbarn.)

## 10. Stärken und Schwächen

**Stärken:** offizielle, verifizierte Quellen; einheitliches Bezugsjahr; PCA-Index validiert; räumliche Abhängigkeit geprüft und korrigiert; Robustheit über Lärmmaße, Mietschwellen und Mietjahre.

**Schwächen:** Querschnitt; Fassadenpunkte nicht einwohnergewichtet; Mieten 2022 nur für 341 PLR; Gebiete mit hohem Status im Mietmodell unterrepräsentiert; Wittenau-Vertauschung ungeklärt; Residuen auch mit Kontrollen räumlich abhängig.

## 11. Technisches

```bash
cd berlin_laerm_sozialstruktur_starter
python aggregate_noise.py      # optional, mehrere Minuten
python berlin_data_science.py
```

Benötigte Rohdaten: `planungsraeume.geojson`, `mss2023_gesamtindex_plr.xlsx`, `mss2023_indexindikatoren_anteile_plr.xlsx`, `mss2023_indexindikatoren_zwerte_plr.xlsx`, `Mietdaten.xlsx`; dazu `data/processed/laermdaten_aggregiert.csv`.

## 12. Fazit

- **H1 nicht gestützt:** Kein signifikanter linearer Zusammenhang zwischen Benachteiligung und Lärm (+0,27 dB pro SD, p = 0,22 mit Kontrollen und Cluster-SE); gilt für alle Lärmmaße.
- **Nichtlineares Muster:** Nur die am wenigsten benachteiligten Gebiete sind ca. 2,5 dB leiser; kein „je ärmer, desto lauter“.
- **H2 gestützt:** Lauter ist teurer (+0,27 EUR/m² pro dB), benachteiligt ist günstiger (−1,77 EUR/m² pro SD) – Lageeffekt, keine Kausalität; robust über Mietschwellen und Mietjahr 2025.
- **H3 gestützt:** Vier Gebietstypen; 26 % der PLR laut und benachteiligt, konzentriert in innenstadtnahen Quartieren (Wedding, Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte).
- Lärm und Benachteiligung sind räumlich stark geclustert; die Korrektur ändert keine Aussage, beseitigt aber scheinbare Tendenzen.
