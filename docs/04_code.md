# 4. Der Code: jede Funktion erklärt

Das Projekt besteht aus zwei Python-Skripten, die nacheinander laufen:

| Skript | Aufgabe | Laufzeit | Wie oft nötig? |
|---|---|---|---|
| `aggregate_noise.py` | Lädt 3,8 Mio. Lärmpunkte aus dem Internet und fasst sie pro Planungsraum zusammen | mehrere Minuten | einmal (Ergebnis wird gespeichert) |
| `berlin_data_science.py` | Gesamte Analyse: Daten verknüpfen, PCA, ANOVA, Regression, K-Means, Moran, Karten und Ergebnis; standardmäßig für 2022 und neueste verfügbare Daten | ca. 1 Minute je Datenstand | bei jeder Änderung |

`berlin_data_science.py` ist bewusst **einsteigerfreundlich** geschrieben (Branch `beginner-code`):
- deutsche Variablen- und Funktionsnamen (`daten`, `laerm_werte`, `daten_laden()`),
- einfache `for`-Schleifen statt verschachtelter Python-Kurzschreibweisen,
- jeder Schritt eine eigene Funktion mit Kommentaren,
- alle Einstellungen oben an einer Stelle.

Dadurch ist die Datei etwas länger, aber Zeile für Zeile nachvollziehbar. Die Ergebnisse der 2022-Hauptanalyse wurden mit der kompakteren Version auf dem Branch `simplify-analysis` automatisch verglichen. Die Auswahl der Datenstände und der Jahrgangsvergleich sind in dieser Einsteiger-Version ergänzt.

---

## 4.1 Verwendete Bibliotheken

| Bibliothek | Wofür? | Beispiel im Code |
|---|---|---|
| **argparse** (Standardbibliothek) | Kommandozeilenoptionen für die Wahl des Datenstands | `--datenstand aktuell` |
| **pandas** (`pd`) | Tabellen (DataFrames) lesen, filtern, verknüpfen | `pd.read_excel`, `merge`, `groupby` |
| **numpy** (`np`) | Rechnen mit Zahlenreihen | `np.log1p`, `np.corrcoef` |
| **geopandas** (`gpd`) | Tabellen mit Geometrie (Polygone); Karten | `gpd.read_file`, `dissolve`, `plot` |
| **matplotlib / seaborn** (`plt`, `sns`) | Diagramme und Karten zeichnen | `plt.subplots`, `sns.boxplot`, `sns.heatmap` |
| **scipy.stats** | Statistische Tests | `stats.f_oneway` (ANOVA) |
| **statsmodels** (`sm`) | Regression mit ausführlichen Ergebnistabellen | `sm.OLS(y, X).fit()` |
| **scikit-learn** | Standardisierung, PCA, K-Means | `StandardScaler`, `PCA`, `KMeans` |
| **libpysal / esda** | Räumliche Statistik | `Queen` (Nachbarschaften), `Moran` |
| **textwrap** (Standardbibliothek) | lange Texte umbrechen | `textwrap.fill` |
| **openpyxl, pyogrio, shapely** | im Hintergrund: Excel lesen, Geodateien lesen, Geometrie | – |

Alle Versionen sind in `requirements.txt` fest vorgegeben, damit alle im Team dieselben Ergebnisse bekommen.

---

## 4.2 `aggregate_noise.py` – Lärmdaten aufbereiten

Dieses Skript läuft von oben nach unten durch. Es hat vier Hilfsfunktionen und einen Hauptablauf.

### Konstanten

| Konstante | Wert | Bedeutung |
|---|---|---|
| `WFS_URL` | `https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022` | Adresse des offiziellen Geodaten-Webdienstes |
| `TYPE_NAME` | `ua_stratlaerm_2022:aa_fp_gesamt2022` | Name des Datensatzes „Fassadenpegel Gesamtlärm 2022“ |
| `PAGE_SIZE` | 100.000 | so viele Punkte werden pro Anfrage geladen |
| `MAX_RETRIES` | 3 | so oft wird eine fehlgeschlagene Anfrage wiederholt |
| `LDEN_THRESHOLD_DB` | 65 | Schwellenwert für „stark belastete Fassade“ (LDEN) |
| `LN_THRESHOLD_DB` | 55 | Schwellenwert nachts (LN) |

