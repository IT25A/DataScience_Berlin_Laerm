# 6. Das Endergebnis: Was haben wir herausgefunden?

## 6.1 Die Antwort auf die Leitfrage in einem Absatz

> **In Berlin sind sozial benachteiligte Planungsräume im Durchschnitt nicht systematisch lauter als andere.** Ein linearer Zusammenhang zwischen sozialer Benachteiligung und Lärm ist statistisch nicht nachweisbar – auch nicht, wenn man Dichte und Innenstadtlage berücksichtigt und die räumliche Abhängigkeit korrigiert. Nur die am wenigsten benachteiligten Gebiete sind etwas leiser (ca. 2 dB). Entscheidend für den Lärm ist die **Lage**: Innenstadtgebiete sind deutlich lauter, und sie sind gleichzeitig teurer. Trotzdem gibt es einen klar abgrenzbaren **Gebietstyp, der laut und benachteiligt zugleich ist** – knapp ein Viertel der untersuchten Gebiete, vor allem in Wedding, Nord-Neukölln und Schöneberg. Umweltungerechtigkeit beim Lärm ist in Berlin also **kein stadtweites Muster, sondern ein räumlich konzentriertes Problem bestimmter innerstädtischer Quartiere**.

---

## 6.2 Die Hypothesen im Einzelnen

### H1 – „Benachteiligte Gebiete sind lauter“ → **nicht gestützt**

**Was die Daten zeigen:**

| Prüfung | Ergebnis | Bedeutung |
|---|---|---|
| Korrelation Index – Lärm | r = 0,06 | praktisch kein linearer Zusammenhang |
| Regression A1 (ohne Kontrollen) | +0,22 dB pro SD, p = 0,445 (korrigiert) | nicht signifikant, winziger Effekt |
| Regression A2 (mit Dichte und Lage) | +0,22 dB pro SD, p = 0,289 (korrigiert) | nicht signifikant |
| ANOVA über Quintile | p < 0,001 | Gruppen unterscheiden sich … |
| Mittelwerte der Quintile | Q1 55,8 · Q2 58,4 · Q3 57,7 · Q4 57,2 · Q5 57,4 dB | … aber nur Q1 ist anders |

**Wie passt „ANOVA signifikant“ mit „Regression nicht signifikant“ zusammen?**
Das ist kein Widerspruch, sondern genau die Erkenntnis:
- Die **Regression** sucht eine **gerade Linie** („je benachteiligter, desto lauter“). Die gibt es nicht.
- Die **ANOVA** sucht **irgendeinen** Unterschied zwischen den Gruppen. Den gibt es: Die wohlhabendsten 20 % (Q1) wohnen leiser.
- Zusammen heißt das: **Wohlhabende Gebiete sind etwas privilegiert, aber benachteiligte Gebiete sind nicht zusätzlich belastet.** Zwischen „durchschnittlich“ und „stark benachteiligt“ gibt es beim Lärm keinen Unterschied.

**Warum gibt es keinen linearen Zusammenhang?**
Die Karten zeigen den Grund: Es gibt **zwei Arten von benachteiligten Gebieten**:

| Typ | Beispiel | Lärm | Benachteiligungsindex |
|---|---|---:|---:|
| innerstädtisches Altbauquartier | Rollberg (Neukölln) | 59,7 dB | +2,03 |
| Großsiedlung am Stadtrand | Rollbergesiedlung (Reinickendorf) | 52,1 dB | +2,44 |

Beide Gebiete sind stark benachteiligt, liegen beim Lärm aber 7,7 dB auseinander. Die lauten Innenstadt-Gebiete und die leisen Stadtrand-Siedlungen heben sich im Durchschnitt gegenseitig auf. Deshalb ist die Gerade fast waagerecht.

**Wie groß ist der Effekt der Lage im Vergleich?**
Innenstadtgebiete sind bei gleicher Benachteiligung im Mittel **3,6 dB lauter** (p < 0,001). Der Effekt der Lage ist also rund **16-mal so groß** wie der (nicht signifikante) Effekt der Benachteiligung.

### H2 – „Lärm hängt mit den Mieten zusammen“ → **gestützt**

