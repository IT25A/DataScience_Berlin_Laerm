# Berlin Environmental Justice Data-Science-Projekt - Plan & Status

## Aktualisiert: 23.11.2026

## 1. Forschungsfrage und Hypothesen

### Projekttitel
**Quantifying Environmental Justice: Eine räumliche Data-Science-Analyse von Verkehrslärm, sozialer Deprivation und Wohnkosten in Berlin.**

### Hauptforschungsfrage
Sind sozial benachteiligte Berliner Planungsräume stärker von Verkehrslärm betroffen, und wie hängen Lärmbelastung, soziale Deprivation und Angebotsmieten zusammen?

### Hypothesen
- **H1 – Umweltgerechtigkeit**: Planungsräume mit höherer sozialer Deprivation weisen höhere Lärmbelastungen auf.
- **H2 – Lärm und Mieten**: Lärmbelastung hängt mit den Angebotsmieten zusammen; die Richtung kann durch Lageeffekte beeinflusst werden.
- **H3 – Gebietstypen**: Berliner Planungsräume lassen sich anhand von Lärm, Deprivation und Mieten in unterschiedliche Gebietstypen gruppieren.

---

## 2. Aktueller Datenstatus

### Vorhandene Daten in data/raw/
| Datei | Status | Beschreibung |
|-------|--------|--------------|
| `planungsraeume.geojson` | ✅ heruntergeladen | **NEU**: GeoJSON mit Polygon-Geometrie der 542 Planungsräume (von ODIS Berlin) |
| `laerm_strassen_lden.geojson` | ✅ heruntergeladen | **NEU**: Lärm-Linien (Straßen/U-Bahn) mit L_DEN Werten (5762 Features) |
| `laerm_capabilities.xml` | ✅ heruntergeladt | WFS-Capabilities für Lärmkarten |
| (Alte Daten in data/current/) | verschoben | Alte Daten in data/current/ verschoben |

### Vorhandene Daten in data/current/ (Original-Daten)
| Datei | Status | Beschreibung |
|-------|--------|--------------|
| `planungsraume.csv` | ✅ vorhanden | Tabellarische Daten der Planungsräume (plr_id, plr_name, etc.) - KEINE GEOMETRIE |
| `sozialdaten.xlsx` | ✅ vorhanden | Sozialdaten (Arbeitslosigkeit, Transferbezug, Kinderarmut) |
| `Mietdaten.xlsx` | ✅ vorhanden | Mietdaten (Median-Angebotsmiete, Fallzahlen) |
| `strassenverteilung.csv` | ⚠️ vorhanden | Straßendaten mit Koordinaten (VP-Knoten) - nicht direkt nutzbar für Lärm |
| `laermdate.GetCapabilities.xml` | ⚠️ vorhanden | Metadaten für Lärm-WFS-Dienst (keine eigentlichen Lärmwerte) |

### Fehlende Daten (kritisch)
1. ~~**Geometrie für Planungsräume**~~: ✅ **HERUNTERGELADEN**
   - `planungsraeume.geojson` (542 Planungsräume mit Polygon-Geometrie)
   - Spalten: plr_id, plr_name, bzr_id, bzr_name, pgr_id, pgr_name, bez, finhalt, stadtraum_id, stadtraum_name, stand

2. **Lärmdaten**: ⚠️ **AGGREGIERT, aber nur als Proxy (Linienlänge)**
   - `laermdaten_aggregiert.csv` ✅ in data/processed/ erstellt
   - `laermdaten_aggregiert.geojson` ✅ in data/processed/ erstellt
   - **Problem**: Die heruntergeladenen Lärm-Linien enthalten keine dB-Werte, nur Geometrie
   - **Aktuelle Lösung**: Verwendet Linienlänge als Proxy für Lärmexposition (nicht in dB!)
   - **Bessere Lösung**: GeoTIFF-Raster oder Fassadenpegel-Daten herunterladen (siehe unten)