### `valid_levels(values)`
Bereinigt eine Reihe von Lärmwerten: alles in Zahlen umwandeln (Ungültiges wird „leer“), nur Werte > 0 behalten.

### `energetic_mean(values)`
Energetischer Mittelwert in dB: `10 · log10(Mittelwert(10^(dB/10)))` (Formel und Beispiel in [02_daten.md](02_daten.md)).

### `share_above(values, threshold)`
Anteil der Werte über einem Schwellenwert in Prozent. Beispiel: 1.000 Punkte, davon 80 über 65 dB → 8,0.

### `fetch_page(start_index)`
Lädt ein Paket von 100.000 Lärmpunkten vom Webdienst (ab Punkt `start_index`). Bei einem Netzwerkfehler wird bis zu 3-mal neu versucht (mit 10 bzw. 20 Sekunden Pause).

### Hauptablauf
1. **Planungsräume laden**, IDs auf 8 Stellen bringen.
2. **Erste Seite laden**, Gesamtzahl der Punkte lesen (3.799.746).
3. **Schleife über alle Seiten:** Punkte in eine Tabelle umwandeln, Spalten prüfen, Punkt-Geometrien erzeugen, **räumlicher Join** (`gpd.sjoin(..., predicate="within")`: jeder Punkt bekommt die ID des Planungsraums, in dem er liegt), Ergebnis sammeln.
4. **Alle Seiten zusammenfügen.**
5. **Pro Planungsraum zusammenfassen:** Anzahl Punkte, energetische Mittelwerte (Gesamt/Straße, Tag/Nacht), Mediane, Anteile über 65 bzw. 55 dB.
6. **An alle 542 Planungsräume anhängen.**
7. **Speichern** als `data/processed/laermdaten_aggregiert.csv` und `.geojson`.

---

## 4.3 `berlin_data_science.py` – die Analyse

### Aufbau der Datei

```text
Einstellungen           Datenstandsprofile, Dateinamen, Parameter, Beschriftungen
Hilfsfunktionen         p_wert_text, grafik_speichern, excel_zeilen_mit_plr_id, bezirksgrenzen_zeichnen
Schritt 1               daten_laden, daten_speichern
Schritt 2               pca_benachteiligungsindex
Schritt 3               deskriptive_statistik
Schritt 4               anova
Schritt 5               regression_rechnen, regressionen
Schritt 6               stufe, kmeans_clustering
Schritt 7               moran_berechnen, morans_i
Schritt 8               karte_zeichnen, cluster_karte_zeichnen
Schritt 9               ergebnis_text, ergebnisgrafik
Hauptprogramm           datenstand_konfigurieren, analyse_ausfuehren,
                        datenstaende_korrelieren, main
```

**Tipp zum Lesen:** Fang ganz unten bei `main()` an. Dort sieht man in 20 Zeilen den gesamten Ablauf. Danach liest man die einzelnen Schritte.

### Einstellungen

| Name | Wert | Bedeutung |
|---|---|---|
| `ORDNER` | Ordner des Skripts | Ausgangspunkt für alle Pfade |
| `ROHDATEN`, `AUFBEREITET`, `AUSGABE` | `data/raw`; Ausgabeordner des aktiven Datenstands | Eingabe- und Ausgabeordner |
| `DATEI_PLANUNGSRAEUME` | `planungsraeume.geojson` | Gebietsgrenzen |
| `DATENSTAND_KONFIGURATIONEN` | Profile `2022` und `aktuell` | Quelldateien, Excel-Blätter und Unterordner für getrennte Ergebnisse |
| `DATEI_MSS_TABELLE_1/2/3`, `MIETEN_BLATT` | werden durch `datenstand_konfigurieren()` gesetzt | MSS 2023 / Mieten 2022 oder MSS 2025 / Mieten 2025 |
| `DATEI_LAERM` | `data/processed/laermdaten_aggregiert.csv` | dieselbe Lärmkarte 2022 in beiden Varianten |
| `MINDEST_INSERATE` | 21 | Mindestzahl an Mietinseraten |
| `ANZAHL_CLUSTER` | 4 | k für K-Means |
| `CLUSTER_SCHWELLE` | 0,25 | ab welcher Abweichung ein Clustermerkmal „hoch“/„niedrig“ heißt |
| `ZUFALLSZAHL` | 42 | fester Zufallsstartwert → reproduzierbare Ergebnisse |
| `MORAN_PERMUTATIONEN` | 999 | Anzahl Zufallsmischungen beim Moran-Test |
| `SIGNIFIKANZNIVEAU` | 0,05 | Grenze für „signifikant“ |
| `INDIKATOREN` | S1–S4 | Spalten für die PCA |
| `KONTROLLVARIABLEN` | `log_einwohnerdichte`, `innere_stadt` | Kontrollvariablen der Regression |
| `CLUSTER_MERKMALE` | Lärm, Index, Miete | Merkmale für K-Means |
| `QUINTIL_NAMEN` | `Q1\ngeringste`, …, `Q5\nstärkste` | Namen der 5 Gruppen (`\n` = Zeilenumbruch in der Grafik) |
| `BESCHRIFTUNG` | Wörterbuch | deutsche Achsenbeschriftung für jede Spalte |

