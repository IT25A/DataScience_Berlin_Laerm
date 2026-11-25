# 2. Die Daten: Herkunft, Inhalt und Aufbereitung

Alle Daten stammen aus **offiziellen, öffentlich zugänglichen Quellen** des Landes Berlin bzw. der landeseigenen Investitionsbank Berlin (IBB). Wir haben nichts selbst erhoben, sondern vorhandene Daten zusammengeführt. Das ist typisch für Data Science: Der größte Teil der Arbeit besteht darin, Daten aus verschiedenen Quellen zu finden, zu prüfen und zusammenzubringen.

## 2.1 Überblick über die Datenquellen

| Datensatz | Herausgeber | Stand | Datei im Projekt | Was nutzen wir daraus? |
|---|---|---|---|---|
| LOR-Planungsräume (Gebietsgrenzen) | Land Berlin, ODIS / Geoportal | 2021 | `data/raw/planungsraeume.geojson` | Umrisse der 542 Gebiete, Bezirk, Prognoseraum, Innere/Äußere Stadt |
| Strategische Lärmkarte 2022 | Senatsverwaltung, Umweltatlas | 2022 | wird live geladen → `data/processed/laermdaten_aggregiert.csv` | Lärmpegel an ca. 3,8 Mio. Fassadenpunkten |
| MSS 2025, Tabelle 1 | Senatsverwaltung für Stadtentwicklung | 31.12.2024 | `data/raw/sozialdaten.xlsx` | Einwohnerzahl |
| MSS 2025, Tabelle 2.1 | Senatsverwaltung für Stadtentwicklung | 31.12.2024 | `data/raw/mss2025_indexindikatoren_anteile_plr.xlsx` | Die vier sozialen Indikatoren S1–S4 |
| MSS 2025, Tabelle 3 | Senatsverwaltung für Stadtentwicklung | 31.12.2024 | `data/raw/mss2025_indexindikatoren_zwerte_plr.xlsx` | Amtlicher Status-Index (nur zur Kontrolle unserer PCA) |
| IBB Wohnungsmarktbericht 2025 | Investitionsbank Berlin | 2025 | `data/raw/Mietdaten.xlsx` | Median-Angebotsmiete und Zahl der Inserate pro PLR |

**Links:**
- Gebietsgrenzen: https://daten.odis-berlin.de/
- Lärmkarte 2022: https://www.berlin.de/umweltatlas/verkehr-laerm/laermbelastung/2022/download/ (WFS-Dienst: https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022)
- MSS 2025: https://www.berlin.de/sen/stadt/stadtdaten/stadtwissen/monitoring-soziale-stadtentwicklung/bericht-2025/tabellen-der-index-indikatoren-zum-bericht-2025/
- IBB: https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2025.html

---

## 2.2 Die Gebietsgrenzen (Planungsräume)

**Was ist das?** Eine Geodatei (GeoJSON), in der für jeden der 542 Planungsräume die Umrisslinie (ein Polygon) gespeichert ist – also eine digitale Landkarte.

**Wichtige Spalten:**

| Spalte | Bedeutung | Beispiel |
|---|---|---|
| `plr_id` | achtstellige Kennnummer des Planungsraums | `08100207` |
| `plr_name` | Name | `Rollberg` |
| `pgr_id` | Kennnummer des Prognoseraums (58 Stück) | `0810` |
| `bez` | Bezirk | `08 - Neukölln` |
| `stadtraum_name` | `Innere Stadt` oder `Äußere Stadt` (ungefähr innerhalb/außerhalb des S-Bahn-Rings) | `Innere Stadt` |
| `geometry` | die Umrisslinie | (Polygon) |

**Koordinatensystem:** EPSG:25833 (ETRS89 / UTM Zone 33N). Das ist ein Koordinatensystem in **Metern**. Deshalb können wir Flächen direkt in m² berechnen.

