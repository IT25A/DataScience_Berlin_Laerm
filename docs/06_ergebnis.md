# 6. Das Endergebnis: Was haben wir herausgefunden?

Alle Zahlen beziehen sich auf das **Bezugsjahr 2022** (Lärm 2022, Sozialdaten 31.12.2022, Mieten 2022).

## 6.1 Die Antwort auf die Leitfrage in einem Absatz

> **In Berlin sind sozial benachteiligte Planungsräume im Durchschnitt nicht systematisch lauter als andere.** Ein linearer Zusammenhang zwischen sozialer Benachteiligung und Lärm ist statistisch nicht nachweisbar – auch nicht, wenn man Dichte und Innenstadtlage berücksichtigt und die räumliche Abhängigkeit korrigiert. Nur die am wenigsten benachteiligten Gebiete sind etwas leiser (ca. 2,5 dB). Entscheidend für den Lärm ist die **Lage**: Innenstadtgebiete sind deutlich lauter, und sie sind gleichzeitig teurer. Trotzdem gibt es einen klar abgrenzbaren **Gebietstyp, der laut und benachteiligt zugleich ist** – rund ein Viertel der untersuchten Gebiete, vor allem in Wedding, Moabit-West, Tempelhof-Schöneberg und Spandau-Mitte. Umweltungerechtigkeit beim Lärm ist in Berlin also **kein stadtweites Muster, sondern ein räumlich konzentriertes Problem bestimmter innenstadtnaher Quartiere**.

---

## 6.2 Die Hypothesen im Einzelnen

### H1 – „Benachteiligte Gebiete sind lauter“ → **nicht gestützt**

**Was die Daten zeigen:**

| Prüfung | Ergebnis | Bedeutung |
|---|---|---|
| Korrelation Index – Lärm | r = 0,08 | praktisch kein linearer Zusammenhang |
| Regression A1 (ohne Kontrollen) | +0,29 dB pro SD, p = 0,318 (korrigiert) | nicht signifikant, winziger Effekt |
| Regression A2 (mit Dichte und Lage) | +0,27 dB pro SD, p = 0,215 (korrigiert) | nicht signifikant |
| ANOVA über Quintile | F = 14,3, p < 0,001 | Gruppen unterscheiden sich … |
| Mittelwerte der Quintile | Q1 55,3 · Q2 58,8 · Q3 57,7 · Q4 57,4 · Q5 57,3 dB | … aber nur Q1 ist anders |

**Wie passt „ANOVA signifikant“ mit „Regression nicht signifikant“ zusammen?**
Das ist kein Widerspruch, sondern genau die Erkenntnis:
- Die **Regression** sucht eine **gerade Linie** („je benachteiligter, desto lauter“). Die gibt es nicht.
- Die **ANOVA** sucht **irgendeinen** Unterschied zwischen den Gruppen. Den gibt es: Die wohlhabendsten 20 % (Q1) wohnen leiser.
- Zusammen heißt das: **Wohlhabende Gebiete sind etwas privilegiert, aber benachteiligte Gebiete sind nicht zusätzlich belastet.** Zwischen „durchschnittlich“ und „stark benachteiligt“ gibt es beim Lärm keinen Unterschied.