| Einfluss auf die Angebotsmiete | Effekt | p (korrigiert) |
|---|---:|---:|
| +1 dB Lärm | **+0,23 EUR/m²** | < 0,001 |
| +1 SD Benachteiligung | **−2,09 EUR/m²** | < 0,001 |
| Innere Stadt (statt Äußere) | **+4,02 EUR/m²** | < 0,001 |
| Modell erklärt | 53 % der Mietunterschiede | |

**Interpretation:**
- Auf den ersten Blick überraschend: **Lautere Gebiete sind teurer**, nicht billiger. Das heißt nicht, dass Menschen gern Lärm bezahlen. Lärm ist hier ein **Merkmal zentraler, begehrter Lagen** – dort, wo viel Verkehr ist, sind auch Arbeitsplätze, Kultur, Gastronomie, ÖPNV. Auch nach Berücksichtigung von „Innere Stadt“ bleibt ein Rest dieses Effekts, weil die grobe Unterscheidung innen/außen nicht alle Lagevorteile erfasst.
- **Benachteiligte Gebiete sind deutlich günstiger** – das ist der stärkste Effekt im Modell.
- **Keine Kausalität:** Wir können nicht sagen, dass Lärm die Miete erhöht oder dass niedrige Mieten Benachteiligung verursachen. Wir sehen nur, was zusammen auftritt.

### H3 – „Es gibt interpretierbare Gebietstypen“ → **gestützt**

| Cluster | Anteil | Beschreibung | Wo? |
|---|---:|---|---|
| C1 leise · benachteiligt · günstig | 20 % | Großsiedlungen am Stadtrand | Marzahn-Hellersdorf, Hohenschönhausen, Gropiusstadt |
| C2 leise · wohlhabend · mittlere Miete | 26 % | Einfamilienhausgebiete | Steglitz-Zehlendorf, Köpenick, Pankow-Nord |
| **C3 laut · benachteiligt · günstig** | **23 %** | **mehrfach belastete Innenstadtquartiere** | **Wedding, Nord-Neukölln, Schöneberg** |
| C4 laut · wohlhabend · teuer | 30 % | begehrte Innenstadtlagen | Charlottenburg, Mitte, Prenzlauer Berg |

**Interpretation:** Die vier Typen bilden fast ein „2 × 2“-Schema aus laut/leise und benachteiligt/wohlhabend. Für die Umweltgerechtigkeit ist **C3** entscheidend: 101 Gebiete, in denen soziale Benachteiligung und hohe Lärmbelastung zusammenkommen. Hier wäre Lärmschutz (z. B. Tempo 30, Lärmschutzfenster, Verkehrsberuhigung) sozialpolitisch besonders wirksam.

### Räumliche Struktur

| | Moran's I |
|---|---:|
| Lärm | 0,46 |
| Benachteiligung | 0,43 |
| Residuen A2 | 0,30 |

Lärm und Benachteiligung sind stark räumlich geclustert: Laute Gebiete liegen neben lauten, benachteiligte neben benachteiligten. Auch die Fehler der Regression sind gehäuft. Deshalb haben wir die Standardfehler nach Prognoseraum geclustert. Ergebnis: Die p-Werte werden größer (A1: 0,15 → 0,45), aber **keine Schlussfolgerung ändert sich**.

---

## 6.3 Was wir sagen dürfen – und was nicht

### ✅ Zulässige Aussagen
- „In Berlin gibt es auf Ebene der Planungsräume **keinen signifikanten linearen Zusammenhang** zwischen sozialer Benachteiligung und Verkehrslärm.“
- „Die am wenigsten benachteiligten Gebiete sind im Mittel etwa 2 dB leiser als der Rest.“
- „Die Lage (Innenstadt vs. Stadtrand) erklärt die Lärmunterschiede deutlich besser als die soziale Lage.“
- „Lautere Gebiete haben höhere, benachteiligte Gebiete niedrigere Angebotsmieten.“
- „Rund ein Viertel der untersuchten Gebiete ist zugleich laut und sozial benachteiligt; diese Gebiete konzentrieren sich in bestimmten Innenstadtquartieren.“
- „Lärm und soziale Lage sind räumlich stark geclustert; das haben wir in der Regression berücksichtigt.“

### ❌ Unzulässige Aussagen

