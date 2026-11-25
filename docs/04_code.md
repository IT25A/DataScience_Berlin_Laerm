# 4. Der Code: jede Funktion erklärt

Das Projekt besteht aus zwei Python-Skripten, die nacheinander laufen:

| Skript | Aufgabe | Laufzeit | Wie oft nötig? |
|---|---|---|---|
| `aggregate_noise.py` | Lädt 3,8 Mio. Lärmpunkte aus dem Internet und fasst sie pro Planungsraum zusammen | mehrere Minuten | einmal (Ergebnis wird gespeichert) |
| `berlin_data_science.py` | Gesamte Analyse: Daten verknüpfen, PCA, ANOVA, Regression, K-Means, Moran, Karten, Ergebnis | ca. 1 Minute | bei jeder Änderung |

---

## 4.1 Verwendete Bibliotheken

| Bibliothek | Wofür? | Beispiel im Code |
|---|---|---|
| **pandas** | Tabellen (DataFrames) lesen, filtern, verknüpfen | `pd.read_excel`, `merge`, `groupby` |
| **numpy** | Rechnen mit Zahlenreihen | `np.log1p`, `np.log10` |
| **geopandas** | Tabellen mit Geometrie (Polygone, Punkte); räumliche Joins; Karten | `gpd.read_file`, `sjoin`, `dissolve` |
| **matplotlib / seaborn** | Diagramme und Karten zeichnen | `plt.subplots`, `sns.boxplot`, `sns.heatmap` |
| **scipy.stats** | Statistische Tests | `stats.f_oneway` (ANOVA) |
| **statsmodels** | Regression mit ausführlichen Ergebnistabellen | `sm.OLS(...).fit(cov_type="cluster")` |
| **scikit-learn** | Machine Learning: Standardisierung, PCA, K-Means | `StandardScaler`, `PCA`, `KMeans` |
| **libpysal / esda** | Räumliche Statistik | `Queen` (Nachbarschaften), `Moran` |
| **openpyxl, pyogrio, shapely** | im Hintergrund: Excel lesen, Geodateien lesen, Geometrie | – |

Alle Versionen sind in `requirements.txt` fest vorgegeben, damit alle im Team dieselben Ergebnisse bekommen.

---

## 4.2 `aggregate_noise.py` – Lärmdaten aufbereiten

Dieses Skript ist kein Satz von Funktionen, die man aufruft, sondern läuft von oben nach unten durch. Es hat vier Hilfsfunktionen und einen Hauptablauf.

### Konstanten

| Konstante | Wert | Bedeutung |
|---|---|---|
| `WFS_URL` | `https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022` | Adresse des offiziellen Geodaten-Webdienstes |
| `TYPE_NAME` | `ua_stratlaerm_2022:aa_fp_gesamt2022` | Name des Datensatzes „Fassadenpegel Gesamtlärm 2022“ |
| `PAGE_SIZE` | 100.000 | so viele Punkte werden pro Anfrage geladen |
| `MAX_RETRIES` | 3 | so oft wird eine fehlgeschlagene Anfrage wiederholt |
| `LDEN_THRESHOLD_DB` | 65 | Schwellenwert für „stark belastete Fassade“ tagsüber (LDEN) |
| `LN_THRESHOLD_DB` | 55 | Schwellenwert nachts (LN) |

### `valid_levels(values)`
- **Zweck:** Bereinigt eine Reihe von Lärmwerten.
- **Eingabe:** eine Spalte mit Dezibelwerten (evtl. mit Text oder leeren Feldern).
- **Was passiert:** Wandelt alles in Zahlen um (Ungültiges wird zu „leer“) und behält nur Werte > 0, die endlich sind.
- **Ausgabe:** bereinigte Zahlenreihe.

### `energetic_mean(values)`
- **Zweck:** Berechnet den energetischen Mittelwert in dB (Formel in [02_daten.md](02_daten.md)).
- **Was passiert:** `10 · log10(Mittelwert(10^(dB/10)))`. Gibt „leer“ zurück, wenn keine gültigen Werte da sind.
- **Ausgabe:** eine Zahl (dB).

