# Teil 5: Ergebnis und Auswertung (Thanh, ca. 2,5 min)

## Folie 18 – Antworten auf die Hypothesen

**Auf der Folie:**

| Hypothese | Ergebnis | Kernzahl |
|---|---|---|
| H1: Benachteiligte Gebiete sind lauter | ❌ nicht gestützt | +0,27 dB, p = 0,22 |
| H2: Lärm hängt mit Mieten zusammen | ✅ gestützt | +0,27 EUR/m² pro dB |
| H3: Es gibt Gebietstypen | ✅ gestützt | 26 % laut + benachteiligt |

**Sprechtext:**
„Zusammengefasst: H1 wird nicht gestützt – im Durchschnitt sind benachteiligte Gebiete nicht lauter. H2 wird gestützt, allerdings anders als erwartet. Und H3 wird gestützt: Es gibt vier klare Gebietstypen.“

---

## Folie 19 – Die Lage entscheidet

**Auf der Folie:**
- Innenstadt: **+3,6 dB lauter** und **+3,2 EUR/m² teurer**
- Laut ist **teurer**, nicht billiger: +0,27 EUR/m² pro dB
- Benachteiligt ist günstiger: −1,77 EUR/m²
- Grund: Zentrale Lagen sind laut **und** begehrt
- Korrelation ≠ Kausalität

**Sprechtext:**
„Den stärksten Einfluss auf den Lärm hat nicht die soziale Lage, sondern die Lage in der Stadt: Innenstadtgebiete sind 3,6 dB lauter – das ist dreizehnmal so viel wie der Effekt der Benachteiligung. Überraschend war H2: Lautere Gebiete sind teurer. Das heißt nicht, dass Menschen gern für Lärm zahlen, sondern dass zentrale Lagen beides sind: laut und beliebt. Wir zeigen Zusammenhänge, keine Ursachen.“

---

## Folie 20 – Fazit

**Auf der Folie:**
> Umweltungerechtigkeit beim Lärm ist in Berlin **kein stadtweites Muster**, sondern ein **räumlich konzentriertes Problem** bestimmter innenstadtnaher Quartiere.

- Ca. ein Viertel der Gebiete ist laut **und** benachteiligt (Wedding, Moabit, Schöneberg, Spandau-Mitte)
- Hier wäre Lärmschutz (Tempo 30, Schallschutzfenster) **sozial besonders zielgenau**
- Grafik: `ergebnis_leitfrage.png` (Gesamtüberblick)

**Sprechtext:**
„Unser Fazit: Die einfache Formel ‚arm gleich laut‘ gilt für Berlin nicht. Aber es gibt bestimmte Quartiere, in denen Armut und Lärm zusammenkommen – rund ein Viertel der untersuchten Gebiete. Genau dort würden Lärmschutzmaßnahmen am meisten für die Gerechtigkeit bringen.“

---

## Folie 21 – Grenzen und Ausblick

**Auf der Folie:**
- Gebietsebene, keine Aussagen über Personen
- Querschnitt 2022: keine Ursache-Wirkung
- Mieten nur für 341 Gebiete (wenige Inserate am Stadtrand)
- Ausblick: Lärmkarte 2027 vergleichen, Luftqualität und Grünflächen ergänzen

**Sprechtext:**
„Zum Schluss die Grenzen: Wir sprechen über Gebiete, nicht über Menschen, und wir haben nur einen Zeitpunkt betrachtet. Spannend wäre ein Vergleich mit der nächsten Lärmkarte 2027 und weitere Umweltfaktoren wie Luft und Grün. Vielen Dank – wir freuen uns auf Fragen.“

---

## Demo (nur wenn gefragt)

1. Terminal öffnen:
   ```bash
   cd berlin_laerm_sozialstruktur_starter
   source .venv/bin/activate
   python berlin_data_science.py
   ```
2. Während es läuft (ca. 1 Minute): erklären, dass die Schritte 1–9 nacheinander ausgegeben werden.
3. Am Ende `outputs/ergebnis_zusammenfassung.txt` öffnen – der Ergebnistext wird **automatisch aus den Zahlen erzeugt**.
4. Optional `outputs/map_kmeans_cluster.png` öffnen.

Vorher testen, dass `.venv` aktiviert ist und `data/processed/laermdaten_aggregiert.csv` existiert (sonst dauert `aggregate_noise.py` mehrere Minuten).