| Falsche Aussage | Warum falsch? |
|---|---|
| „Arme Menschen sind in Berlin nicht von Lärm betroffen.“ | Wir haben Gebiete untersucht, keine Personen (ökologischer Fehlschluss). Innerhalb eines Gebiets können ärmere Haushalte trotzdem öfter an der lauten Straße wohnen. |
| „Es ist bewiesen, dass es keine Umweltungerechtigkeit gibt.“ | „Nicht signifikant“ heißt „kein Beleg gefunden“, nicht „Gegenteil bewiesen“. Außerdem zeigt Cluster C3, dass es mehrfach belastete Gebiete gibt. |
| „Lärm macht Wohnungen teurer.“ | Korrelation ist keine Kausalität. Wahrscheinlicher ist: Zentrale Lage macht Wohnungen teurer **und** lauter. |
| „Benachteiligung verursacht niedrige Mieten.“ | ebenfalls keine Kausalität; die Richtung kann auch umgekehrt sein (günstige Mieten ziehen einkommensschwache Haushalte an). |
| „In Wedding sind alle Bewohner arm und lärmbelastet.“ | Clusterwerte sind Durchschnitte über Gebiete. |
| „Die Ergebnisse gelten auch für andere Städte.“ | Berlin hat eine besondere Struktur (z. B. Großsiedlungen am Stadtrand). |

---

## 6.4 Grenzen der Untersuchung

| Grenze | Auswirkung | Wie gehen wir damit um? |
|---|---|---|
| **Querschnitt, ein Zeitpunkt** | keine Aussagen über Ursache und Wirkung | nur Zusammenhänge formulieren |
| **Unterschiedliche Jahre** (Lärm 2022, Sozialdaten 2024, Mieten 2025) | leichte zeitliche Unschärfe | Lärm und Sozialstruktur ändern sich langsam; offen benennen |
| **Gebietsebene** | keine Aussagen über Personen | immer „Gebiete mit …“ formulieren |
| **Fassadenpunkte nicht einwohnergewichtet** | ein Gebiet mit einer lauten Hauptstraße und vielen ruhigen Hinterhöfen kann laut erscheinen | zusätzlich Anteil Fassaden > 65 dB betrachtet (gleiches Muster) |
| **Angebotsmieten ≠ Bestandsmieten** | Mieten beschreiben den Markt, nicht die Belastung der Bewohner | offen benennen |
| **Mietfilter (≥ 21 Inserate)** | wohlhabende Einfamilienhausgebiete sind in Mietmodell und Clustering unterrepräsentiert | offen benennen |
| **Wittenau Mitte/Süd vertauscht** (IBB) | 2 von 434 Gebieten evtl. falsche Miete | vernachlässigbar, offen benennen |
| **Residuen auch mit Korrektur räumlich abhängig** | Modell erfasst nicht die ganze räumliche Struktur | geclusterte Standardfehler; räumliche Regressionsmodelle wären der nächste Schritt (außerhalb des Modulumfangs) |
| **ANOVA nicht räumlich korrigiert** | p-Wert eher zu optimistisch | bei p < 0,001 ändert das nichts an der Aussage |
| **Kontrollvariablen grob** („Innere Stadt“ nur 0/1) | Lageeffekte werden nur teilweise erfasst | offen benennen |

---

## 6.5 Typische Rückfragen in der Präsentation – und Antworten

**„Warum habt ihr eine PCA gemacht und nicht einfach die Arbeitslosenquote genommen?“**
Weil soziale Benachteiligung mehr ist als Arbeitslosigkeit. Die vier Indikatoren hängen stark zusammen; die PCA fasst sie objektiv zu einer Zahl zusammen, die 81 % ihrer Information enthält. Unser Index stimmt zu 99,8 % mit dem amtlichen Index des Senats überein.

**„Euer Ergebnis ist nicht signifikant – ist das Projekt dann gescheitert?“**
Nein. Ein nicht signifikantes Ergebnis ist ein Ergebnis. Es widerlegt die einfache Vorstellung „je ärmer, desto lauter“ für Berlin und zeigt stattdessen, dass die Belastung auf bestimmte Quartiere konzentriert ist. Das ist für die Stadtplanung sogar hilfreicher.

**„Warum ist die ANOVA signifikant, die Regression aber nicht?“**
Die Regression prüft einen geradlinigen Zusammenhang, die ANOVA beliebige Unterschiede zwischen Gruppen. Es gibt einen Unterschied (die wohlhabendsten Gebiete sind leiser), aber keinen durchgehenden Anstieg.