Wer etwas ändern will (z. B. eine andere Mindestfallzahl), muss nur diesen Abschnitt anpassen.

### Datenstände wählen und vergleichen

`datenstand_konfigurieren(datenstand)` schaltet die Eingabedateien und Ausgabeordner um:
- **2022:** MSS-Datenstand 31.12.2022 und IBB-Blatt `Planungsräume_2022`.
- **aktuell:** MSS 2025 mit Sozialdatenstand 31.12.2024 und IBB-Blatt `Planungsräume_2025`. Die aktuellste verfügbare Lärmkarte bleibt 2022.

`main()` führt standardmäßig beide Profile aus. Die alten Ausgabepfade unter `outputs/` und `data/processed/` bleiben für 2022 bestehen; die neuere Variante wird getrennt unter `aktuell/` gespeichert.

`datenstaende_korrelieren()` liest anschließend beide zusammengeführten Tabellen ein, verbindet sie über `plr_id` und berechnet für Sozialindikatoren, Benachteiligungsindex, Mieten und Einwohnerwerte Pearson-r sowie Spearman-rho. Der paarweise Ausschluss fehlender Werte führt je Kennzahl zu einer eigenen Fallzahl. Tabelle und gruppiertes Balkendiagramm werden als `outputs/vergleich_zeitraeume.csv` und `outputs/vergleich_zeitraeume.png` gespeichert.

### Hilfsfunktionen

#### `p_wert_text(p)`
Macht aus einem p-Wert einen kurzen Text: `0.2888` → `"p = 0.289"`, sehr kleine Werte → `"p < 0.001"`. Einfaches `if`.

#### `grafik_speichern(fig, dateiname, dpi=170)`
Speichert eine Grafik als PNG im Ausgabeordner des aktiven Datenstands und schließt sie (spart Arbeitsspeicher). `dpi` ist die Auflösung.

#### `excel_zeilen_mit_plr_id(datei, blatt, id_spalte)`
**Die wichtigste Einlesefunktion.** Die Excel-Tabellen der Behörden haben Titel, Überschriften und Fußnoten. Die Funktion behält nur die Datenzeilen:
1. Liest das ganze Blatt ohne Kopfzeile (`header=None`) – die Spalten heißen dann 0, 1, 2, …
2. Macht aus der ID-Spalte einen einheitlichen Text: Leerzeichen weg, `.0` weg, mit `zfill(8)` links mit Nullen auf 8 Stellen auffüllen (`1100101` → `01100101`).
3. Behält nur Zeilen, deren ID genau 8 Ziffern hat (`str.isdigit()` und Länge 8). Titel und Fußnoten fallen dadurch automatisch weg.
4. Bricht mit einer Fehlermeldung ab, falls eine ID doppelt vorkommt.

**Rückgabe:** Tabelle mit genau einer Zeile pro Planungsraum.

#### `bezirksgrenzen_zeichnen(ax, daten, mit_namen=False)`
Zeichnet die 12 Bezirksgrenzen als schwarze Linien in eine Karte. Mit `dissolve(by="bez")` werden alle Planungsräume eines Bezirks zu einer Fläche verschmolzen. Mit `mit_namen=True` wird zusätzlich der Bezirksname in die Fläche geschrieben (`"08 - Neukölln"` → `"Neukölln"`).

### Schritt 1: `daten_laden()`