### `share_above(values, threshold)`
- **Zweck:** Anteil der Werte über einem Schwellenwert, in Prozent.
- **Beispiel:** 1.000 Fassadenpunkte, davon 80 über 65 dB → 8,0.

### `fetch_page(start_index)`
- **Zweck:** Lädt ein Paket von 100.000 Lärmpunkten vom Webdienst.
- **Eingabe:** ab welchem Punkt (0, 100.000, 200.000, …).
- **Was passiert:** Baut eine WFS-Anfrage-URL (`GetFeature`, Format JSON), schickt sie ab, liest die Antwort. Bei einem Netzwerkfehler wartet es 10, dann 20 Sekunden und versucht es erneut (max. 3 Versuche).
- **Ausgabe:** ein Python-Dictionary im GeoJSON-Format (Liste von Punkten mit Koordinaten und Eigenschaften).

### Hauptablauf (Schritt für Schritt)
1. **Planungsräume laden** aus `data/raw/planungsraeume.geojson`, prüfen, dass ein Koordinatensystem gesetzt ist, IDs auf 8 Stellen bringen.
2. **Erste Seite laden** und daraus die Gesamtzahl der Punkte lesen (3.799.746).
3. **Schleife über alle Seiten:**
   - Punkte in eine Tabelle umwandeln, prüfen, dass die erwarteten Spalten (`ges_den`, `ges_n`, `str_den`, `str_n`) vorhanden sind,
   - daraus Punkt-Geometrien erzeugen (Koordinatensystem EPSG:25833),
   - **räumlicher Join** (`gpd.sjoin(..., predicate="within")`): Jeder Punkt bekommt die ID des Planungsraums, in dem er liegt,
   - Geometrie verwerfen (spart Arbeitsspeicher) und Ergebnis sammeln.
4. **Alle Seiten zusammenfügen** (`pd.concat`).
5. **Pro Planungsraum zusammenfassen** (`groupby("plr_id")`):
   - Anzahl der Punkte,
   - energetischer Mittelwert für Gesamt-LDEN, Gesamt-LN, Straßen-LDEN, Straßen-LN,
   - Median für Gesamt-LDEN und Gesamt-LN,
   - Anteil Fassaden über 65 dB (LDEN) und über 55 dB (LN).
6. **An alle 542 Planungsräume anhängen**, damit auch Gebiete ohne Punkte (hier: keine) in der Tabelle stehen.
7. **Speichern** als `data/processed/laermdaten_aggregiert.csv` und `.geojson`, Kurzstatistik ausgeben.

---

## 4.3 `berlin_data_science.py` – die Analyse

### Aufbau der Datei

```text
1. Konfiguration        Dateipfade, Spaltenpositionen, Parameter
2. Hilfsfunktionen      kleine Werkzeuge
3. Datenimport          Daten laden und verknüpfen
4. PCA                  Benachteiligungsindex
5. Deskriptiv + ANOVA
6. Regression
7. K-Means
8. Moran's I
9. Karten, Ergebnis, main()
```

### Konfiguration (Abschnitt 1)

Hier stehen alle Einstellungen. Wer etwas ändern will (z. B. eine andere Mindestfallzahl), muss nur hier etwas anpassen.