**Wozu brauchen wir die Datei?**
- als gemeinsame Basis, an die alle anderen Daten angehängt werden,
- um Lärmpunkte den Gebieten zuzuordnen,
- um die Fläche (für die Einwohnerdichte) zu berechnen,
- um Nachbarschaften für Moran's I zu bestimmen,
- um Karten zu zeichnen.

---

## 2.3 Die Lärmdaten (Strategische Lärmkarte 2022)

### Was ist eine strategische Lärmkarte?
Die EU verpflichtet große Städte, alle fünf Jahre Lärmkarten zu erstellen (Umgebungslärmrichtlinie 2002/49/EG). Berlin hat das zuletzt für 2022 getan. Der Lärm wird dabei **nicht gemessen, sondern berechnet** – aus Verkehrszahlen, Geschwindigkeiten, Straßenbelag, Gebäudehöhen usw.

### Was sind Fassadenpegel?
Für fast jedes Gebäude in Berlin wurden mehrere Punkte vor der Fassade festgelegt (z. B. alle paar Meter rund ums Haus). Für jeden Punkt wurde berechnet, wie laut es dort ist. Insgesamt sind das **3.799.746 Punkte**.

### Was bedeuten die Werte?
- **dB(A)** (Dezibel, A-bewertet) ist die Einheit. Das „A“ bedeutet, dass die Messung an das menschliche Gehör angepasst ist.
- Dezibel sind **logarithmisch**:
  - +3 dB = doppelte Schallenergie (z. B. doppelt so viele Autos),
  - +10 dB = wird als etwa **doppelt so laut empfunden**.
- **LDEN** (Level Day-Evening-Night) ist der Tagesmittelwert, bei dem der Abend (18–22 Uhr) um 5 dB und die Nacht (22–6 Uhr) um 10 dB „strenger“ gezählt werden, weil Lärm dann mehr stört:

$$
L_{DEN} = 10 \cdot \log_{10}\left(\frac{1}{24}\left(12 \cdot 10^{\frac{L_{Tag}}{10}} + 4 \cdot 10^{\frac{L_{Abend}+5}{10}} + 8 \cdot 10^{\frac{L_{Nacht}+10}{10}}\right)\right)
$$

  Diesen Wert berechnet nicht unser Projekt, er wird von der Lärmkarte geliefert.

**Zur Einordnung:**

| LDEN | Beispiel / Bewertung |
|---|---|
| < 50 dB | ruhige Wohnstraße, Hinterhof |
| 53 dB | WHO-Empfehlung: Straßenverkehrslärm sollte darunter liegen, darüber steigt das Gesundheitsrisiko |
| 65 dB | Schwellenwert der Lärmaktionsplanung – hohe Belastung |
| > 70 dB | Hauptverkehrsstraße, deutliches Gesundheitsrisiko |

### Welche Felder nutzen wir?
Der Datensatz enthält pro Punkt u. a. `ges_den` (Gesamtlärm LDEN aus Straße, Tram/U-Bahn oberirdisch und Flugverkehr), `ges_n` (Gesamtlärm nachts), `str_den` (nur Straßenlärm). In der Analyse verwenden wir vor allem **`ges_den`**.

### Wie kommen die Punkte in die Planungsräume? (Aggregation)
Das macht das Skript `aggregate_noise.py`:

1. **Herunterladen:** Die 3,8 Mio. Punkte werden in Paketen zu je 100.000 vom offiziellen Web-Dienst (WFS) geladen.
2. **Räumlicher Join:** Für jeden Punkt wird geprüft, in welchem Planungsraum-Polygon er liegt („Punkt-in-Polygon“). 3.799.712 Punkte werden zugeordnet; 34 liegen exakt auf einer Grenzlinie und fallen weg (vernachlässigbar).
3. **Zusammenfassen pro Planungsraum** zu drei Kennzahlen:

**a) Energetischer Mittelwert** (Hauptwert `laerm_gesamt_lden_db`)

