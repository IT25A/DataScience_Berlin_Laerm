# 5. Die Outputs: was jede Datei zeigt und wie man sie liest

Nach `python berlin_data_science.py` liegen im Ordner `outputs/` 25 Dateien. Dieses Kapitel geht sie in der Reihenfolge der Analyse durch. Für jede Datei: **Was steht drin? Wie liest man es? Was sehen wir bei uns?**

Alle Zahlen beziehen sich auf das **Bezugsjahr 2022** (Lärm 2022, Sozialdaten 31.12.2022, Mieten 2022).

## Übersicht

| Schritt | Datei | Typ |
|---|---|---|
| Datenqualität | `datenqualitaet.csv`, `pruefung_namensabweichungen_ibb.csv` | Tabelle |
| PCA | `pca_bericht.txt`, `pca_explained_variance.csv`, `pca_loadings.csv`, `pca_scree_ladungen.png` | Text, Tabelle, Grafik |
| Deskriptiv | `descriptive_statistics.csv`, `histogramme.png`, `korrelationsmatrix.png` | Tabelle, Grafik |
| ANOVA | `anova_ergebnis.txt`, `anova_profile.csv` | Text, Tabelle |
| Regression | `regression_uebersicht.csv`, `regression_A1_laerm_einfach.txt`, `regression_A2_laerm_kontrollen.txt`, `regression_B_miete.txt` | Tabelle, Text |
| K-Means | `kmeans_elbow.png`, `kmeans_cluster_profiles.csv`, `kmeans_clusters.csv`, `map_kmeans_cluster.png` | Grafik, Tabelle, Karte |
| Moran's I | `morans_i.csv` | Tabelle |
| Karten | `map_laerm_gesamt_lden_db.png`, `map_benachteiligungsindex.png`, `map_angebotsmiete_median_eur_m2.png` | Karte |
| Ergebnis | `ergebnis_leitfrage.png`, `ergebnis_zusammenfassung.txt` | Grafik, Text |

CSV-Dateien lassen sich mit Excel, LibreOffice oder pandas öffnen (Trennzeichen: Komma, Dezimalpunkt: Punkt).

---

## 5.1 Datenqualität

### `datenqualitaet.csv`
Für jede Variable: Anzahl gültiger (`gueltig`) und fehlender (`fehlend`) Werte nach allen Filtern.

**So liest man es:** Diese Datei erklärt, warum verschiedene Analysen unterschiedlich viele Gebiete verwenden.

| Variable | gültig | fehlend | Grund |
|---|---:|---:|---|
| Lärm | 542 | 0 | vollständig |
| S1–S4, Status-Index | 536 | 6 | vom MSS ausgeschlossene, fast unbewohnte Gebiete |
| Rohmiete 2022 | 518 | 24 | keine Inserate |
| Miete (gefiltert) | 341 | 201 | zusätzlich 177 Gebiete mit < 21 Inseraten |

→ Lärm-Analysen: 536 Gebiete, Miet-Analysen und K-Means: 341 Gebiete.

### `pruefung_namensabweichungen_ibb.csv`
Gebiete, deren Name in der IBB-Miettabelle anders lautet als in den offiziellen Gebietsgrenzen. 5 Treffer: 3 Schreibvarianten, 1 andere Bezeichnung und **Wittenau Mitte/Süd vertauscht** (siehe [02_daten.md](02_daten.md)).

---

## 5.2 PCA

### `pca_bericht.txt`
Kurzbericht: Anzahl Gebiete, Eigenwerte, erklärte Varianz von PC1, Ladungen, Übereinstimmung mit dem amtlichen Index.

```text
PCA über 4 MSS-Status-Indikatoren, n = 536 Planungsräume
Eigenwerte: [3.254, 0.66, 0.064, 0.03]
Erklärte Varianz PC1: 81.2%
Ladungen PC1: Arbeitslosigkeit 0.969, Alleinerziehende 0.657, Transferbezug 0.968, Kinderarmut 0.973
Übereinstimmung mit dem amtlichen MSS-Status-Index: r = 0.998
```