| Konstante | Wert | Bedeutung |
|---|---|---|
| `RAW`, `PROCESSED`, `OUT` | `data/raw`, `data/processed`, `outputs` | Ordner |
| `BOUNDARIES_FILE` | `planungsraeume.geojson` | Gebietsgrenzen |
| `BOUNDARY_COLUMNS` | `plr_id, plr_name, pgr_id, bez, stadtraum_name, geometry` | welche Spalten der Geodatei behalten werden |
| `SOCIAL_STATUS_FILE` / `SOCIAL_INDICATOR_FILE` / `SOCIAL_ZVALUE_FILE` | MSS-Tabellen 1, 2.1, 3 | Sozialdaten |
| `SOCIAL_INDICATOR_COLUMNS` | `{arbeitslosenanteil_prozent: 3, ...}` | in welcher Excel-Spalte welcher Indikator steht (gezählt ab 0) |
| `RENT_FILE`, `RENT_SHEET` | `Mietdaten.xlsx`, `Planungsräume_2025` | Mietdaten |
| `NOISE_CSV`, `NOISE_COLUMNS` | `laermdaten_aggregiert.csv`, LDEN und Anteil > 65 dB | Ergebnis von `aggregate_noise.py` |
| `CONTROL_VARIABLES` | `log_einwohnerdichte`, `innere_stadt` | Kontrollvariablen der Regression |
| `CLUSTER_SE_COLUMN` | `pgr_id` | Gruppierung für geclusterte Standardfehler (Prognoseraum) |
| `MIN_RENT_LISTINGS` | 21 | Mindestzahl an Inseraten |
| `N_CLUSTERS` | 4 | Anzahl K-Means-Cluster |
| `CLUSTER_FEATURES` | Lärm, Index, Miete | Merkmale für K-Means |
| `CLUSTER_LEVEL_THRESHOLD_Z` | 0,25 | ab welcher Abweichung ein Clustermerkmal „hoch“/„niedrig“ heißt |
| `RANDOM_STATE` | 42 | fester Zufallsstartwert → reproduzierbare Ergebnisse |
| `MORAN_PERMUTATIONS` | 999 | Anzahl Zufallsmischungen beim Moran-Test |
| `SIGNIFICANCE_LEVEL` | 0,05 | Signifikanzniveau |
| `DEUTSCHE_BESCHRIFTUNG` | Wörterbuch | lesbare deutsche Achsenbeschriftungen für jede Spalte |

### Hilfsfunktionen (Abschnitt 2)

#### `label(col)`
Gibt für einen Spaltennamen die deutsche Beschriftung zurück, z. B. `"laerm_gesamt_lden_db"` → `"Gesamtlärm LDEN [dB(A)]"`. Gibt es keine, wird der Spaltenname selbst zurückgegeben.

#### `p_text(p)`
Formatiert einen p-Wert für Texte: `0.2888` → `"p = 0.289"`, sehr kleine Werte → `"p < 0.001"`.

#### `normalize_plr_id(series)`
Bringt Planungsraum-IDs in eine einheitliche Form:
1. in Text umwandeln, Leerzeichen entfernen,
2. ein angehängtes `.0` entfernen (entsteht, wenn Excel die ID als Kommazahl speichert),
3. links mit Nullen auf 8 Stellen auffüllen.

Beispiel: `1100101.0` → `"01100101"`.

#### `to_number(series)`
Wandelt eine Spalte in Zahlen um; was keine Zahl ist (z. B. „keine Daten“), wird zu einem fehlenden Wert (`NaN`).

#### `read_plr_rows(path, sheet, id_col)`
**Die wichtigste Einlesefunktion.**
- **Zweck:** Liest aus einer Behörden-Excel-Tabelle nur die Datenzeilen.
- **Eingabe:** Dateipfad, Tabellenblatt, Nummer der Spalte mit der PLR-ID.
- **Was passiert:**
  1. prüft, ob die Datei existiert (sonst verständliche Fehlermeldung),
  2. liest das ganze Blatt ohne Kopfzeile,
  3. normalisiert die ID-Spalte mit `normalize_plr_id`,
  4. behält nur Zeilen, deren ID genau aus 8 Ziffern besteht → Titel, Überschriften und Fußnoten fallen automatisch weg,
  5. bricht ab, falls eine ID doppelt vorkommt.
- **Ausgabe:** Tabelle mit genau einer Zeile pro Planungsraum; die Spalten sind nummeriert (0, 1, 2, …).

#### `save_figure(fig, name, dpi)`
Speichert eine Grafik als PNG in `outputs/` und schließt sie (spart Arbeitsspeicher).