Dezibel darf man nicht einfach normal mitteln, weil sie logarithmisch sind. Stattdessen rechnet man die Werte zurück in Schallenergie, mittelt die Energie und rechnet wieder in Dezibel um:

$$
L_{PLR} = 10 \cdot \log_{10}\left(\frac{1}{n}\sum_{i=1}^{n} 10^{L_i/10}\right)
$$

*Beispiel:* Zwei Fassaden mit 50 dB und 70 dB.
- Normaler Mittelwert: (50 + 70) / 2 = 60 dB
- Energetischer Mittelwert: 10 · log₁₀((10⁵ + 10⁷)/2) = 10 · log₁₀(5.050.000) ≈ **67,0 dB**

Der energetische Mittelwert ist physikalisch korrekt, wird aber stark von den **lautesten** Fassaden bestimmt. Ein Gebiet mit einer einzigen sehr lauten Hauptstraße erscheint dadurch laut, auch wenn die meisten Wohnungen ruhig liegen.

**b) Median** (`laerm_gesamt_lden_median_db`) – der mittlere Wert aller Fassaden (die Hälfte ist lauter, die Hälfte leiser). Er wird in der vereinfachten Analyse nicht verwendet, steht aber in der CSV-Datei.

**c) Anteil Fassaden über 65 dB** (`anteil_fassaden_lden_ueber_65_prozent`) – wie viel Prozent der Fassadenpunkte über dem Schwellenwert von 65 dB liegen. Das ist sehr anschaulich („in diesem Gebiet sind 8 % der Fassaden stark belastet“).

**Ergebnis:** Alle 542 Planungsräume haben einen Lärmwert. Im Durchschnitt hat ein Planungsraum 7.011 Fassadenpunkte (Minimum 17 im fast unbewohnten „Pankower Tor“, Maximum 42.267).

| Kennzahl | Mittelwert | Minimum | Maximum |
|---|---:|---:|---:|
| LDEN energetisch | 57,3 dB | 46,4 dB (Alt-Rixdorf) | 73,2 dB (Lüneburger Straße) |
| Anteil Fassaden > 65 dB | 6,5 % | 0 % | 100 % (Pankower Tor, nur 17 Punkte) |

**Qualitätsprüfung:** Wir haben für drei Planungsräume die Punkte unabhängig neu vom Web-Dienst geladen und nachgerechnet – die Werte stimmen exakt überein.

---

## 2.4 Die Sozialdaten (Monitoring Soziale Stadtentwicklung 2025)

### Was ist das MSS?
Die Berliner Senatsverwaltung für Stadtentwicklung erstellt alle zwei Jahre das „Monitoring Soziale Stadtentwicklung“. Es beschreibt für jeden Planungsraum die soziale Lage anhand von vier sogenannten **Status-Indikatoren**:

| Kürzel | Indikator | Genaue Definition (vereinfacht) | Berliner Mittel |
|---|---|---|---:|
| **S1** | Arbeitslosigkeit | Anteil der Arbeitslosen nach SGB II („Bürgergeld“) an den Einwohnern von 15 Jahren bis zum Rentenalter | 4,7 % |
| **S2** | Alleinerziehende | Anteil der Kinder unter 18, die in Alleinerziehenden-Haushalten leben | 24,0 % |
| **S3** | Transferbezug | Anteil der Einwohner, die Sozialleistungen beziehen (SGB II ohne Arbeitslose, Sozialhilfe, Grundsicherung im Alter) | 9,9 % |
| **S4** | Kinderarmut | Anteil der Kinder unter 15, die in Haushalten mit SGB-II-Bezug leben | 20,8 % |

Stand der Daten: 31.12.2024.