**So liest man es:**
- **81,2 %** → Eine einzige Zahl fasst die vier Indikatoren sehr gut zusammen. Faustregel: Ab ca. 60–70 % ist eine Hauptkomponente ein guter Index.
- **Ladungen alle positiv und hoch** → Alle Indikatoren zeigen in dieselbe Richtung; der Index misst „mehr Benachteiligung“.
- **r = 0,998** → Unser Index ist praktisch identisch mit dem amtlichen. Die Berechnung ist korrekt.

### `pca_explained_variance.csv`
Eigenwert und erklärter Varianzanteil für PC1–PC4. Die Summe der Anteile ist 100 %.

### `pca_loadings.csv`
Ladungen aller vier Komponenten. Für uns ist nur die Spalte `PC1` relevant.

### `pca_scree_ladungen.png`
Zwei Diagramme nebeneinander:
- **Links – Scree-Plot:** Balken = erklärte Varianz jeder Komponente. Ein hoher erster Balken und danach ein steiler Abfall („Geröllhalde“, englisch *scree*) zeigt: Eine Komponente reicht. Bei uns: 81,2 % → 16,5 % → 1,6 % → 0,7 %.
- **Rechts – Ladungen von PC1:** Wie stark jeder Indikator in den Index eingeht. Kinderarmut, Arbeitslosigkeit und Transferbezug fast gleich (≈ 0,97), Alleinerziehende schwächer (0,66).

**Für die Präsentation:** „Wir haben vier soziale Indikatoren mit einer PCA zu einem Benachteiligungsindex zusammengefasst. Die erste Komponente erklärt 81 % der Varianz und stimmt mit dem offiziellen Index des Senats zu 99,8 % überein.“

---

## 5.3 Deskriptive Statistik

### `descriptive_statistics.csv`
Pro Variable: `count` (Anzahl), `mean` (Mittelwert), `std` (Standardabweichung), `min`, `25%` (1. Quartil), `50%` (Median), `75%` (3. Quartil), `max`, `variance` (Varianz).

| Variable | Mittel | SD | Min | Median | Max |
|---|---:|---:|---:|---:|---:|
| Lärm LDEN (dB) | 57,3 | 3,6 | 46,4 | 57,4 | 73,2 |
| Fassaden > 65 dB (%) | 6,5 | 6,9 | 0 | 5,3 | 100 |
| Benachteiligungsindex | 0,0 | 1,0 | −1,9 | −0,21 | 3,5 |
| S1 Arbeitslosigkeit (%) | 4,3 | 2,4 | 0,4 | 3,9 | 15,3 |
| S2 Alleinerziehende (%) | 26,4 | 6,8 | 8,4 | 25,6 | 50,2 |
| S3 Transferbezug (%) | 10,5 | 6,5 | 0,9 | 8,7 | 37,0 |
| S4 Kinderarmut (%) | 22,4 | 14,5 | 0,4 | 19,2 | 67,9 |
| Miete 2022 (EUR/m²) | 11,8 | 4,1 | 5,4 | 11,2 | 27,1 |
| Einwohnerdichte (EW/km²) | 9.893 | 7.599 | 0 | 8.582 | 36.290 |

**So liest man es:**
- Liegen Mittelwert und Median nah beieinander (Lärm, Miete), ist die Verteilung symmetrisch.
- Ist der Mittelwert deutlich größer als der Median (Kinderarmut, Transferbezug, Dichte), gibt es einige Gebiete mit sehr hohen Werten → **rechtsschiefe** Verteilung.
- Der Index hat per Konstruktion Mittel 0 und SD 1.

### `histogramme.png`
Neun Histogramme. Die x-Achse zeigt die Werte, die y-Achse die Anzahl der Planungsräume („Count“). Die Linie ist eine geglättete Form der Verteilung.

**Was wir sehen:**
- **Lärm:** schöne Glockenform um 57 dB, wenige Ausreißer nach oben (bis 73 dB) → Voraussetzung für ANOVA und Regression gut erfüllt.
- **Fassaden > 65 dB:** die meisten Gebiete zwischen 0 und 15 %, einzelne Ausreißer (100 % = Pankower Tor mit nur 17 Punkten).
- **Sozialindikatoren und Index:** rechtsschief – die meisten Gebiete sind durchschnittlich, einige wenige stark benachteiligt.
- **Einwohnerdichte:** stark rechtsschief → Grund für den Logarithmus in der Regression.