3. **Sozialdaten (MSS 2025)**: ✅ **VORHANDEN (aus data/current/)**
   - `sozialdaten.xlsx` - muss noch auf korrekte Spaltennamen geprüft werden
   - **Aktuelle Version**: https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/

4. **Mietdaten (IBB 2025)**: ✅ **VORHANDEN (aus data/current/)**
   - `Mietdaten.xlsx` - muss noch auf korrekte Spaltennamen geprüft werden
   - **Aktuelle Version**: https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html

---

## 3. Vorgenommene Code-Anpassungen (basierend auf Plan.md-Kritik)

### ✅ Priorität 1: PCA ausschließlich für soziale Indikatoren
- **Änderung**: Neue Funktion `run_pca_benachteiligungsindex()` verwendet nur `arbeitslosenanteil_prozent`, `transferbezugsanteil_prozent`, `kinderarmut_prozent`
- **Ergebnis**: PC1 wird als `benachteiligungsindex` gespeichert
- **Invertierung**: Wenn PC1 negativ mit Deprivation korreliert, wird der Index invertiert

### ✅ Priorität 1: K-Means mit Deprivationsindex und nachvollziehbarer k-Auswahl
- **Änderung**: Neue Funktion `run_clustering()` verwendet `laerm_gesamt_lden_db`, `benachteiligungsindex`, `angebotsmiete_median_eur_m2`
- **k-Auswahl**: Automatisch basierend auf Silhouette Score (vermeidet k=2, wenn besserer Score existiert)

### ✅ Priorität 1: Regressionen an Hypothesen angepasst
- **Änderung**: `run_regressions()` verwendet `benachteiligungsindex` statt einzelner sozialer Variablen
- **Modell A**: Lärm erklärt durch Deprivation (+ optionale Kontrollvariablen)
- **Modell B**: Miete erklärt durch Lärm und Deprivation (+ optionale Kontrollvariablen)
- **Neu**: VIF-Werte (Variance Inflation Factor) werden berechnet und exportiert

### ✅ Priorität 2: Moran's I für Deprivationsindex und Residuen
- **Änderung**: `run_morans_i()` prüft auch `benachteiligungsindex` (statt nur einzelne soziale Variablen)
- **Neu**: Parameter für Regressionsresiduen vorbereitet (wird später ergänzt)

### ✅ Optional: Decision Tree auskommentiert
- **Änderung**: `run_decision_tree()` ist in `main()` auskommentiert

### ✅ Sonstige Anpassungen
- **CSV-Unterstützung**: `load_boundaries()` kann jetzt auch CSV ohne Geometrie laden
- **Geometrie-Prüfung**: Moran's I und Kartenexport werden übersprungen, wenn keine Geometrie vorhanden
- **Karten**: `benachteiligungsindex` zur Liste der Kartenvariablen hinzugefügt

---

## 4. Nächste Schritte

### Schritt 1: Geometrie herunterladen (kritisch)
```
1. https://daten.odis-berlin.de/ besuchen
2. Nach "LOR Planungsräume" suchen
3. GeoPackage oder GeoJSON herunterladen
4. Als planungsraeume.gpkg oder planungsraeume.geojson in data/raw/ speichern
5. BOUNDARIES_FILE in berlin_data_science.py aktualisieren
```

### Schritt 2: Lärmdaten beschaffen (kritisch)
**Option A - WFS-Dienst auswerten:**
- Die XML-Datei enthält Metadaten für den WFS-Dienst
- Python-Skript schreiben, um Lärmwerte pro Planungsraum abzurufen
- Als laermdaten.csv speichern

**Option B - GeoTIFF-Raster:**
- Lärmkarten 2022 als GeoTIFF herunterladen
- Mit rasterstats zonal pro Planungsraum aggregieren
- `NOISE_LDEN_TIF` in berlin_data_science.py konfigurieren