### Welche Tabellen nutzen wir?
- **Tabelle 1** (`sozialdaten.xlsx`): Einwohnerzahl und die amtliche Statusklasse (hoch / mittel / niedrig / sehr niedrig). Wir nutzen daraus die **Einwohnerzahl**.
- **Tabelle 2.1** (`mss2025_indexindikatoren_anteile_plr.xlsx`): die vier Indikatoren S1–S4 in Prozent. **Das ist die Grundlage unseres Benachteiligungsindex.**
- **Tabelle 3** (`mss2025_indexindikatoren_zwerte_plr.xlsx`): der amtliche, stetige Status-Index. Wir nutzen ihn **nur zur Kontrolle**: Stimmt unser selbst berechneter PCA-Index mit dem amtlichen überein? (Ja: Korrelation 0,998.)

### Fehlende Werte
7 der 542 Planungsräume haben keine Sozialdaten, weil das MSS sie ausschließt – es sind Gebiete mit kaum Einwohnern (z. B. „Pankower Tor“ mit 0, „Landweg“ mit 0, „Gewerbegebiet Bitterfelder Straße“ mit 1.221 Einwohnern). Das ist korrekt und kein Fehler. Es bleiben **535 Planungsräume** mit Sozialdaten.

---

## 2.5 Die Mietdaten (IBB Wohnungsmarktbericht 2025)

### Was ist das?
Die Investitionsbank Berlin wertet jedes Jahr alle Wohnungsinserate aus (Datenbasis: VALUE Marktdatenbank). Für jeden Planungsraum gibt es:
- die **Median-Angebotsmiete** in EUR pro m² Wohnfläche, netto kalt, pro Monat,
- die **Fallzahl**, also die Zahl der ausgewerteten Inserate.

**Median** heißt: Die Hälfte der Inserate ist teurer, die Hälfte billiger. Der Median ist robuster gegen einzelne Luxuswohnungen als der Durchschnitt.

### Mindestfallzahl
Die IBB schreibt selbst in die Tabelle, dass Planungsräume mit **weniger als 21 Inseraten nicht repräsentativ** sind. Ein Median aus 3 Inseraten ist reiner Zufall. Deshalb setzen wir die Miete in diesen Gebieten auf „fehlend“ (wir erfinden keinen Ersatzwert).

| | Anzahl PLR |
|---|---:|
| alle Planungsräume | 542 |
| ohne jedes Inserat („keine Daten“) | 20 |
| mit 1–20 Inseraten (auf fehlend gesetzt) | 88 |
| **mit gültigem Mietwert** | **434** |

**Nebenwirkung:** Gebiete mit vielen Einfamilienhäusern (meist wohlhabend) haben wenige Mietinserate und fallen öfter heraus. Wohlhabende Gebiete sind in der Mietanalyse daher etwas unterrepräsentiert (16 % aller Gebiete, aber nur 11 % der Mietstichprobe).

**Wichtig:** Angebotsmieten sind die Preise für **neu angebotene** Wohnungen. Wer seit 20 Jahren in seiner Wohnung lebt, zahlt meist deutlich weniger. Die Daten beschreiben also den Wohnungsmarkt, nicht die Mietbelastung der Bewohner.

---

## 2.6 Datenaufbereitung Schritt für Schritt

Die Aufbereitung passiert in `berlin_data_science.py`, Funktion `load_all_data()` (Details in [04_code.md](04_code.md)).

### Schritt 1: Excel-Tabellen robust einlesen
Die Excel-Dateien der Behörden haben Titelzeilen, mehrzeilige Überschriften und Fußnoten. Statt fest „ab Zeile 10“ zu lesen, sucht das Skript **jede Zeile, in der eine gültige achtstellige Planungsraum-ID steht**. So werden Überschriften und Fußnoten automatisch ignoriert, und das Skript funktioniert auch, wenn eine Behörde eine Zeile einfügt.

### Schritt 2: IDs vereinheitlichen
Excel speichert IDs manchmal als Zahl und verliert dabei die führende Null (`1100101` statt `01100101`). Das Skript wandelt alle IDs in achtstellige Texte um. Nur so passen die Tabellen zusammen.