### `korrelationsmatrix.png`
Heatmap aller paarweisen Pearson-Korrelationen. Jede Zelle zeigt r für die Kombination aus Zeile und Spalte. Rot = positiv, blau = negativ, weiß = kein Zusammenhang. Die Diagonale ist immer 1 (jede Variable mit sich selbst).

**Was wir sehen:**
- **Rotes Quadrat in der Mitte:** Index und S1–S4 korrelieren stark (0,66–0,97) → deshalb ist eine PCA sinnvoll.
- **Lärm – Index: 0,08** → praktisch kein linearer Zusammenhang (erster Hinweis zu H1).
- **Miete – Lärm: +0,42**, **Miete – Index: −0,51** → mittlere Zusammenhänge (erster Hinweis zu H2).
- **Lärm – Fassaden > 65 dB: 0,80** → beide Lärmmaße messen Ähnliches.

**Achtung:** Die Korrelationsmatrix ist nur ein Überblick. Korrelationen berücksichtigen keine anderen Einflüsse; das macht erst die Regression.

---

## 5.4 ANOVA

### `anova_profile.csv`
Pro Quintil: Anzahl (`count`), Mittelwert, Median, SD des Lärms.

| Quintil | n | Mittel (dB) | Median (dB) | SD |
|---|---:|---:|---:|---:|
| Q1 (geringste Benachteiligung) | 108 | 55,3 | 55,1 | 3,4 |
| Q2 | 107 | 58,8 | 58,7 | 4,0 |
| Q3 | 107 | 57,7 | 58,0 | 3,1 |
| Q4 | 107 | 57,4 | 57,8 | 3,2 |
| Q5 (stärkste Benachteiligung) | 107 | 57,3 | 57,8 | 3,5 |

(In der CSV steht in den Gruppennamen ein Zeilenumbruch `\n` – das ist für die Achsenbeschriftung der Grafik gedacht.)

### `anova_ergebnis.txt`
F-Wert und p-Wert: **F = 14,27, p < 0,001**.

**So liest man es:**
1. p < 0,05 → Die fünf Gruppen haben **nicht** alle denselben mittleren Lärm.
2. Dann in die Tabelle schauen, **wo** der Unterschied liegt: Q1 ist 2,5 dB leiser als der Durchschnitt von Q2–Q5. Q2 bis Q5 unterscheiden sich untereinander kaum (max. 1,5 dB).
3. Schlussfolgerung: Nicht „je ärmer, desto lauter“, sondern „die Wohlhabendsten wohnen leiser“.

Zur Einordnung: Ein Unterschied von 2,5 dB ist hörbar, aber nicht groß (zum Vergleich: Halbierung des Verkehrs = −3 dB).

---

## 5.5 Regression

### `regression_uebersicht.csv`
**Die wichtigste Tabelle der Regression.** Eine Zeile pro Koeffizient.

| Spalte | Bedeutung |
|---|---|
| `modell` | A1, A2 oder B |
| `zielvariable` | was erklärt wird (Lärm oder Miete) |
| `term` | Einflussvariable |
| `koeffizient` | geschätzter Effekt (β) |
| `std_fehler_ols`, `p_wert_ols` | klassischer Standardfehler und p-Wert (zum Vergleich) |
| `std_fehler_cluster`, `p_wert_cluster` | **räumlich korrigiert (maßgeblich)** |
| `n` | Anzahl Gebiete im Modell |
| `r2` | Bestimmtheitsmaß R² |

Unsere Werte:

| Modell | Term | β | p (klassisch) | p (korrigiert) | R² |
|---|---|---:|---:|---:|---:|
| A1 | Benachteiligung | +0,285 | 0,068 | **0,318** | 0,006 |
| A2 | Benachteiligung | +0,267 | 0,086 | **0,215** | 0,225 |
| A2 | log(Dichte) | −0,038 | 0,825 | 0,881 | 0,225 |
| A2 | Innere Stadt | +3,585 | < 0,001 | **< 0,001** | 0,225 |
| B | Lärm | +0,268 | < 0,001 | **< 0,001** | 0,512 |
| B | Benachteiligung | −1,770 | < 0,001 | **< 0,001** | 0,512 |
| B | log(Dichte) | −0,153 | 0,479 | 0,399 | 0,512 |
| B | Innere Stadt | +3,240 | < 0,001 | **< 0,001** | 0,512 |

**So liest man es – Schritt für Schritt am Beispiel A2, Benachteiligung:**
1. **Vorzeichen:** + → mehr Benachteiligung geht mit mehr Lärm einher.
2. **Größe:** 0,27 dB pro Standardabweichung Benachteiligung → sehr klein, nicht hörbar.
3. **p-Wert (korrigiert):** 0,215 > 0,05 → nicht signifikant. Der kleine Effekt kann gut Zufall sein.
4. **Fazit:** Kein belastbarer Zusammenhang.

**Und am Beispiel A2, Innere Stadt:** +3,58 dB, p < 0,001 → Innenstadtgebiete sind bei gleicher Benachteiligung und Dichte deutlich lauter. Die **Lage** ist der stärkste Einflussfaktor auf den Lärm.

**R² vergleichen:** A1 erklärt nur 0,6 % der Lärmunterschiede, A2 22,5 % – fast der ganze Zuwachs kommt von „Innere Stadt“. Modell B erklärt 51 % der Mietunterschiede.

**Klassisch vs. korrigiert:** Die Koeffizienten sind gleich, die korrigierten p-Werte bei den Lärmmodellen deutlich größer. Wichtig: Ohne Korrektur läge A1 mit p = 0,068 knapp an der 5-%-Grenze; mit Korrektur (p = 0,318) bleibt davon nichts übrig. An der Entscheidung „signifikant / nicht signifikant“ ändert sich bei keiner Variable etwas.

### `regression_A1_laerm_einfach.txt`, `regression_A2_laerm_kontrollen.txt`, `regression_B_miete.txt`
Die vollständigen Ergebnistabellen von statsmodels. Jede Datei enthält **zwei Tabellen**: oben die räumlich korrigierte (maßgeblich), unten die klassische (zum Vergleich).

**Wie liest man so eine Tabelle?**

Ausschnitt aus `regression_A2_laerm_kontrollen.txt` (räumlich korrigierte Tabelle):

```text
                             OLS Regression Results
================================================================================
Dep. Variable:     laerm_gesamt_lden_db   R-squared:                       0.225
Model:                              OLS   Adj. R-squared:                  0.220
Method:                   Least Squares   F-statistic:                     20.61
No. Observations:                   536   Prob (F-statistic):           3.60e-09
Covariance Type:                cluster
=========================================================================================
                            coef    std err          z      P>|z|      [0.025      0.975]
-----------------------------------------------------------------------------------------
const                    56.3945      2.109     26.737      0.000      52.260      60.529
benachteiligungsindex     0.2673      0.216      1.240      0.215      -0.155       0.690
log_einwohnerdichte      -0.0380      0.254     -0.150      0.881      -0.536       0.460
innere_stadt              3.5849      0.676      5.305      0.000       2.260       4.909
```

| Feld | Bedeutung |
|---|---|
| `Dep. Variable` | Zielvariable (abhängige Variable) |
| `R-squared` | Bestimmtheitsmaß R² |
| `Adj. R-squared` | R², leicht nach unten korrigiert für die Zahl der Variablen |
| `No. Observations` | Anzahl der Gebiete im Modell |
| `Covariance Type` | `cluster` = räumlich korrigiert, `nonrobust` = klassisch |
| `F-statistic`, `Prob (F-statistic)` | Test, ob das Modell **insgesamt** etwas erklärt (hier ja: p = 3,6·10⁻⁹ – wegen „Innere Stadt“, nicht wegen der Benachteiligung) |
| `coef` | Koeffizient β |
| `std err` | Standardfehler |
| `z` (bzw. `t`) | coef / std err; ab einem Betrag über 1,96 signifikant |
| `P>\|z\|` | p-Wert |
| `[0.025  0.975]` | Bereich, in dem der wahre Wert mit 95 % Sicherheit liegt. **Enthält er die 0, ist der Effekt nicht signifikant.** |
| `const` | Achsenabschnitt: erwarteter Wert, wenn alle Einflussvariablen 0 sind (hier rein rechnerisch, ohne eigene Bedeutung) |