### Datenimport (Abschnitt 3)

#### `load_boundaries()`
Lädt die Gebietsgrenzen, prüft das Koordinatensystem, normalisiert die IDs und behält nur die Spalten aus `BOUNDARY_COLUMNS`. **Ausgabe:** GeoDataFrame mit 542 Zeilen.

#### `load_social()`
Lädt die drei MSS-Tabellen und verknüpft sie:
1. Tabelle 1 → Einwohnerzahl (Spalte 2),
2. Tabelle 2.1 → S1–S4 (Spalten 3–6),
3. Tabelle 3 → amtlicher Status-Index (Spalte 8),
4. Verknüpfung über die PLR-ID mit Eindeutigkeitsprüfung.

**Ausgabe:** Tabelle mit `plr_id`, `einwohner`, vier Indikatoren und `mss_statusindex`.

#### `load_rents()`
Lädt das Blatt `Planungsräume_2025` der IBB-Tabelle: ID (Spalte 1), Name (2), Median-Miete (4), Fallzahl (6). **Ausgabe:** Tabelle mit `plr_id`, `plr_name_ibb`, `angebotsmiete_median_roh`, `anzahl_mietinserate`.

#### `load_noise()`
Liest die von `aggregate_noise.py` erzeugte CSV und gibt `plr_id`, `laerm_gesamt_lden_db` und `anteil_fassaden_lden_ueber_65_prozent` zurück. Fehlt die Datei, kommt die Meldung, zuerst `aggregate_noise.py` auszuführen.

#### `load_all_data()`
**Fügt alles zusammen.**
1. Gebietsgrenzen laden,
2. Sozial-, Miet- und Lärmdaten nacheinander per `merge(..., how="left", validate="one_to_one")` anhängen. „left“ heißt: Alle 542 Gebiete bleiben erhalten, auch wenn in einer Tabelle Werte fehlen,
3. Namensabgleich IBB ↔ Geometrie → `pruefung_namensabweichungen_ibb.csv`,
4. neue Variablen berechnen: `einwohnerdichte` (Einwohner / km², Fläche aus der Geometrie), `log_einwohnerdichte`, `innere_stadt` (0/1),
5. Mietfilter: `angebotsmiete_median_eur_m2` = Rohmiete nur bei ≥ 21 Inseraten, sonst fehlend,
6. Qualitätsbericht → `datenqualitaet.csv`, kurze Zusammenfassung in der Konsole.

**Ausgabe:** GeoDataFrame mit 542 Zeilen und allen Variablen.

#### `save_merged(data)`
Speichert den fertigen Datensatz (inkl. Index, Quintil, Cluster) als GeoPackage und CSV in `data/processed/`. Wandelt dafür die Quintil-Spalte (Kategorie-Datentyp) in Text um, weil das GeoPackage-Format keine Kategorien kennt.

### PCA (Abschnitt 4)

#### `run_pca_benachteiligungsindex(df)`
Berechnet den Benachteiligungsindex (Methode in [03_methoden.md, 3.2](03_methoden.md)).
1. Nimmt die vier Indikatoren aller Gebiete ohne fehlende Werte (535),
2. standardisiert sie (`StandardScaler`),
3. führt die PCA durch (`PCA().fit_transform`),
4. speichert Eigenwerte und erklärte Varianz → `pca_explained_variance.csv`,
5. berechnet die Ladungen (Eigenvektor × √Eigenwert) → `pca_loadings.csv`,
6. dreht das Vorzeichen, falls nötig, sodass hohe Werte = mehr Benachteiligung,
7. standardisiert PC1 (Mittel 0, SD 1) und speichert ihn als Spalte `benachteiligungsindex`,
8. berechnet die Korrelation mit dem amtlichen Status-Index,
9. schreibt `pca_bericht.txt` und zeichnet `pca_scree_ladungen.png`.

**Ausgabe:** Kopie des Datensatzes mit der neuen Spalte.