### Schritt 3: Zusammenführen (Join)
Alle Tabellen werden über die PLR-ID an die Gebietsgrenzen angehängt:

```text
Gebietsgrenzen (542)
   + Sozialdaten (535 mit Werten)
   + Mietdaten   (522 mit Werten)
   + Lärmdaten   (542 mit Werten)
   = ein Datensatz mit 542 Zeilen
```

Dabei wird mit `validate="one_to_one"` geprüft, dass jede ID in jeder Tabelle nur einmal vorkommt. Gäbe es Duplikate, würde das Skript abbrechen, statt still falsche Daten zu erzeugen.

### Schritt 4: Namensabgleich
Zur Kontrolle vergleicht das Skript die Gebietsnamen der IBB-Tabelle mit denen der Gebietsgrenzen. Ergebnis (`outputs/pruefung_namensabweichungen_ibb.csv`): 5 Abweichungen. Drei sind nur Schreibvarianten („Meller Bogen“ / „Mellerbogen“). **Auffällig:** Bei den IDs `12500926` und `12500930` sind „Wittenau Mitte“ und „Wittenau Süd“ vertauscht. Ob dort auch die Mietwerte vertauscht sind, ist ungeklärt – das betrifft 2 von 434 Gebieten und wird als Limitation genannt.

### Schritt 5: Neue Variablen berechnen

| Neue Variable | Berechnung | Wozu? |
|---|---|---|
| `einwohnerdichte` | Einwohner / Fläche in km² | Kontrollvariable: dichte Gebiete haben mehr Verkehr |
| `log_einwohnerdichte` | log(1 + Einwohnerdichte) | Die Dichte ist sehr ungleich verteilt (0 bis 35.600 EW/km²). Der Logarithmus staucht große Werte, damit wenige extrem dichte Gebiete die Regression nicht dominieren. Das „+1“ verhindert log(0) bei unbewohnten Gebieten. |
| `innere_stadt` | 1, wenn `stadtraum_name` = „Innere Stadt“, sonst 0 | Kontrollvariable für die zentrale Lage |
| `angebotsmiete_median_eur_m2` | Median-Miete, aber nur bei ≥ 21 Inseraten | gefilterter Mietwert |
| `benachteiligungsindex` | PCA aus S1–S4 (siehe [03_methoden.md](03_methoden.md)) | unsere zentrale Sozialvariable |
| `deprivationsquintil` | Einteilung des Index in 5 gleich große Gruppen (Q1–Q5) | für ANOVA und Grafiken |

### Schritt 6: Qualitätsbericht
Die Datei `outputs/datenqualitaet.csv` listet für jede Variable, wie viele gültige und fehlende Werte es gibt – **nach** allen Filtern.

### Schritt 7: Speichern
Der fertige Datensatz wird gespeichert als
- `data/processed/berlin_merged.gpkg` (mit Geometrie, z. B. für QGIS),
- `data/processed/berlin_merged.csv` (ohne Geometrie, z. B. für Excel).

Hinweis zum Öffnen der CSV: Damit die führenden Nullen der IDs erhalten bleiben, die Spalte `plr_id` als Text einlesen (in pandas: `pd.read_csv(..., dtype={"plr_id": str})`).

---

## 2.7 Was wir bewusst nicht verwenden

| Datei / Daten | Grund |
|---|---|
| Straßennetzdaten ohne Pegel | enthalten keine Dezibelwerte |
| MSS-Statusklasse (1–4) als Analysevariable | nur 4 grobe Stufen; der stetige PCA-Index enthält mehr Information |
| Mieten aus Gebieten mit < 21 Inseraten | nicht repräsentativ (IBB-Vorgabe) |
| Fehlende Werte durch Mittelwerte ersetzen | würde künstliche Daten erzeugen und die Ergebnisse verfälschen |