Beispiel „benachteiligungsindex“: coef 0,2673 / std err 0,216 = z 1,24 < 1,96 → p = 0,215 → nicht signifikant; das 95-%-Intervall [−0,155; 0,690] enthält die 0.
Beispiel „innere_stadt“: z = 5,31 → p < 0,001 → signifikant; das Intervall [2,3; 4,9] dB liegt klar über 0.

Die Zeilen unter der Koeffiziententabelle (Omnibus, Durbin-Watson usw.) sind weitere Diagnosen, die wir nicht auswerten.

---

## 5.6 K-Means

### `kmeans_elbow.png`
Liniendiagramm: x-Achse = Anzahl Cluster k (1–8), y-Achse = Inertia. Die gestrichelte Linie markiert das gewählte k = 4.

**So liest man es:** Man sucht den „Ellenbogen“, ab dem die Kurve flach wird. Bei uns flacht sie zwischen k = 3 und k = 4 ab; danach bringen weitere Cluster nur noch wenig. k = 4 wurde zusätzlich wegen der guten Interpretierbarkeit gewählt.

### `kmeans_cluster_profiles.csv`
Pro Cluster: Name, Anzahl Gebiete, mittlerer Lärm, mittlerer Index, mittlere Miete 2022 (in Originaleinheiten).

| Cluster | Anzahl | Lärm (dB) | Index | Miete (EUR/m²) |
|---|---:|---:|---:|---:|
| C1: Lärm niedrig · Benachteiligung hoch · Miete niedrig | 74 | 54,6 | +1,15 | 7,64 |
| C2: Lärm niedrig · Benachteiligung niedrig · Miete mittel | 90 | 55,6 | −0,69 | 11,67 |
| C3: Lärm hoch · Benachteiligung hoch · Miete niedrig | 88 | 59,9 | +0,82 | 10,18 |
| C4: Lärm hoch · Benachteiligung niedrig · Miete hoch | 89 | 60,5 | −0,51 | 16,81 |

**So liest man es:** Jeder Cluster ist ein „typisches Gebiet“. Die Bezeichnungen „hoch/niedrig“ sind relativ zum Berliner Durchschnitt.
- **C1** – benachteiligt, aber leise: typischerweise Großsiedlungen am Stadtrand (Plattenbau, Hochhaussiedlungen mit viel Grün zwischen den Häusern).
- **C2** – wohlhabend und leise: Einfamilienhaus- und Villengebiete am Stadtrand.
- **C3** – **benachteiligt und laut**: dicht bebaute Quartiere der Innenstadt und innenstadtnahe Gebiete mit vielen Hauptstraßen. Das ist die **mehrfach belastete** Gruppe im Sinne der Umweltgerechtigkeit.
- **C4** – wohlhabend, laut und teuer: beliebte Innenstadtlagen.

### `kmeans_clusters.csv`
Zuordnung jedes der 341 Gebiete (`plr_id`, `plr_name`) zu seinem Cluster. Nützlich, um nachzuschlagen, wo ein bestimmter Kiez landet.

### `map_kmeans_cluster.png`
Berlin-Karte, jedes Gebiet in der Farbe seines Clusters, Bezirksgrenzen schwarz, Bezirksnamen eingeblendet. Graue Gebiete sind nicht geclustert (Miete oder Sozialdaten fehlen) – 2022 sind das 201 Gebiete, vor allem am Stadtrand.