Lädt die Quellen des aktiven Datenstands und verknüpft sie zu **einer** Tabelle mit 542 Zeilen. Die Lärmdaten und Gebietsgrenzen sind in beiden Läufen gleich; Sozial- und Mietdaten wechseln mit dem Profil. Die Funktion ist in Unterschritte 1a–1h gegliedert:

| Unterschritt | Was passiert? |
|---|---|
| **1a** Planungsräume | Geodatei lesen, IDs auf 8 Stellen, nur die benötigten Spalten behalten |
| **1b** Sozialdaten | MSS-Tabelle 1 → Einwohner (Spalte 2); Tabelle 2.1 → S1–S4 (Spalten 3–6); Tabelle 3 → amtlicher Status-Index (Spalte 8). Jede wird mit `excel_zeilen_mit_plr_id` gelesen und in eine kleine Tabelle mit sprechenden Spaltennamen übertragen. `pd.to_numeric(..., errors="coerce")` macht aus Text wie „keine Daten“ einen fehlenden Wert. |
| **1c** Mietdaten | IBB-Tabelle → ID (Spalte 1), Name (2), Median-Miete (4), Anzahl Inserate (6) |
| **1d** Lärmdaten | CSV von `aggregate_noise.py` lesen, LDEN und Anteil > 65 dB behalten |
| **1e** Verknüpfen | Fünfmal `daten.merge(..., on="plr_id", how="left", validate="one_to_one")`. `how="left"` = alle 542 Gebiete bleiben erhalten; `validate` = Abbruch bei doppelten IDs |
| **1f** Namensabgleich | Gebiete, deren IBB-Name vom offiziellen Namen abweicht → `pruefung_namensabweichungen_ibb.csv` |
| **1g** Neue Variablen | `einwohnerdichte` = Einwohner / Fläche in km² (Fläche aus der Geometrie, m² / 1.000.000); `log_einwohnerdichte` = log(1 + Dichte); `innere_stadt` = 1 oder 0; `angebotsmiete_median_eur_m2` = Miete nur bei ≥ 21 Inseraten (mit `.where()`, sonst fehlend) |
| **1h** Qualitätsbericht | Für jede Spalte Anzahl gültiger und fehlender Werte → `datenqualitaet.csv` |

**Rückgabe:** die fertige Tabelle `daten`.

### `daten_speichern(daten)`
Speichert den fertigen Datensatz (inkl. Index, Quintil, Cluster) als `berlin_merged.gpkg` (mit Geometrie) und `berlin_merged.csv` (ohne Geometrie). Die Quintil-Spalte wird vorher in Text umgewandelt, weil das GeoPackage-Format keine Kategorien kennt.

### Schritt 2: `pca_benachteiligungsindex(daten)`

Berechnet den Benachteiligungsindex (Methode in [03_methoden.md, 3.2](03_methoden.md)):

| Unterschritt | Was passiert? |
|---|---|
| Auswahl | nur Gebiete mit allen vier Indikatoren (2022: 536; aktuell: 535) |
| **2a** | Standardisieren mit `StandardScaler().fit_transform(...)` |
| **2b** | PCA mit `PCA().fit_transform(...)`; Eigenwerte und erklärte Varianz → `pca_explained_variance.csv` |
| **2c** | Ladungen = Eigenvektoren × √Eigenwert |
| **2d** | Vorzeichen prüfen: Ist die Summe der PC1-Ladungen negativ, werden Ladungen und PC1 umgedreht (hohe Werte = mehr Benachteiligung) → `pca_loadings.csv` |
| **2e** | PC1 standardisieren (Mittel 0, SD 1) und als Spalte `benachteiligungsindex` speichern |
| **2f** | Korrelation mit dem amtlichen Index (`np.corrcoef`) → `pca_bericht.txt` |
| **2g** | Grafik: Scree-Plot und Ladungen → `pca_scree_ladungen.png` |

**Rückgabe:** `daten` mit der neuen Spalte.

### Schritt 3: `deskriptive_statistik(daten)`
1. Kennzahlen mit `describe()` plus Varianz → `descriptive_statistics.csv`,
2. 9 Histogramme in einem 3×3-Raster. `achsen.flatten()` macht aus dem Raster eine einfache Liste, damit eine `for`-Schleife die Felder der Reihe nach füllen kann → `histogramme.png`,
3. Korrelationsmatrix als Heatmap → `korrelationsmatrix.png`.