### Deskriptive Statistik und ANOVA (Abschnitt 5)

#### `run_descriptive(df)`
1. Kennzahlentabelle (Anzahl, Mittelwert, SD, Min, Quartile, Max, Varianz) für 9 Variablen → `descriptive_statistics.csv`,
2. 9 Histogramme in einer Grafik → `histogramme.png`,
3. Korrelationsmatrix als Heatmap → `korrelationsmatrix.png`.

#### `run_anova(df)`
1. Teilt die Gebiete nach Quintil des Index in 5 Gruppen (die Spalte `deprivationsquintil` wird vorher in `main()` mit `pd.qcut` erzeugt),
2. führt die einfaktorielle ANOVA durch (`stats.f_oneway`),
3. berechnet pro Gruppe Anzahl, Mittelwert, Median, SD → `anova_profile.csv`,
4. schreibt F-Wert und p-Wert → `anova_ergebnis.txt`.

**Ausgabe:** der p-Wert (wird später für die Ergebnisgrafik gebraucht).

### Regression (Abschnitt 6)

#### `run_regressions(df)`
Schätzt die drei Modelle A1, A2, B (Formeln in [03_methoden.md, 3.5](03_methoden.md)). Für jedes Modell:
1. wählt die benötigten Spalten und entfernt Zeilen mit fehlenden Werten (A1/A2: 535 Gebiete, B: 434),
2. fügt die Konstante hinzu (`sm.add_constant`),
3. schätzt das Modell **zweimal**:
   - klassisch: `sm.OLS(y, X).fit()`,
   - mit geclusterten Standardfehlern: `sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})`; `groups` ist die Prognoseraum-Nummer jedes Gebiets,
4. schreibt beide Ergebnistabellen in `regression_<Modell>.txt` (die geclusterte zuerst),
5. sammelt für jeden Koeffizienten: Wert, beide Standardfehler, beide p-Werte, n, R².

Alle Zeilen zusammen → `regression_uebersicht.csv`.

**Ausgabe:** Dictionary `{"ols": {...}, "cluster": {...}}` mit allen geschätzten Modellen. Die Residuen (für Moran) sind in beiden Varianten gleich.

### K-Means (Abschnitt 7)

#### `describe_level(z)`
Übersetzt einen standardisierten Clustermittelwert in Text: > 0,25 → „hoch“, < −0,25 → „niedrig“, sonst „mittel“.

#### `run_clustering(df)`
1. nimmt die 434 Gebiete mit allen drei Merkmalen (Lärm, Index, Miete) und standardisiert sie,
2. **Elbow-Methode:** berechnet K-Means für k = 1 bis 8 und zeichnet die Inertia → `kmeans_elbow.png`,
3. berechnet K-Means mit k = 4 (`n_init=20`, `random_state=42`),
4. sortiert die Cluster nach mittlerem Lärm (C1 = leisester), damit die Nummern bei jedem Lauf gleich sind,
5. benennt die Cluster automatisch mit `describe_level`,
6. speichert die Clusterprofile (Mittelwerte in Originaleinheiten, Anzahl) → `kmeans_cluster_profiles.csv` und die Zuordnung jedes Gebiets → `kmeans_clusters.csv`.

**Ausgabe:** Spalte mit dem Clusternamen für jedes der 434 Gebiete.

### Moran's I (Abschnitt 8)

#### `run_morans_i(gdf, models)`
1. Prüft, ob die Pakete `libpysal` und `esda` installiert sind (sonst Hinweis und Abbruch dieses Schritts),
2. stellt vier Wertereihen zusammen: Lärm, Benachteiligungsindex, Residuen von A1, Residuen von A2,
3. für jede Reihe:
   - Gebiete ohne Wert entfernen,
   - Queen-Nachbarschaft aus den Polygonen berechnen (`Queen.from_dataframe`) und zeilenstandardisieren (`transform = "r"`),
   - Zufallsstartwert setzen (damit p_sim reproduzierbar ist),
   - Moran's I mit 999 Permutationen berechnen,