**Warum die räumliche Korrektur hier wichtig ist:**
Ohne Korrektur läge Modell A1 mit p = 0,068 knapp an der 5-%-Grenze – man wäre versucht, von einer „Tendenz“ zu sprechen. Weil benachbarte Gebiete sich ähneln (Moran's I), sind diese klassischen p-Werte zu optimistisch. Mit der Korrektur (p = 0,318) bleibt von dieser „Tendenz“ nichts übrig.

**Warum gibt es keinen linearen Zusammenhang?**
Die Karten zeigen den Grund: Es gibt **zwei Arten von benachteiligten Gebieten**:

| Typ | Beispiel | Lärm | Benachteiligungsindex |
|---|---|---:|---:|
| innerstädtisches Altbauquartier | Rollberg (Neukölln) | 59,7 dB | +2,13 |
| Großsiedlung am Stadtrand | Rollbergesiedlung (Reinickendorf) | 52,1 dB | +2,54 |

Beide Gebiete sind stark benachteiligt, liegen beim Lärm aber 7,6 dB auseinander. Die lauten Innenstadtgebiete und die leisen Stadtrand-Siedlungen heben sich im Durchschnitt gegenseitig auf. Deshalb ist die Gerade fast waagerecht.

**Wie groß ist der Effekt der Lage im Vergleich?**
Innenstadtgebiete sind bei gleicher Benachteiligung im Mittel **3,6 dB lauter** (p < 0,001). Der Effekt der Lage ist also rund **13-mal so groß** wie der (nicht signifikante) Effekt der Benachteiligung.

### H2 – „Lärm hängt mit den Mieten zusammen“ → **gestützt**

| Einfluss auf die Angebotsmiete (2022) | Effekt | p (korrigiert) |
|---|---:|---:|
| +1 dB Lärm | **+0,27 EUR/m²** | < 0,001 |
| +1 SD Benachteiligung | **−1,77 EUR/m²** | < 0,001 |
| Innere Stadt (statt Äußere) | **+3,24 EUR/m²** | < 0,001 |
| Modell erklärt | 51 % der Mietunterschiede | |

**Interpretation:**
- Auf den ersten Blick überraschend: **Lautere Gebiete sind teurer**, nicht billiger. Das heißt nicht, dass Menschen gern Lärm bezahlen. Lärm ist hier ein **Merkmal zentraler, begehrter Lagen** – dort, wo viel Verkehr ist, sind auch Arbeitsplätze, Kultur, Gastronomie, ÖPNV. Auch nach Berücksichtigung von „Innere Stadt“ bleibt ein Rest dieses Effekts, weil die grobe Unterscheidung innen/außen nicht alle Lagevorteile erfasst.
- **Benachteiligte Gebiete sind deutlich günstiger** – das ist der stärkste Effekt im Modell.
- **Keine Kausalität:** Wir können nicht sagen, dass Lärm die Miete erhöht oder dass niedrige Mieten Benachteiligung verursachen. Wir sehen nur, was zusammen auftritt.
- **Euro-Beträge gelten für 2022.** Bis 2025 ist das Mietniveau um rund 37 % gestiegen. Mit den Mieten 2025 ergeben sich +0,24 EUR/m² pro dB und −1,98 EUR/m² pro SD – gleiche Richtung, gleiche Aussage.

### H3 – „Es gibt interpretierbare Gebietstypen“ → **gestützt**

| Cluster | Anteil | Beschreibung | Wo? |
|---|---:|---|---|
| C1 leise · benachteiligt · günstig | 22 % | Großsiedlungen am Stadtrand | Marzahn-Hellersdorf, Neu-Hohenschönhausen, Gropiusstadt, Märkisches Viertel |
| C2 leise · wohlhabend · mittlere Miete | 26 % | Einfamilienhausgebiete | Steglitz-Zehlendorf, Köpenick, Pankow-Nord |
| **C3 laut · benachteiligt · günstig** | **26 %** | **mehrfach belastete innenstadtnahe Quartiere** | **Wedding, Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte, Teile Nord-Neuköllns** |
| C4 laut · wohlhabend · teuer | 26 % | begehrte Innenstadtlagen | Charlottenburg, Mitte, Prenzlauer Berg, Friedrichshain |

**Interpretation:** Die vier Typen bilden fast ein „2 × 2“-Schema aus laut/leise und benachteiligt/wohlhabend. Für die Umweltgerechtigkeit ist **C3** entscheidend: 88 Gebiete, in denen soziale Benachteiligung und hohe Lärmbelastung zusammenkommen. Hier wäre Lärmschutz (z. B. Tempo 30, Lärmschutzfenster, Verkehrsberuhigung) sozialpolitisch besonders zielgenau.

Hinweis: Geclustert werden nur die 341 Gebiete mit verlässlichem Mietwert 2022. Mit den Mieten 2025 (434 Gebiete) ergibt sich dieselbe Typologie; 92 % der Gebiete werden beim Typ „laut und benachteiligt“ gleich zugeordnet.

### Räumliche Struktur

| | Moran's I |
|---|---:|
| Lärm | 0,46 |
| Benachteiligung | 0,43 |
| Residuen A2 | 0,31 |

Lärm und Benachteiligung sind stark räumlich geclustert: Laute Gebiete liegen neben lauten, benachteiligte neben benachteiligten. Auch die Fehler der Regression sind gehäuft. Deshalb haben wir die Standardfehler nach Prognoseraum geclustert. Ergebnis: Die p-Werte werden größer (A1: 0,068 → 0,318), aber **keine Schlussfolgerung ändert sich** – im Gegenteil, eine scheinbare „Tendenz“ verschwindet.

---

## 6.3 Was wir sagen dürfen – und was nicht

### ✅ Zulässige Aussagen
- „In Berlin gab es 2022 auf Ebene der Planungsräume **keinen signifikanten linearen Zusammenhang** zwischen sozialer Benachteiligung und Verkehrslärm.“
- „Die am wenigsten benachteiligten Gebiete sind im Mittel etwa 2,5 dB leiser als der Rest.“
- „Die Lage (Innenstadt vs. Stadtrand) erklärt die Lärmunterschiede deutlich besser als die soziale Lage.“
- „Lautere Gebiete haben höhere, benachteiligte Gebiete niedrigere Angebotsmieten.“
- „Rund ein Viertel der untersuchten Gebiete ist zugleich laut und sozial benachteiligt; diese Gebiete konzentrieren sich in bestimmten innenstadtnahen Quartieren.“
- „Lärm und soziale Lage sind räumlich stark geclustert; das haben wir in der Regression berücksichtigt.“
- „Alle Daten stammen aus demselben Jahr (2022); mit neueren Sozial- und Mietdaten ergeben sich dieselben Aussagen.“

### ❌ Unzulässige Aussagen

| Falsche Aussage | Warum falsch? |
|---|---|
| „Arme Menschen sind in Berlin nicht von Lärm betroffen.“ | Wir haben Gebiete untersucht, keine Personen (ökologischer Fehlschluss). Innerhalb eines Gebiets können ärmere Haushalte trotzdem öfter an der lauten Straße wohnen. |
| „Es ist bewiesen, dass es keine Umweltungerechtigkeit gibt.“ | „Nicht signifikant“ heißt „kein Beleg gefunden“, nicht „Gegenteil bewiesen“. Außerdem zeigt Cluster C3, dass es mehrfach belastete Gebiete gibt. |
| „Es gibt eine Tendenz, dass benachteiligte Gebiete lauter sind (p = 0,07).“ | Das ist der klassische p-Wert ohne räumliche Korrektur. Korrigiert ist p = 0,32 – keine Tendenz. |
| „Lärm macht Wohnungen teurer.“ | Korrelation ist keine Kausalität. Wahrscheinlicher ist: Zentrale Lage macht Wohnungen teurer **und** lauter. |
| „Benachteiligung verursacht niedrige Mieten.“ | ebenfalls keine Kausalität; die Richtung kann auch umgekehrt sein (günstige Mieten ziehen einkommensschwache Haushalte an). |
| „In Wedding sind alle Bewohner arm und lärmbelastet.“ | Clusterwerte sind Durchschnitte über Gebiete. |
| „Die Ergebnisse gelten auch für andere Städte.“ | Berlin hat eine besondere Struktur (z. B. Großsiedlungen am Stadtrand). |

---

## 6.4 Grenzen der Untersuchung

| Grenze | Auswirkung | Wie gehen wir damit um? |
|---|---|---|
| **Querschnitt, ein Zeitpunkt** | keine Aussagen über Ursache und Wirkung | nur Zusammenhänge formulieren |
| **Bezugsjahr 2022** | nicht der neueste Stand; neuere Lärmkarten gibt es erst 2027 | Prüfung mit Sozialdaten 2024 und Mieten 2025: gleiche Aussagen (siehe [02_daten.md](02_daten.md), 2.6) |
| **Gebietsebene** | keine Aussagen über Personen | immer „Gebiete mit …“ formulieren |
| **Fassadenpunkte nicht einwohnergewichtet** | ein Gebiet mit einer lauten Hauptstraße und vielen ruhigen Hinterhöfen kann laut erscheinen | zusätzlich Anteil Fassaden > 65 dB betrachtet (gleiches Muster) |
| **Angebotsmieten ≠ Bestandsmieten** | Mieten beschreiben den Markt, nicht die Belastung der Bewohner | offen benennen |
| **Mietfilter (≥ 21 Inserate)** | 2022 nur 341 Gebiete mit Mietwert; wohlhabende Einfamilienhausgebiete sind in Mietmodell und Clustering unterrepräsentiert | offen benennen; mit Mieten 2025 (434 Gebiete) gleiche Ergebnisse |
| **Wittenau Mitte/Süd vertauscht** (IBB) | höchstens 2 von 341 Gebieten evtl. falsche Miete | vernachlässigbar, offen benennen |
| **Residuen auch mit Korrektur räumlich abhängig** | Modell erfasst nicht die ganze räumliche Struktur | geclusterte Standardfehler; räumliche Regressionsmodelle wären der nächste Schritt (außerhalb des Modulumfangs) |
| **ANOVA nicht räumlich korrigiert** | p-Wert eher zu optimistisch | bei p < 0,001 ändert das nichts an der Aussage |
| **Kontrollvariablen grob** („Innere Stadt“ nur 0/1) | Lageeffekte werden nur teilweise erfasst | offen benennen |

---

## 6.5 Typische Rückfragen in der Präsentation – und Antworten

**„Warum habt ihr Daten von 2022 genommen und nicht die neuesten?“**
Weil die Lärmkarte nur alle fünf Jahre erscheint und die aktuellste von 2022 ist. Damit Lärm, Sozialdaten und Mieten zusammenpassen, haben wir alles auf 2022 ausgerichtet (MSS-Stand 31.12.2022, Mieten 2022). Mit den neueren Sozialdaten (2024) und Mieten (2025) kommen dieselben Ergebnisse heraus, weil sich das räumliche Muster kaum verändert (Sozialindex 2022 vs. 2024: r = 0,99).

**„Warum habt ihr eine PCA gemacht und nicht einfach die Arbeitslosenquote genommen?“**
Weil soziale Benachteiligung mehr ist als Arbeitslosigkeit. Die vier Indikatoren hängen stark zusammen; die PCA fasst sie objektiv zu einer Zahl zusammen, die 81 % ihrer Information enthält. Unser Index stimmt zu 99,8 % mit dem amtlichen Index des Senats überein.

**„Euer Ergebnis ist nicht signifikant – ist das Projekt dann gescheitert?“**
Nein. Ein nicht signifikantes Ergebnis ist ein Ergebnis. Es widerlegt die einfache Vorstellung „je ärmer, desto lauter“ für Berlin und zeigt stattdessen, dass die Belastung auf bestimmte Quartiere konzentriert ist. Das ist für die Stadtplanung sogar hilfreicher.

**„Warum ist die ANOVA signifikant, die Regression aber nicht?“**
Die Regression prüft einen geradlinigen Zusammenhang, die ANOVA beliebige Unterschiede zwischen Gruppen. Es gibt einen Unterschied (die wohlhabendsten Gebiete sind leiser), aber keinen durchgehenden Anstieg.

**„Habt ihr berücksichtigt, dass benachbarte Gebiete sich ähneln?“**
Ja. Moran's I zeigt eine deutliche räumliche Clusterung (I ≈ 0,46). Deshalb haben wir die Standardfehler nach den 58 Prognoseräumen geclustert. Ohne diese Korrektur hätte Modell A1 knapp an der Signifikanz gelegen (p = 0,068) – mit Korrektur ist p = 0,318.

**„Warum 4 Cluster?“**
Die Elbow-Kurve flacht ab k = 4 deutlich ab, und 4 Cluster ergeben eine klar interpretierbare Typologie (laut/leise × benachteiligt/wohlhabend).

**„Warum ist laut teurer? Das ist doch unlogisch.“**
Lärm steht hier für zentrale Lage. Zentrale Gebiete sind begehrt (Arbeitsplätze, Kultur, ÖPNV) und gleichzeitig verkehrsreich. Das Modell zeigt einen Zusammenhang, keinen ursächlichen Effekt von Lärm auf die Miete.

**„Warum habt ihr Gebiete mit weniger als 21 Inseraten weggelassen?“**
Die IBB selbst kennzeichnet diese Werte als nicht repräsentativ. Ein Median aus 3 Inseraten ist Zufall. Wir haben die Werte nicht durch Schätzungen ersetzt, um keine künstlichen Daten zu erzeugen.

**„Woher wisst ihr, dass die Lärmdaten stimmen?“**
Es sind die offiziellen EU-Lärmkarten des Landes Berlin. Wir haben die Zusammenfassung pro Gebiet stichprobenartig gegen den offiziellen Webdienst nachgerechnet; die Werte stimmen exakt.

**„Was bedeutet 1 dB? Ist 0,27 dB viel?“**
Nein. Ein Unterschied unter 1 dB ist für Menschen nicht hörbar. +3 dB entsprechen einer Verdopplung des Verkehrs, +10 dB werden als doppelt so laut empfunden.

**„Was würdet ihr als Nächstes untersuchen?“**
1. Lärm nur an Wohngebäuden und nach Einwohnern gewichtet,
2. räumliche Regressionsmodelle,
3. Vergleich mit der Lärmkarte 2027, sobald sie erscheint (Entwicklung über die Zeit),
4. weitere Umweltfaktoren (Luftqualität, Grünflächen, Hitze).

---

## 6.6 Vorschlag für die Ergebnisfolie

**Titel:** Sind sozial benachteiligte Gebiete in Berlin stärker von Lärm betroffen?

**Grafik:** `outputs/ergebnis_leitfrage.png` (oder Feld A + `map_kmeans_cluster.png`)

**Drei Kernaussagen:**
1. **Kein linearer Zusammenhang:** Benachteiligte Gebiete sind im Mittel nicht lauter (p = 0,22). Nur die wohlhabendsten 20 % wohnen ca. 2,5 dB leiser.
2. **Die Lage entscheidet:** Innenstadt = laut und teuer (+3,6 dB, +3,2 EUR/m²).
3. **Konzentrierte Mehrfachbelastung:** Rund ein Viertel der Gebiete ist laut und benachteiligt zugleich – vor allem Wedding, Moabit-West, Tempelhof-Schöneberg, Spandau-Mitte.

**Fußzeile:** Bezugsjahr 2022, Gebietsebene (542 Planungsräume), Querschnitt, keine Kausalaussagen; räumliche Abhängigkeit über geclusterte Standardfehler berücksichtigt.

---

## 6.7 Zuordnung zur Präsentationsaufteilung

| Präsentationsteil (siehe `praesentation.md`) | Relevante Doku | Relevante Outputs |
|---|---|---|
| Problemfrage und Motivation | [01_projekt.md](01_projekt.md) §1.1–1.3 | – |
| Daten sammeln und anpassen | [02_daten.md](02_daten.md) (inkl. 2.6 Bezugsjahr) | `datenqualitaet.csv`, `pruefung_namensabweichungen_ibb.csv` |
| Algorithmen und Statistik | [03_methoden.md](03_methoden.md) | `pca_scree_ladungen.png`, `kmeans_elbow.png`, `regression_uebersicht.csv`, `morans_i.csv` |
| Output und Visualisierung | [05_outputs.md](05_outputs.md) | Karten, `histogramme.png`, `korrelationsmatrix.png` |
| Ergebnis / Auswertung | dieses Kapitel | `ergebnis_leitfrage.png`, `map_kmeans_cluster.png` |
