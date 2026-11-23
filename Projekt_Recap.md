# Environmental Justice in Berlin – Projekt-Rekapitulation

**Stand:** 23. November 2026

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

Das Projekt ist als Querschnittanalyse aufgebaut. Die Daten stammen nicht alle aus exakt demselben Jahr:

- Lärm: 2022
- Soziale Lage: MSS 2025, Datenstand überwiegend 31.12.2024
- Mieten: IBB 2025

Eine zeitlich exakte Längsschnittanalyse wäre deshalb nicht möglich. Die Ergebnisse beschreiben räumliche Zusammenhänge zum jeweiligen Datenstand.

---

## 2. Wissenschaftlicher Ansatz

Der Analyseablauf ist bewusst mehrstufig aufgebaut:

1. Datenbeschaffung
2. Daten- und Geometrieprüfung
3. Vereinheitlichung der LOR-Planungsraum-ID
4. Verknüpfung von Lärm, sozialer Lage und Mietdaten
5. Deskriptive Statistik
6. Pearson- und Spearman-Korrelation
7. robuste lineare Regression
8. K-Means-Clustering
9. räumliche Autokorrelation nach Moran
10. Kartenexport und Diagrammerstellung

Die Kombination dieser Methoden entspricht dem Umfang eines Data-Science-Moduls:

- Erwartungswert, Median, Varianz und Standardabweichung
- Verteilungen und Ausreißer
- Korrelationsanalyse
- lineare Regression
- Standardisierung
- K-Means-Clustering
- räumliche Abstände und Nachbarschaften
- räumliche Statistik
- Kartendarstellung

Der Wissenschaftlerische Kern liegt nicht in der Anzahl der Algorithmen, sondern darin, dass Datenqualität, räumliche Einheit, Aggregation und Limitationen sauber dokumentiert werden.

---

## 3. Verwendete Datenpakete

## 3.1 Berliner LOR-Planungsräume

**Datei im Projekt:**  
`data/raw/planungsraeume.geojson`

**Eigenschaften:**

- 542 Planungsräume
- Polygone
- achtstellige LOR-ID
- CRS EPSG:25833
- 542 gültige und eindeutige Geometrien
- keine leeren oder ungültigen Polygone
- Gebietsstand laut Datei: 2021

Die Datei enthält neben Geometrie auch:

- `plr_id`
- `plr_name`
- Bezirks-ID und Bezirksname
- Prognoserraum-ID und Prognoserraumname
- Bezirk
- Stadtteil- beziehungsweise Raumzuordnung
- Datenstand

Diese Daten bilden die gemeinsame räumliche Ebene des Projekts.

**Quellen zur Beschaffung:**

- ODIS Berlin: https://daten.odis-berlin.de/
- Berliner Geoportal: https://gdi.berlin.de/

---

## 3.2 Strategische Lärmkarte 2022

**Offizieller WFS:**  
https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022

**Feature-Type:**  
`ua_stratlaerm_2022:aa_fp_gesamt2022`

**Abgerufene Hauptfelder:**

- `importid`
- `x`
- `y`
- `ges_den`: Gesamt-LDEN in dB(A)
- `ges_n`: Gesamt-LN in dB(A)
- `str_den`: Straßenverkehr-LDEN
- `str_n`: Straßenverkehr-LN
- `sch_den`: Straßenbahn und oberirdische U-Bahn
- `sch_n`: Nachtwert für Straßenbahn und oberirdische U-Bahn
- `flg_den`: Flugverkehr-LDEN
- `flg_n`: Flugverkehr-LN

Der WFS enthält 3.799.746 Fassadenpegelpunkte.

Die Punkte wurden per räumlichem Join den 542 Planungsraum-Polygonen zugeordnet.

**Aggregierte Projektdateien:**

- `data/processed/laermdaten_aggregiert.csv`
- `data/processed/laermdaten_aggregiert.geojson`

**Ergebnisqualität:**

- alle 542 Planungsräume besitzen einen Gesamt-LDEN-Wert
- Gesamt-LDEN-Mittelwert: 57,33 dB(A)
- Gesamt-LDEN-Minimum: 46,41 dB(A)
- Gesamt-LDEN-Median: 57,37 dB(A)
- Gesamt-LDEN-Maximum: 73,25 dB(A)

Die Dezibelwerte wurden **energetisch gemittelt**:

\[
L_{\text{PLR}} = 10 \cdot \log_{10}\left(
\frac{1}{n}\sum_{i=1}^{n}10^{L_i/10}
\right)
\]

Dies ist wichtig, weil ein einfacher arithmetischer Mittelwert von Dezibelwerten nicht den physikalischen Gesamtlärm korrekt repräsentiert.

Die Daten sind damit deutlich stärker als die zuvor verwendeten Straßennetzlängen oder ein Linienlängen-Proxy. Die Aggregation ist aber weiterhin kein individuelles Expositionsmaß für Bewohnerinnen und Bewohner. Jeder Punkt repräsentiert einen gemessenen beziehungsweise bewerteten Fassadenpunkt, nicht eine Person oder einen Haushalt.

**WFS-Quelle:**

- [Berliner Umweltatlas – Strategische Lärmkarten 2022](https://www.berlin.de/umweltatlas/verkehr-laerm/laermbelastung/2022/download/)
- [WFS Capabilities](https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022)

---

## 3.3 MSS-Sozialdaten

**Datei im Projekt:**  
`data/raw/sozialdaten.xlsx`

**Tabellenblatt:**  
`1.SDI_PLR_MSS2025`

**Offizielle Datenquelle:**  
https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/

Die Datei enthält:

- 542 Planungsräume
- 542 eindeutige IDs
- Einwohnerzahl
- Statusindex
- Statuskategorie
- Dynamikkategorie
- kombinierte Status-Dynamik-Klasse

Die vorhandene Datei enthält nicht die ursprünglich angenommenen Einzelindikatoren:

- Arbeitslosigkeit
- Transferbezugsquote
- Kinderarmut

Daher wurde keine PCA über diese drei Einzelindikatoren berechnet.

Im aktuellen Projekt wird stattdessen der MSS-Status als Deprivationsvariable verwendet.

Die Kategorien wurden in einen ordinalen Score umgewandelt:

| MSS-Kategorie | Deprivationswert |
|---|---:|
| Hoch | 1 |
| Mittel | 2 |
| Niedrig | 3 |
| Sehr niedrig | 4 |

Die Kategorie wirkt hier als vereinfachter Deprivationsindikator. Höhere Werte bedeuten eine ungünstigere soziale Lage.

**Qualität:**

- 542 gültige Planungsraumzeilen
- 542 eindeutige IDs
- 7 fehlende Statuswerte
- 535 Planungsräume in der Deprivations-Lärm-Regression

Die Daten entsprechen der vorliegenden offiziellen MSS-Tabellenstruktur. Für eine wissenschaftlich differenzierte PCA wären einzelne soziale Kontextindikatoren notwendig.

---

## 3.4 IBB-Angebotsmieten

**Datei im Projekt:**  
`data/raw/Mietdaten.xlsx`

**Tabellenblatt:**  
`Planungsräume_2025`

**Offizielle Datenquelle:**  
https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html

Die Tabelle enthält pro Planungsraum:

- ID
- Name
- Median-Angebotsmiete 2025
- Anzahl der Inserate
- arithmetisches Mittel der Angebotsmiete

**Qualität:**

- 542 nicht leere Medianwerte
- 542 Fallzahlen
- 88 Planungsräume mit weniger als 21 Inseraten
- Mindestfallzahl: 3
- maximale Fallzahl: 374

Planungsräume mit weniger als 21 Inseraten wurden in der Hauptanalyse auf fehlenden Mietwert gesetzt. Dadurch bleiben 434 Planungsräume für das vollständige Mietmodell.

Der Schwellenwert von 21 ist eine bewusste Annahme zur Stabilisierung kleiner Stichproben. Ein späterer Robustheitscheck sollte diesen Wert variieren, beispielsweise:

- Mindestfallzahl 10
- Mindestfallzahl 21
- Mindestfallzahl 30

**Wichtige Limitation:** Angebotsmieten sind nicht mit den tatsächlich von Haushalten gezahlten Nettokaltmieten identisch. Die Daten beschreiben den betrachteten Angebotsmarkt und nicht individuelle Mietbelastung.

---

## 3.5 Entfernte oder nicht verwendete Daten

Die folgenden Daten sind nicht Bestandteil der belastbaren Hauptanalyse:

- `strassenverteilung.csv`
- `laerm_strassen_lden.geojson`
- alte Proxy-Aggregation aus Linienlängen
- 404-Datei `laerm_fassadenpegel2022.txt`
- alte XML- oder GPKG-Fehlerdateien

Die Straßendaten enthalten keine dB-Werte und sind daher kein Ersatz für Lärminformationen.

Die Datei `laerm_strassen_lden.geojson` enthält den Verlauf bewerteter Straßen, aber keine Pegel.

Die frühere CSV-Aggregation mit Kilometerwerten wurde durch echte Fassadenpegel ersetzt und darf nicht als Lärmvariable interpretiert werden.

---

## 4. Datenverknüpfung

Die Daten werden über die Planungsraum-ID zusammengeführt:

```text
Planungsraumgeometrie
        +
MSS-Sozialdaten
        +
IBB-Mietdaten
        +
WFS-Fassadenpegel
        =
berlin_merged
```

Die Planungsraum-ID wird bei jedem Datensatz auf acht Stellen normalisiert:

```text
01100101
01100102
...
```

Die Zusammenführung verwendet `validate="one_to_one"`. Damit wird verhindert, dass doppelte IDs die Datensätze vervielfachen.

**Ergebnis des finalen Joins:**

- 542 Planungsräume
- 542 Lärmwerte
- 535 vollständige Lärm-/Deprivations-Fälle
- 434 vollständige Miet-/Lärm-/Deprivations-Fälle

Die zusammengeführten Dateien sind:

- `data/processed/berlin_merged.csv`
- `data/processed/berlin_merged.gpkg`

---

## 5. Deskriptive Statistik

Die Deskriptive Analyse umfasst:

- Anzahl gültiger Beobachtungen
- Mittelwert
- Median
- Minimum
- Maximum
- Standardabweichung
- Varianz
- Quartile
- Histogramme
- Boxplots

Die wichtigsten Ausgabedateien sind:

- `outputs/descriptive_statistics.csv`
- `outputs/boxplots.png`
- `outputs/hist_laerm_gesamt_lden_db.png`
- `outputs/hist_angebotsmiete_median_eur_m2.png`

Die Mietdaten sind aufgrund kleiner Fallzahlen teilweise unvollständig. Die fehlenden Mietwerte werden nicht durch Mittelwerte ersetzt.

---

## 6. Korrelationsanalyse

Für die Analyse werden Pearson- und Spearman-Korrelationen verwendet.

## 6.1 Deprivation und Lärm

- Beobachtungen: 535
- Pearson: \(r = 0.102\)
- Pearson-p-Wert: 0.0185
- Spearman: \(\rho = 0.190\)
- Spearman-p-Wert: ungefähr 0.000010

Interpretation:

- Die Richtung ist positiv.
- Ein höherer Deprivationswert geht tendenziell mit höherem Lärm einher.
- Die lineare Pearson-Korrelation ist schwach.
- Der etwas stärkere Spearman-Wert deutet auf einen monotone, möglicherweise nichtlineare Komponente hin.

Die Hypothese H1 wird daher schwach unterstützt.

## 6.2 Miete und Lärm

- Beobachtungen: 434
- Pearson: \(r = 0.384\)
- Pearson-p-Wert: sehr klein
- Spearman: \(\rho = 0.386\)

Höhere Angebotsmieten treten tendenziell in Planungsräumen mit höherem Lärm auf. Dieser Zusammenhang ist nicht automatisch durch Lärm verursacht. Er kann zentrale Lageeffekte, Infrastruktur, Arbeitsplätzen oder Innenstadtlage widerspiegeln.

## 6.3 Deprivation und Miete

- Beobachtungen: 434
- Pearson: \(r = -0.382\)
- Spearman: \(\rho = -0.353\)

Höhere Deprivation geht tendenziell mit niedrigeren Angebotsmieten einher.

Die Ausgabedatei ist:

- `outputs/pairwise_correlations.csv`

---

## 7. Lineare Regression

Die Modelle verwenden heteroskedastizitätsrobuste HC3-Standardfehler.

## 7.1 Modell A: Lärm erklärt durch Deprivation

\[
\mathrm{Lärm}_i =
\beta_0 +
\beta_1 \cdot \mathrm{Deprivation}_i +
\epsilon_i
\]

Ergebnis:

- Fallzahl: 535
- Deprivationskoeffizient: 0.473
- HC3-Konfidenzintervall: 0.060 bis 0.886
- p-Wert: 0.0247
- \(R^2 = 0.010\)
- bereinigtes \(R^2 = 0.009\)

Interpretation:

- Der Koeffizient ist positiv und statistisch signifikant.
- Jede Zunahme um eine Einheit des ordinalen Deprivationsscores geht im unbereinigten Modell mit etwa 0,47 dB(A) mehr Gesamt-LDEN einher.
- Das Modell erklärt nur 1 % der Lärmvariation.

Die kleine erklärte Varianz zeigt, dass Lärm durch viele weitere Faktoren bestimmt wird.

## 7.2 Modell B: Angebotsmiete erklärt durch Lärm und Deprivation

\[
\mathrm{Miete}_i =
\beta_0 +
\beta_1 \cdot \mathrm{Lärm}_i +
\beta_2 \cdot \mathrm{Deprivation}_i +
\epsilon_i
\]

Ergebnis:

- Fallzahl: 434
- Lärmkoeffizient: 0.513
- Deprivationskoeffizient: -2.441
- \(R^2 = 0.305\)
- bereinigtes \(R^2 = 0.302\)

Interpretation:

- Bei gleicher Deprivation ist ein höherer Lärmwert mit höheren Angebotsmieten verbunden.
- Bei gleichem Lärm sind stärker benachteiligte Gebiete mit niedrigeren Mieten verbunden.
- Das Modell ist stärker als das reine Lärmmodell, kann aber keinen kausalen Effekt belegen.

Die Ausgabedateien sind:

- `outputs/regression_laerm_erklart.txt`
- `outputs/regression_laerm_erklart_coefficients.csv`
- `outputs/regression_angebotsmiete_erklart.txt`
- `outputs/regression_angebotsmiete_erklart_coefficients.csv`

---

## 8. VIF und Multikollinearität

Für das Mietmodell wurden VIF-Werte berechnet:

| Variable | VIF |
|---|---:|
| Deprivation | 1.010 |
| Lärm | 1.010 |

Die beiden Prädiktoren sind nicht problematisch kollinear.

Ausgabedatei:

- `outputs/vif_values.csv`

---

## 9. K-Means-Clustering

Die Merkmale wurden standardisiert:

- Gesamt-LDEN
- Deprivationsindex
- Angebotsmiete

Für \(k=2\) bis \(k=7\) wurden:

- Inertia
- Silhouette Score
- Clusterprofile
- Clustergrößen

berechnet.

**Modelauswahl:**

| k | Silhouette |
|---:|---:|
| 2 | 0.332 |
| 3 | 0.356 |
| 4 | 0.316 |
| 5 | 0.294 |
| 6 | 0.324 |
| 7 | 0.324 |

Die endgültige Clusterzahl ist \(k=3\), da dieser Wert den höchsten Silhouette Score hat.

## Clusterprofile

| Cluster | Mittlerer Lärm dB(A) | Mittlere Deprivation | Mittlere Miete EUR/m² |
|---:|---:|---:|---:|
| 0 | 55.32 | 1.79 | 13.22 |
| 1 | 56.97 | 3.57 | 10.39 |
| 2 | 60.10 | 1.98 | 18.71 |

Interpretation:

- Cluster 0: relativ moderate Lärmwerte und mittlere soziale Lage
- Cluster 1: stärkere Deprivation und niedrigere Mietwerte
- Cluster 2: höhere Lärmwerte und deutlich höhere Mietwerte

Diese Clusterbildung beschreibt Gebietstypen, keine gesellschaftlich bindenden Kategorien.

Ausgabedateien:

- `outputs/kmeans_model_selection.csv`
- `outputs/kmeans_cluster_profiles.csv`
- `outputs/kmeans_clusters.csv`
- `outputs/kmeans_clusters.png`

---

## 10. Räumliche Analyse nach Moran

Für die räumliche Nachbarschaft wurde eine Queen-Nachbarschaft verwendet.

## 10.1 Moran's I für Lärm

- \(I = 0.4647\)
- simulierter p-Wert: 0.001
- kein Inselproblem

Der Lärm zeigt eine starke positive räumliche Autokorrelation. Hochbelastete Planungsräume liegen tendenziell nahe beieinander.

## 10.2 Moran's I für Deprivation

- \(I = 0.3116\)
- simulierter p-Wert: 0.001

Die soziale Lage weist ebenfalls räumliche Cluster auf.

## 10.3 Moran's I für Regressionsresiduen

- \(I = 0.4728\)
- simulierter p-Wert: 0.001

Die Residuen des Lärm-Deprivation-Modells sind stark räumlich korreliert. Das bedeutet:

- das einfache Modell erfasst die räumliche Struktur nicht vollständig
- zusätzliche räumliche oder sachliche Kontrollvariablen wären sinnvoll
- eine gewöhnliche OLS-Analyse allein reicht für eine räumliche Umweltgerechtigkeitsanalyse nicht vollständig aus

Ausgabedateien:

- `outputs/morans_i_laerm_gesamt_lden_db.txt`
- `outputs/morans_i_benachteiligungsindex.txt`
- `outputs/morans_i_residuals.txt`

---

## 11. Karte und Visualisierung

Das Projekt exportiert statische Karten und Scatterplots.

Karten:

- `outputs/map_laerm_gesamt_lden_db.png`
- `outputs/map_benachteiligungsindex.png`
- `outputs/map_angebotsmiete_median_eur_m2.png`

Weitere Visualisierungen:

- Korrelationsheatmap
- Lärm-Deprivation-Scatterplot
- Miet-Lärm-Scatterplot
- Miet-Deprivation-Scatterplot
- K-Means-Projektion
- Verteilungsdiagramme
- Boxplots

Eine interaktive Dashboard-Version wäre möglich, beispielsweise mit Streamlit und Plotly. Dafür müssten zusätzlich Streamlit und Plotly in der Umgebung installiert werden.

---

## 12. Datenrealität und wissenschaftliche Aussagekraft

Die Daten entsprechen den offiziellen Datenquellen und sind technisch nutzbar. Trotzdem gibt es wichtige Einschränkungen.

## Stärken

- Offizielles WFS mit 3.799.746 Fassadenpegelpunkten
- echte dB(A)-Werte statt Linienlängen
- vollständige Geometrie für alle 542 Planungsräume
- eindeutige Planungsraum-ID
- echte Lärm-, Miet- und Sozialdaten
- robuste HC3-Standardfehler
- räumliche Autokorrelation geprüft
- transparente Fallzahlnachweise

## Schwächen

- Querschnitt statt Längsschnitt
- unterschiedliche Datenstände
- Lärmaggregation auf Gebietsebene
- kein Bevölkerungsgewichtung der Lärmpunkte
- kein individueller Wohnbezug
- Mietdaten nur für Angebotsmarkt und viele kleine Stichproben
- MSS-Datei enthält keine Einzelindikatoren für eine echte PCA
- der Deprivationsscore ist vereinfacht ordinal
- die Residuen weisen starke räumliche Abhängigkeit auf
- Kontrollvariablen wie Fläche, Dichte und Grünanteil sind nicht final integriert

## Was die Analyse nicht beweist

Die Studie beweist nicht:

- dass soziale Benachteiligung Lärm verursacht
- dass Lärm direkte Mietpreise verursacht
- dass einzelne Haushalte benachteiligt sind
- dass ein beobachteter Zusammenhang für alle Zeitebenen gilt

Zulässige Aussagen sind beispielsweise:

- „In den betrachteten Daten besteht ein schwacher positiver räumlicher Zusammenhang zwischen Deprivation und Lärm.“
- „Nach Berücksichtigung der Deprivation hängt die Angebotsmiete positiv mit dem Lärm zusammen.“
- „Lärm und Deprivation sind räumlich stark geclustert.“
- „Das einfache Regressionsmodell erklärt einen kleinen Anteil der Lärmvariation.“

---

## 13. Aktueller Technischer Stand

Der vorhandene technische Ablauf ist:

```text
aggregate_noise.py
        ->
WFS-Abfrage
        ->
energetische PLR-Aggregation
        ->
laermdaten_aggregiert.csv
        ->
berlin_data_science.py
        ->
berlin_merged.csv / berlin_merged.gpkg
        ->
EDA / Regression / K-Means / Moran / Karten
        ->
outputs/
```

Der vollständige Hauptlauf lautet:

```powershell
cd berlin_laerm_sozialstruktur_starter
..\.venv\Scripts\python.exe aggregate_noise.py
..\.venv\Scripts\python.exe berlin_data_science.py
```

Die Lärmaggregation braucht typischerweise mehrere Minuten, weil 3.799.746 WFS-Punkte geladen werden.

Der Hauptlauf wurde erfolgreich getestet und erzeugt:

- zusammengeführten Geodatensatz
- Deskriptivstatistik
- Korrelationsmatrix
- Regressionssummaries
- VIF-Datei
- K-Means-Modellwahl
- Clusterprofile
- Moran-Ausgaben
- Karten
- Scatterplots

---

## 14. Aufräumliste

Diese Dateien können Sie selbst löschen, sofern sie nicht als Dokumentationsnachweis benötigt werden:

### Nicht mehr für die Analyse benötigt

- `data/current/planungsraume.csv`
- `data/current/strassenverteilung.csv`
- `data/current/laermdate.GetCapabilities.xml`
- `data/raw/laerm_strassen_lden.geojson`
- `data/raw/Mietdaten.xlsx`
- `data/raw/sozialdaten.xlsx`
- `data/raw/laerm_capabilities.xml`
- `data/raw/laerm_fassadenpegel2022.geojson`

Hinweis: Die letzten drei sind aktuell nur Redundanzen, wenn die finalen aggregierten Datensätze und das Skript als reproduzierbare Quelle erhalten bleiben. Die Lärmdaten können neu über den WFS geladen werden.

Die Dateien unter `data/current/` sind ältere Kopien und können nach Sicherung entfernt werden.

### Nicht mehr benötigte Verzeichnisinhalte

- `__pycache__/`
- überholte Dateien in `data/current/`
- überholte WFS-Testdateien, falls erneut erstellt

### Dateien, die erhalten bleiben sollten

- `aggregate_noise.py`
- `berlin_data_science.py`
- `README.md`
- `Plan.md`
- `requirements.txt`
- `data/raw/planungsraeume.geojson`
- `data/raw/sozialdaten.xlsx`
- `data/raw/Mietdaten.xlsx`
- `data/raw/laerm_capabilities.xml`
- `data/processed/laermdaten_aggregiert.csv`
- `data/processed/laermdaten_aggregiert.geojson`
- `data/processed/berlin_merged.csv`
- `data/processed/berlin_merged.gpkg`
- `outputs/`

---

## 15. Empfohlene nächste Verbesserungen

Für eine besonders starke Universitätsabgabe wären folgende Erweiterungen sinnvoll:

1. Ein räumliches Regressionsmodell ergänzen.
2. Moran Residuen in eine räumliche Modellinterpretation integrieren.
3. Ein bevölkerungsgewichtetes Lärmmaß berechnen.
4. Weitere MSS-Kontextindikatoren beschaffen.
5. Bei ausreichender Datenbasis eine PCA durchführen.
6. Mietrobustheitschecks für 10, 21 und 30 Inserate durchführen.
7. OLS-Residuen normaler prüfen.
8. Strukturgleichheit der Mietdaten für 2022 mit Lärm 2022 prüfen.
9. Multi-Jahr-Auswertung hinzufügen, falls mehrere MSS- und Mietdatenstände vorhanden sind.
10. Streamlit-Dashboard mit Karte, Scatterplots und Clusterfilter ergänzen.

---

## 16. Endgültiges Projektfazit

Das Projekt besitzt jetzt eine vollständige und wissenschaftlich nachvollziehbare Datenbasis.

Die Planungsraumgeometrien sind vollständig und valide. Der Lärmdatensatz basiert auf echten Fassadenpegeln und nicht mehr auf Straßennetzlängen. Sozialdaten und Mietdaten wurden korrekt auf die gemeinsame PLR-Ebene gebracht.

Die zentrale Hypothese erhält eine schwache positive Unterstützung:

- sozial ungünstigere Gebiete haben tendenziell höhere Lärmbelastung
- der Zusammenhang ist statistisch nachweisbar, aber praktisch schwach
- Angebotsmieten hängen stärker mit Lärm und Lage zusammen
- sozial benachteiligte Gebiete zeigen tendenziell niedrigere Mieten
- Lärm und Deprivation sind räumlich stark geclustert
- Residuen zeigen, dass ein einfaches OLS-Modell räumliche Muster nicht vollständig erklärt

Damit ist das Projekt bereit für eine universitäre Präsentation und Analyse, wenn die genannten methodischen Limitationen transparent berichtet werden.
