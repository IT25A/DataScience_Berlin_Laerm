# Berlin Environmental Justice – Plan & Status

## Aktualisiert: 24.11.2026

**Titel:** Quantifying Environmental Justice: Eine räumliche Data-Science-Analyse von Verkehrslärm, sozialer Benachteiligung und Wohnkosten in Berlin

**Leitfrage:** Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von Lärm betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?

- **H1:** Benachteiligte Planungsräume weisen höhere Lärmwerte auf.
- **H2:** Lärm hängt mit den Angebotsmieten zusammen (Lageeffekte möglich).
- **H3:** Planungsräume lassen sich nach Lärm, Benachteiligung und Miete in interpretierbare Gebietstypen gruppieren.

---

## 1. Erledigt (Review vom 24.11.2026)

### Daten
- [x] MSS 2025 **Tabelle 2.1** (Einzelindikatoren S1–S4) und **Tabelle 3** (z-Werte, amtlicher Status-Index) ergänzt
- [x] Lärm neu aggregiert: zusätzlich Median-LDEN und Anteil Fassaden > 65 dB LDEN / > 55 dB LN (alte Werte identisch reproduziert)
- [x] Namensabgleich IBB ↔ Geometrie automatisiert (`outputs/pruefung_namensabweichungen_ibb.csv`)
- [x] Excel-Import robust über PLR-ID statt fester Kopfzeilen (Fußnotenzeilen werden ignoriert)
- [x] Dateiname `Mietdaten.xlsx` korrekt (vorher `mietdaten.xlsx`, brach unter Linux)

### Methodik
- [x] **PCA** über S1–S4 → PC1 = Benachteiligungsindex (80,7 % Varianz, r = 0,998 mit amtlichem MSS-Status-Index)
- [x] Ordinaler Score 1–4 durch stetigen Index ersetzt
- [x] EDA nach der PCA, mit allen Variablen; Pearson **und** Spearman; Boxplots je Variable
- [x] Gruppenvergleich (Kruskal-Wallis, ANOVA) nach MSS-Klasse und Index-Quintil
- [x] Regressionen mit nach Prognoseraum **geclusterten Standardfehlern** + Kontrollen (log Dichte, Innere Stadt)
- [x] Robustheit: Median-LDEN, Anteil > 65 dB, nur Straßenlärm, Mietschwellen 10/21/30, Mieten 2022
- [x] VIF korrekt (mit Konstante, auf Modellstichprobe)
- [x] K-Means: k = 4 begründet, automatische Clusterbenennung, Elbow-/Silhouette-Plot
- [x] Moran's I mit festem Seed, inkl. Miete und Residuen beider Lärmmodelle
- [x] Berlin-Karte der Cluster (`map_kmeans_cluster.png`) und Ergebnisgrafik (`ergebnis_leitfrage.png`)

### Technik
- [x] Toter Code entfernt (alte PCA-Platzhalter, Decision Tree, Raster-Zweig, ungenutzte Imports)
- [x] Paketversionen in `requirements.txt` fest gepinnt; `rasterio`/`rasterstats` entfernt
- [x] Qualitätsbericht nach dem Mietfilter (`outputs/datenqualitaet.csv`)

---

## 2. Offene Punkte (nach Priorität)

### Priorität 1 – vor der Präsentation
- [ ] **Ergebnisse interpretieren und Folien bauen** (Kernaussagen siehe Projekt_Recap §16)
- [ ] **Wittenau Mitte/Süd** (`12500926`, `12500930`): In der IBB-Tabelle vertauschte Namen prüfen (IBB-PDF vergleichen); im Zweifel beide PLR im Mietmodell ausschließen und als Limitation nennen
- [ ] Limitationen-Folie: Fassadenpunkte nicht bevölkerungsgewichtet, Mietfilter unterrepräsentiert Gebiete mit hohem Status, Querschnitt, unterschiedliche Datenjahre
- [ ] Quellenverzeichnis mit Abrufdatum (WFS-Abruf 24.11.2026)

### Priorität 2 – wenn Zeit bleibt
- [ ] Bevölkerungsgewichtung: Fassadenpunkte auf Wohngebäude beschränken (Layer `ab_wohngebaeude2022` ist im WFS vorhanden)
- [ ] LISA-Karte (lokales Moran's I) für Hot-/Coldspots von Lärm und Benachteiligung

### Bewusst NICHT geplant (Umfang des Moduls)
- Räumliche Regressionsmodelle (Spatial Lag/Error) – nur als Ausblick erwähnen
- Streamlit-Dashboard – statische Karten reichen für die Präsentation
- Decision Tree, Multi-Jahr-Analyse

---

## 3. Aufgabenverteilung (Vorschlag)

| Person | Aufgabe |
|---|---|
| 1 | Daten & Quellen: Quellenverzeichnis, Wittenau-Prüfung, Datenqualitätsfolie |
| 2 | PCA & EDA: Index erklären (Ladungen, Validierung), deskriptive Folien |
| 3 | Regression & Robustheit: Koeffizientenplot, Interpretation H1/H2 |
| 4 | Cluster & Karten: Gebietstypen, Moran's I, Ergebnisfolie |

---

## 4. Ausführen

```bash
cd berlin_laerm_sozialstruktur_starter
python aggregate_noise.py        # nur nötig, wenn Lärmdaten neu geladen werden sollen
python berlin_data_science.py
```

## 5. Hinweise zur Interpretation

- Ökologischer Fehlschluss: Aussagen gelten für Gebiete, nicht für Personen
- Korrelation ≠ Kausalität
- p-Werte aus den Modellen mit geclusterten Standardfehlern sind maßgeblich (räumliche Autokorrelation)
- Angebotsmieten ≠ tatsächlich gezahlte Mieten
- Zeitstände: Lärm 2022, MSS 2025 (31.12.2024), Mieten 2025
