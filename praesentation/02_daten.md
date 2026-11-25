# Teil 2: Daten sammeln und anpassen (Amir, ca. 2,5 min)

## Folie 5 – Unsere Datenquellen

**Auf der Folie:**

| Daten | Quelle | Stand |
|---|---|---|
| Lärm | Strategische Lärmkarte Berlin | 2022 |
| Soziale Lage | Monitoring Soziale Stadtentwicklung (MSS) | 31.12.2022 |
| Mieten | IBB Wohnungsmarktbericht | 2022 |
| Gebietsgrenzen | ODIS / Geoportal Berlin | 542 Planungsräume |

- Alles **offizielle, öffentliche Daten**
- Alles aus **demselben Jahr** (2022)

**Sprechtext:**
„Wir nutzen nur offizielle Daten des Landes Berlin und der Investitionsbank Berlin. Ganz wichtig war uns, dass alle Daten aus demselben Jahr stammen. Die Lärmkarte erscheint nur alle fünf Jahre, die aktuellste ist von 2022. Deshalb haben wir auch Sozialdaten und Mieten von 2022 genommen – sonst würden wir den Lärm von gestern mit den Mieten von heute vergleichen.“

---

## Folie 6 – Lärm: von 3,8 Millionen Punkten zu 542 Werten

**Auf der Folie:**
- Lärmkarte = berechneter Pegel an **3,8 Mio. Hausfassaden**
- Maß: **LDEN** = 24-Stunden-Lärm, Abend und Nacht strenger gewichtet
- Jeder Punkt wird seinem Planungsraum zugeordnet (räumlicher Join)
- Pro Gebiet: **energetischer Mittelwert** + Anteil Fassaden über 65 dB

**Sprechtext:**
„Die Lärmkarte gibt für jede Hausfassade einen Lärmwert an – insgesamt 3,8 Millionen Punkte. Wir haben jeden Punkt dem Planungsraum zugeordnet, in dem er liegt, und daraus einen Wert pro Gebiet berechnet. Weil Dezibel logarithmisch sind, darf man sie nicht einfach mitteln. Man rechnet sie erst in Schallenergie um, mittelt dann und rechnet zurück. Das nennt man energetischen Mittelwert.“

**Optional (Formel, nur wenn Zeit):**
$L = 10 \cdot \log_{10}\left(\frac{1}{n}\sum 10^{L_i/10}\right)$ — Beispiel: 50 dB und 70 dB ergeben nicht 60, sondern 67 dB.

---

## Folie 7 – Soziale Lage und Mieten

**Auf der Folie:**
- **4 Sozialindikatoren** (MSS): Arbeitslosigkeit, Kinder bei Alleinerziehenden, Transferbezug, Kinderarmut
- **Mieten:** Median-Angebotsmiete in EUR/m² (neu inserierte Wohnungen)
- Mieten nur bei **mind. 21 Inseraten** (IBB-Vorgabe) → 341 Gebiete

**Sprechtext:**
„Die soziale Lage messen wir mit vier Indikatoren des Senats, zum Beispiel Arbeitslosigkeit und Kinderarmut. Bei den Mieten nehmen wir den Median der Inserate. Die IBB sagt selbst, dass Werte aus weniger als 21 Inseraten nicht verlässlich sind – die haben wir weggelassen statt sie zu schätzen. Deshalb haben wir Mieten für 341 der 542 Gebiete.“

---

## Folie 8 – Aufbereitung und Qualitätskontrolle

**Auf der Folie:**
- Alle Tabellen über die **8-stellige Gebiets-ID** verknüpft
- Automatische Prüfung auf doppelte IDs
- Gefunden: 2 Gebietsnamen in der IBB-Tabelle **vertauscht** (Wittenau)
- Lärmwerte stichprobenartig **nachgerechnet** → stimmen exakt
- Keine erfundenen Ersatzwerte

**Sprechtext:**
„Alle Tabellen werden über eine eindeutige Gebietsnummer zusammengeführt. Das Skript prüft automatisch, dass jede Nummer nur einmal vorkommt. Dabei haben wir sogar einen Fehler in den offiziellen Mietdaten gefunden: Zwei Gebietsnamen sind vertauscht. Fehlende Werte haben wir nie durch geschätzte ersetzt, weil das die Ergebnisse verfälschen würde.“

**Übergang:** „Wie wir aus diesen Daten Aussagen gewinnen, erklärt Anes.“