4. Ergebnis (I, p_sim, n) → `morans_i.csv`.

### Karten, Ergebnis und Hauptprogramm (Abschnitt 9)

#### `draw_districts(ax, gdf, labels)`
Zeichnet die 12 Bezirksgrenzen als schwarze Linien in eine Karte. Dafür werden alle Planungsräume eines Bezirks zu einem Polygon verschmolzen (`dissolve`). Mit `labels=True` werden die Bezirksnamen in die Karte geschrieben.

#### `export_maps(gdf)`
1. Drei Choroplethenkarten (Flächen eingefärbt nach Wert) für Lärm, Benachteiligungsindex und Miete → `map_<variable>.png`. Gebiete ohne Wert werden hellgrau dargestellt.
2. Clusterkarte: jeder Cluster in einer eigenen Farbe, nicht geclusterte Gebiete grau, Bezirksgrenzen und -namen, Legende mit Clustername und Anzahl → `map_kmeans_cluster.png`.

#### `build_conclusion(df, models, anova_p, moran)`
Formuliert die Antwort auf die Leitfrage **automatisch aus den berechneten Zahlen** (es ist kein fester Text eingetragen):
1. H1: Ist der Koeffizient der Benachteiligung in Modell A2 mit geclusterten Standardfehlern signifikant positiv? → „gestützt“ bzw. „nicht gestützt“,
2. Effektgrößen und p-Werte von A1 und A2 (korrigiert und unkorrigiert),
3. mittlerer Lärm je Quintil, ANOVA-Ergebnis, Abstand Q1 zum Rest, Spannweite Q2–Q5,
4. H2: Koeffizienten von Modell B,
5. H3: Anzahl Cluster und Anteil „Lärm hoch · Benachteiligung hoch“,
6. Moran-Werte und Hinweis auf die räumliche Korrektur.

Würden sich die Daten ändern, würde sich der Text automatisch anpassen.

#### `plot_final_result(df, models, anova_p, moran)`
Erstellt die Ergebnisgrafik `ergebnis_leitfrage.png` mit vier Feldern (Deutung in [05_outputs.md](05_outputs.md)) und speichert den Antworttext als `ergebnis_zusammenfassung.txt`.

#### `main()`
Das Hauptprogramm ruft alles in der richtigen Reihenfolge auf:

```text
Ordner anlegen
load_all_data()                    -> Daten (bei Fehler: verständliche Meldung, Abbruch)
run_pca_benachteiligungsindex()    -> Index
pd.qcut(..., 5)                    -> Quintile Q1–Q5
run_descriptive()
run_anova()                        -> p-Wert
run_regressions()                  -> Modelle
run_clustering()                   -> Cluster
run_morans_i()                     -> Moran-Tabelle
export_maps()
plot_final_result()
save_merged()
```

`if __name__ == "__main__": main()` sorgt dafür, dass `main()` nur läuft, wenn man die Datei direkt startet – nicht, wenn man sie in einem anderen Skript importiert.

---

## 4.4 Häufige Fehlermeldungen

| Meldung | Ursache | Lösung |
|---|---|---|
| `Datei nicht gefunden: .../data/raw/...` | Rohdatei fehlt oder heißt anders | Datei in `data/raw/` ablegen, Namen prüfen (Groß-/Kleinschreibung!) |
| `Keine Lärmdaten gefunden` | `aggregate_noise.py` wurde noch nicht ausgeführt | `python aggregate_noise.py` |
| `Doppelte PLR-IDs in ...` | Eine Tabelle enthält eine ID zweimal | Excel-Datei prüfen |
| `ModuleNotFoundError: No module named ...` | Pakete nicht installiert oder falsche Umgebung aktiv | `.venv` aktivieren, `pip install -r requirements.txt` |
| `Moran's I übersprungen` | `libpysal`/`esda` fehlen | `pip install -r requirements.txt` |