### Schritt 4: `anova(daten)`
1. **4a:** Für jedes der 5 Quintile die Lärmwerte in einer Liste `gruppen` sammeln (Schleife über `QUINTIL_NAMEN`),
2. **4b:** `stats.f_oneway(gruppe1, ..., gruppe5)` liefert F-Wert und p-Wert,
3. **4c:** Kennzahlen je Quintil mit `groupby(...).agg(["count", "mean", "median", "std"])` → `anova_profile.csv`, Text → `anova_ergebnis.txt`.

**Rückgabe:** der p-Wert (für die Ergebnisgrafik).

### Schritt 5: Regression

#### `regression_rechnen(daten, zielvariable, einflussvariablen)`
Schätzt **ein** Modell zweimal:
1. Gebiete mit fehlenden Werten entfernen (`dropna()`),
2. `y` = Zielvariable, `X` = Einflussvariablen plus Konstante (`sm.add_constant`),
3. **klassisch:** `sm.OLS(y, X).fit()`,
4. **räumlich korrigiert:** `sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": prognoseraum_nummer})`. `pd.factorize` macht aus den Prognoseraum-IDs einfache Gruppennummern 0, 1, 2, …

**Rückgabe:** beide Modelle (`modell_klassisch, modell_korrigiert`).

#### `regressionen(daten)`
1. Definiert die drei Modelle in einer Liste: A1 (Lärm ~ Index), A2 (+ Kontrollen), B (Miete ~ Lärm + Index + Kontrollen),
2. ruft für jedes `regression_rechnen` auf,
3. speichert beide Ergebnistabellen in `regression_<Name>.txt` (korrigierte zuerst),
4. sammelt pro Einflussvariable eine Zeile (Koeffizient, beide Standardfehler, beide p-Werte, n, R²) → `regression_uebersicht.csv`.

**Rückgabe:** Wörterbuch `modelle` mit sechs Einträgen, z. B. `modelle["A2_laerm_kontrollen_korrigiert"]`.

### Schritt 6: K-Means

#### `stufe(z_wert)`
Übersetzt einen standardisierten Mittelwert in Text: über +0,25 → „hoch“, unter −0,25 → „niedrig“, sonst „mittel“.

#### `kmeans_clustering(daten)`

| Unterschritt | Was passiert? |
|---|---|
| **6a** | Gebiete mit allen drei Merkmalen auswählen und standardisieren (2022: 341; aktuell: 434) |
| **6b** | Elbow-Methode: Schleife über k = 1 bis 8, jeweils K-Means rechnen und `inertia_` notieren → `kmeans_elbow.png` |
| **6c** | Endgültiges K-Means mit k = 4 (`n_init=20`, `random_state=42`) |
| **6d** | Cluster nach mittlerem Lärm sortieren: Mittelwert je Cluster berechnen, sortieren, in einer Schleife neue Nummern 1–4 vergeben (C1 = leisester) |
| **6e** | Namen bilden: für jeden Cluster und jedes Merkmal `stufe(...)` aufrufen und zu „C3: Lärm hoch · Benachteiligung hoch · Miete niedrig“ zusammensetzen |
| **6f** | Clusterprofile in Originaleinheiten → `kmeans_cluster_profiles.csv` |
| **6g** | Zuordnung jedes Gebiets → `kmeans_clusters.csv` |

**Rückgabe:** Spalte mit dem Clusternamen für jedes der 341 Gebiete.

### Schritt 7: Moran's I

#### `moran_berechnen(daten, werte)`
Berechnet Moran's I für **eine** Wertereihe:
1. Gebiete ohne Wert entfernen,
2. Queen-Nachbarschaft aus den Polygonen bestimmen (`Queen.from_dataframe`) und zeilenstandardisieren (`transform = "r"`),
3. Zufallsstartwert setzen,
4. `Moran(werte, nachbarn, permutations=999)` berechnen.

**Rückgabe:** Moran-Ergebnis mit `.I` und `.p_sim`.

#### `morans_i(daten, modelle)`
Ruft `moran_berechnen` viermal auf: Lärm, Benachteiligungsindex, Residuen A1, Residuen A2 (aus den klassischen Modellen; die Residuen sind in beiden Varianten gleich) → `morans_i.csv`.