**Was wir sehen:**
- **Rosa (C4)** bildet den Innenstadtkern (Charlottenburg, Mitte, Prenzlauer Berg, Friedrichshain).
- **Blau (C3)** liegt neben diesem Kern: Wedding (Osloer Straße, Parkviertel), Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte, Teile Nord-Neuköllns.
- **Grün (C1)** liegt in Inseln am Stadtrand: Marzahn-Hellersdorf, Neu-Hohenschönhausen, Gropiusstadt, Märkisches Viertel.
- **Orange (C2)** dominiert die äußeren Bezirke (Steglitz-Zehlendorf, Treptow-Köpenick, Pankow-Nord).

Die Karte zeigt auf einen Blick: Laut und benachteiligt sind **bestimmte Innenstadtquartiere**, nicht „die armen Gebiete“ insgesamt.

---

## 5.7 Moran's I

### `morans_i.csv`

| Variable | n | I | p_sim |
|---|---:|---:|---:|
| Lärm | 542 | 0,465 | 0,001 |
| Benachteiligungsindex | 536 | 0,435 | 0,001 |
| Residuen A1 | 536 | 0,474 | 0,001 |
| Residuen A2 | 536 | 0,306 | 0,001 |

**So liest man es:**
- **I zwischen 0,3 und 0,5** → deutliche räumliche Clusterung: Ähnliche Werte liegen nebeneinander.
- **p_sim = 0,001** → kleinstmöglicher Wert bei 999 Permutationen; keine einzige Zufallsmischung erreichte ein so hohes I. Man schreibt korrekt „p ≤ 0,001“.
- **Residuen:** Auch die Fehler der Regression sind räumlich gehäuft → die klassischen p-Werte wären zu optimistisch → deshalb die geclusterten Standardfehler. Durch die Kontrollvariablen sinkt I von 0,47 auf 0,31: Die Lage erklärt einen Teil der räumlichen Struktur, aber nicht alles.

---

## 5.8 Karten

Alle Karten sind **Choroplethenkarten**: Jedes Gebiet ist nach seinem Wert eingefärbt; die Farbskala steht rechts. Schwarze Linien = Bezirksgrenzen, hellgrau = kein Wert.

### `map_laerm_gesamt_lden_db.png`
Farbskala von hellgelb (leise, ~46 dB) bis dunkelviolett/schwarz (laut, ~73 dB).

**Was wir sehen:** Ein klares **Zentrum-Rand-Gefälle**: Die Innenstadt ist dunkel (laut), der Stadtrand hell (leise). Die lautesten Gebiete liegen in Mitte/Tiergarten (Hansaviertel, Lüneburger Straße). Einzelne laute Streifen folgen großen Verkehrsachsen. Das passt zum starken Effekt von „Innere Stadt“ in der Regression und zu Moran's I = 0,46.

### `map_benachteiligungsindex.png`
Farbskala von dunkelviolett (wenig benachteiligt, ~−1,9) bis gelb (stark benachteiligt, ~+3,5).

**Was wir sehen:** Benachteiligung konzentriert sich in zwei Arten von Gebieten:
1. **Innenstadtnah:** Wedding/Gesundbrunnen, Moabit, Nord-Neukölln, Kreuzberg-Nord,
2. **Stadtrand:** Großsiedlungen in Marzahn-Hellersdorf, Spandau, Märkisches Viertel, Gropiusstadt.

Der Südwesten (Steglitz-Zehlendorf) und der Südosten (Köpenick) sind wenig benachteiligt. **Genau deshalb gibt es keinen linearen Zusammenhang mit Lärm:** Ein Teil der benachteiligten Gebiete liegt im lauten Zentrum, ein anderer im leisen Stadtrand – die beiden Effekte heben sich im Durchschnitt auf.

### `map_angebotsmiete_median_eur_m2.png`
Farbskala von dunkel (günstig, ~5,4 EUR/m²) bis gelb (teuer, ~27 EUR/m²); grau = weniger als 21 Inserate im Jahr 2022.

**Was wir sehen:** Die höchsten Mieten in Mitte, Charlottenburg, Prenzlauer Berg und Friedrichshain-Kreuzberg; die niedrigsten in den Großsiedlungen am Stadtrand. Viele graue Flächen = Gebiete mit wenigen Mietinseraten (2022 deutlich mehr als in späteren Jahren).