**„Habt ihr berücksichtigt, dass benachbarte Gebiete sich ähneln?“**
Ja. Moran's I zeigt eine deutliche räumliche Clusterung (I ≈ 0,46). Deshalb haben wir die Standardfehler nach den 58 Prognoseräumen geclustert. Die p-Werte werden dadurch größer, aber keine Aussage ändert sich.

**„Warum 4 Cluster?“**
Die Elbow-Kurve flacht ab k = 4 deutlich ab, und 4 Cluster ergeben eine klar interpretierbare Typologie (laut/leise × benachteiligt/wohlhabend). Mit 2 Clustern würde der Lärm gar keine Rolle spielen.

**„Warum ist laut teurer? Das ist doch unlogisch.“**
Lärm steht hier für zentrale Lage. Zentrale Gebiete sind begehrt (Arbeitsplätze, Kultur, ÖPNV) und gleichzeitig verkehrsreich. Das Modell zeigt einen Zusammenhang, keinen ursächlichen Effekt von Lärm auf die Miete.

**„Warum habt ihr Gebiete mit weniger als 21 Inseraten weggelassen?“**
Die IBB selbst kennzeichnet diese Werte als nicht repräsentativ. Ein Median aus 3 Inseraten ist Zufall. Wir haben die Werte nicht durch Schätzungen ersetzt, um keine künstlichen Daten zu erzeugen.

**„Woher wisst ihr, dass die Lärmdaten stimmen?“**
Es sind die offiziellen EU-Lärmkarten des Landes Berlin. Wir haben die Zusammenfassung pro Gebiet stichprobenartig gegen den offiziellen Webdienst nachgerechnet; die Werte stimmen exakt.

**„Was bedeutet 1 dB? Ist 0,22 dB viel?“**
Nein. Ein Unterschied unter 1 dB ist für Menschen nicht hörbar. +3 dB entsprechen einer Verdopplung des Verkehrs, +10 dB werden als doppelt so laut empfunden.

**„Was würdet ihr als Nächstes untersuchen?“**
1. Lärm nur an Wohngebäuden und nach Einwohnern gewichtet,
2. räumliche Regressionsmodelle,
3. Entwicklung über mehrere Jahre (MSS und Mieten gibt es seit 2012),
4. weitere Umweltfaktoren (Luftqualität, Grünflächen, Hitze).

---

## 6.6 Vorschlag für die Ergebnisfolie

**Titel:** Sind sozial benachteiligte Gebiete in Berlin stärker von Lärm betroffen?

**Grafik:** `outputs/ergebnis_leitfrage.png` (oder Feld A + `map_kmeans_cluster.png`)

**Drei Kernaussagen:**
1. **Kein linearer Zusammenhang:** Benachteiligte Gebiete sind im Mittel nicht lauter (p = 0,29). Nur die wohlhabendsten 20 % wohnen ca. 2 dB leiser.
2. **Die Lage entscheidet:** Innenstadt = laut und teuer (+3,6 dB, +4 EUR/m²).
3. **Konzentrierte Mehrfachbelastung:** 23 % der Gebiete sind laut und benachteiligt zugleich – vor allem Wedding, Nord-Neukölln, Schöneberg.

**Fußzeile:** Gebietsebene (542 Planungsräume), Querschnitt, keine Kausalaussagen; räumliche Abhängigkeit über geclusterte Standardfehler berücksichtigt.

---

## 6.7 Zuordnung zur Präsentationsaufteilung

| Präsentationsteil (siehe `praesentation.md`) | Relevante Doku | Relevante Outputs |
|---|---|---|
| Problemfrage und Motivation | [01_projekt.md](01_projekt.md) §1.1–1.3 | – |
| Daten sammeln und anpassen | [02_daten.md](02_daten.md) | `datenqualitaet.csv`, `pruefung_namensabweichungen_ibb.csv` |
| Algorithmen und Statistik | [03_methoden.md](03_methoden.md) | `pca_scree_ladungen.png`, `kmeans_elbow.png`, `regression_uebersicht.csv`, `morans_i.csv` |
| Output und Visualisierung | [05_outputs.md](05_outputs.md) | Karten, `histogramme.png`, `korrelationsmatrix.png` |
| Ergebnis / Auswertung | dieses Kapitel | `ergebnis_leitfrage.png`, `map_kmeans_cluster.png` |