### Schritt 8: Karten

#### `karte_zeichnen(daten, spalte, farbschema)`
Zeichnet eine Choroplethenkarte: jeder Planungsraum nach seinem Wert eingefärbt, fehlende Werte hellgrau, Bezirksgrenzen schwarz → `map_<spalte>.png`. Wird in `main()` dreimal aufgerufen (Lärm, Index, Miete).

#### `cluster_karte_zeichnen(daten)`
1. nicht geclusterte Gebiete grau zeichnen,
2. in einer Schleife jeden Cluster in seiner Farbe zeichnen und dabei die Legende (Farbkästchen + Text mit Anzahl) aufbauen,
3. Bezirksgrenzen mit Namen → `map_kmeans_cluster.png`.

### Schritt 9: Ergebnis

#### `ergebnis_text(daten, modelle, anova_p, moran_tabelle)`
Formuliert die Antwort auf die Leitfrage **aus den berechneten Zahlen**, nicht als festen Text:
1. mittlerer Lärm je Quintil, Abstand Q1 zum Rest, Spannweite Q2–Q5,
2. Anteil der Gebiete im Cluster „Lärm hoch · Benachteiligung hoch“,
3. H1-Entscheidung per `if`: Ist der korrigierte p-Wert der Benachteiligung in A2 < 0,05 **und** der Effekt positiv?
4. Sätze zu A1/A2, ANOVA, H2, H3 und Moran zusammensetzen.

Würden sich die Daten ändern, würde sich der Text automatisch anpassen.

**Rückgabe:** Liste von Textzeilen.

#### `ergebnisgrafik(daten, modelle, anova_p, moran_tabelle)`
Speichert den Text → `ergebnis_zusammenfassung.txt` und zeichnet die Ergebnisgrafik mit vier Feldern → `ergebnis_leitfrage.png`:
- **Feld A:** Boxplot Lärm je Quintil + rote Linie der Mittelwerte,
- **Feld B:** Balken mittlerer Anteil Fassaden > 65 dB je Quintil,
- **Feld C:** Streudiagramm Index gegen Lärm mit Regressionsgerade `y = b0 + b1 · x` aus Modell A1,
- **Feld D:** Antworttext (mit `textwrap.fill` auf 70 Zeichen umgebrochen).

### Hauptprogramm: `main()`

```text
Profile bestimmen (Standard: 2022 und aktuell)
Eingabedateien für alle gewählten Profile prüfen
Für jedes Profil:
    datenstand_konfigurieren(datenstand)
    daten = daten_laden()                         Schritt 1
    daten = pca_benachteiligungsindex(daten)      Schritt 2
    Quintile Q1–Q5 bilden (pd.qcut)
    deskriptive_statistik(daten)                  Schritt 3
    anova_p = anova(daten)                        Schritt 4
    modelle = regressionen(daten)                 Schritt 5
    daten["cluster"] = kmeans_clustering(daten)   Schritt 6
    moran_tabelle = morans_i(daten, modelle)      Schritt 7
    4 Karten zeichnen                             Schritt 8
    ergebnisgrafik(...)                           Schritt 9
    daten_speichern(daten)
Wenn beide Profile liefen:
    datenstaende_korrelieren()
```

Aufruf: `python berlin_data_science.py` rechnet beide Datenstände. Mit `--datenstand 2022` oder `--datenstand aktuell` kann man gezielt nur einen Lauf ausführen. `if __name__ == "__main__"` sorgt dafür, dass `main()` nur beim direkten Ausführen startet, nicht beim Import.

---

## 4.4 Häufige Fehlermeldungen

| Meldung | Ursache | Lösung |
|---|---|---|
| `Fehlende Eingabedateien für den Datenstand ...` | eine der für dieses Profil benötigten Rohdateien oder die Lärmaggregation fehlt | Dateinamen prüfen; Lärmdatei bei Bedarf mit `python aggregate_noise.py` erzeugen |
| `Doppelte Planungsraum-IDs in ...` | Eine Tabelle enthält eine ID zweimal | Excel-Datei prüfen |
| `ModuleNotFoundError: No module named ...` | Pakete nicht installiert oder falsche Umgebung aktiv | `.venv` aktivieren, `pip install -r requirements.txt` |