---

## 5.9 Das Endergebnis

### `ergebnis_leitfrage.png`
**Die zentrale Grafik für die Präsentation.** Vier Felder:

**Feld A – Boxplot: Lärm nach Benachteiligungs-Quintil**
- Jede Box zeigt die Lärmverteilung eines Quintils: Die Box reicht vom 1. bis 3. Quartil (mittlere 50 % der Gebiete), der Strich in der Box ist der Median, die „Antennen“ (Whisker) zeigen die Spannweite ohne Ausreißer.
- Die rote Linie verbindet die Mittelwerte.
- Titel: ANOVA p < 0,001.
- **Lesart:** Q1 (links) liegt sichtbar tiefer, Q2–Q5 liegen fast auf einer Höhe. Die Boxen überlappen stark → die Unterschiede sind klein im Vergleich zur Streuung innerhalb der Gruppen.

**Feld B – Balken: Anteil Fassaden über 65 dB je Quintil**
- **Lesart:** Gleiches Muster mit einem anschaulicheren Maß: In Q1 sind im Mittel ca. 3 % der Fassaden stark belastet, in Q2–Q5 ca. 6–8 %. Am stärksten belastet ist Q2 (8,4 %), nicht Q5 (6,6 %).

**Feld C – Streudiagramm mit Regressionsgerade**
- Jeder Punkt = ein Planungsraum (x = Benachteiligung, y = Lärm).
- Rote Linie = Regressionsgerade aus Modell A1.
- Legende: Koeffizienten und **räumlich korrigierte** p-Werte von A1 und A2.
- **Lesart:** Die Punktwolke hat keine erkennbare Richtung, die Gerade ist fast waagerecht (+0,29 dB pro SD). Die p-Werte (0,318 und 0,215) zeigen: kein signifikanter Zusammenhang.

**Feld D – Antworttext**
Automatisch aus den Ergebnissen erzeugter Text mit allen Kernaussagen (Inhalt siehe unten).

### `ergebnis_zusammenfassung.txt`
Derselbe Antworttext wie in Feld D, zum Kopieren:

```text
H1 nicht gestützt: Kein signifikanter linearer Zusammenhang zwischen Benachteiligung und Lärm.
A1: +0.29 dB pro SD Benachteiligung, R² = 0.006, p = 0.318 (räumlich korrigiert; ohne Korrektur p = 0.068).
    A2 (mit Dichte und Lage): +0.27 dB, p = 0.215 (ohne Korrektur p = 0.086).
Mittlerer Lärm je Quintil: 55.3 | 58.8 | 57.7 | 57.4 | 57.3 dB (Q1→Q5), ANOVA p < 0.001. Die am wenigsten
    benachteiligten Gebiete (Q1) sind 2.5 dB leiser; zwischen Q2 und Q5 liegen nur 1.5 dB → kein Gradient.
H2: Miete steigt um +0.27 EUR/m² pro dB (p < 0.001) und sinkt um 1.77 EUR/m² pro SD Benachteiligung (p < 0.001).
H3: 4 Gebietstypen; 88 von 341 PLR (26%) sind zugleich laut und benachteiligt (Mehrfachbelastung).
Räumlich: Lärm I = 0.46, Residuen A2 I = 0.31 → Standardfehler nach Prognoseraum geclustert.
```

Die ausführliche Deutung steht in [06_ergebnis.md](06_ergebnis.md).

---

## 5.10 Aufbereitete Daten (`data/processed/`)

| Datei | Inhalt | Nutzung |
|---|---|---|
| `laermdaten_aggregiert.csv` | Lärmkennzahlen pro PLR (Ergebnis von `aggregate_noise.py`) | Eingabe für die Analyse |
| `laermdaten_aggregiert.geojson` | dasselbe mit Geometrie | optional, z. B. für QGIS |
| `berlin_merged.csv` | alle Variablen pro PLR inkl. Index, Quintil und Cluster | eigene Auswertungen in Excel/pandas |
| `berlin_merged.gpkg` | dasselbe mit Geometrie | eigene Karten in QGIS |