### Schritt 3: Spaltennamen prüfen und anpassen
- Sozialdaten und Mietdaten öffnen
- Spaltennamen in `SOCIAL_COLUMN_MAP` und `RENT_COLUMN_MAP` anpassen

### Schritt 4: Analyse durchführen
```bash
cd berlin_laerm_sozialstruktur_starter
source .venv/bin/activate  # oder .venv\Scripts\activate auf Windows
python berlin_data_science.py
```

### Schritt 5: Dashboard (optional, Priorität 2)
- Streamlit und Plotly zu requirements.txt hinzufügen
- app.py mit interaktiver Karte erstellen

---

## 5. Empfohlene Aufgabenverteilung (4 Personen, 2-3 Wochen)

| Person | Hauptverantwortung | Ergebnis |
|--------|-------------------|----------|
| 1 | Datenbeschaffung (Geometrie, Lärm) + Datenqualität | Rohdaten, Quellenverzeichnis, Variablendokumentation |
| 2 | Datenaufbereitung und Spaltenzuordnung | Sauberer gemeinsamer PLR-Datensatz |
| 3 | PCA, EDA und Regression | Index, statistische Ergebnisse, Diagramme |
| 4 | K-Means, Moran's I und Dashboard | Cluster, räumliche Analyse, Streamlit |

---

## 6. Wochenplan

### Woche 1 – Datenbasis fertigstellen
- [ ] Geometrie für Planungsräume herunterladen
- [ ] Lärmdaten beschaffen (WFS oder Raster)
- [ ] Spaltennamen prüfen und anpassen
- [ ] Erste deskriptive Statistien

### Woche 2 – Data Science
- [ ] PCA und Deprivationsindex
- [ ] Pearson und Spearman Korrelationen
- [ ] Beide Regressionsmodelle
- [ ] K-Means und Clusterprofile
- [ ] Erste Dashboard-Version (optional)

### Woche 3 – Fertigstellung
- [ ] Moran's I (inkl. Residuen)
- [ ] Regressionsresiduen untersuchen
- [ ] Interaktive Karte fertigstellen (optional)
- [ ] Ergebnisse kritisch interpretieren
- [ ] Präsentation vorbereiten

---

## 7. Qualität der Daten

### Planungsraume.csv
- **Format**: CSV mit 543 Zeilen (Planungsräume)
- **Spalten**: plr_id, plr_name, bzr_id, bzr_name, pgr_id, pgr_name, bez, finhalt, stadtraum_id, stadtraum_name, stand
- **Qualität**: Gut (vollständige IDs und Namen)
- **Problem**: Keine Geometrie → keine räumlichen Analysen möglich

### Sozialdaten.xlsx
- **Format**: Excel-Datei
- **Qualität**: Muss noch geprüft werden (Spaltennamen)

### Mietdaten.xlsx
- **Format**: Excel-Datei
- **Qualität**: Muss noch geprüft werden (Spaltennamen, Fallzahlen)

### Strassenverteilung.csv
- **Format**: CSV mit 43.509 Zeilen (Straßensegmente)
- **Spalten**: Straßenschlüssel, Straßennamen, Koordinaten (VP-Knoten), Länge, etc.
- **Qualität**: Für Lärmanalyse nicht direkt nutzbar (es fehlen Lärmpegel)

---

## 8. Hinweise zur wissenschaftlichen Interpretation

- **Ökologischer Fehlschluss**: Ergebnisse gelten auf Gebietsebene, nicht für Individuen
- **Korrelation ≠ Kausalität**: Zusammenhänge sind statistisch, nicht kausal
- **Dezibel-Mittelung**: Wenn Raster verwendet werden, ist der arithmetische Mittelwert nicht identisch mit einem energetischen Mittelwert
- **Mietdatenqualität**: Angebotsmieten ≠ tatsächliche Mietkosten der dort lebenden Haushalte
- **Zeitstände**: Dokumentieren (Lärm 2022, MSS 2025, Mieten 2025)
