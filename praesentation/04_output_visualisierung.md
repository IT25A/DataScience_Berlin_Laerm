# Teil 4: Output und Visualisierung (Gabi, ca. 2,5 min)

## Folie 14 – Lärmkarte und Benachteiligungskarte

**Auf der Folie:** zwei Karten nebeneinander
- `map_laerm_gesamt_lden_db.png` – Lärm
- `map_benachteiligungsindex.png` – Benachteiligung

**Stichpunkte:**
- Lärm: klares **Zentrum-Rand-Gefälle** (Innenstadt laut, Rand leise)
- Benachteiligung: **zwei Schwerpunkte** – innenstadtnah (Wedding, Moabit, Nord-Neukölln) **und** Stadtrand (Marzahn, Spandau, Gropiusstadt)

**Sprechtext:**
„Links sieht man den Lärm: Je dunkler, desto lauter. Die Innenstadt ist deutlich lauter als der Stadtrand. Rechts die soziale Benachteiligung: Hier gibt es zwei Schwerpunkte – Quartiere nahe der Innenstadt wie Wedding, aber auch Großsiedlungen am Stadtrand wie Marzahn. Und genau das ist der Schlüssel zu unserem Ergebnis: Ein Teil der benachteiligten Gebiete liegt im lauten Zentrum, ein anderer am leisen Rand.“

---

## Folie 15 – Lärm nach Benachteiligungsgruppen

**Auf der Folie:** Feld A aus `ergebnis_leitfrage.png` (Boxplot)

| Quintil | Q1 (wohlhabend) | Q2 | Q3 | Q4 | Q5 (benachteiligt) |
|---|---:|---:|---:|---:|---:|
| Lärm (dB) | 55,3 | 58,8 | 57,7 | 57,4 | 57,3 |

- ANOVA: p < 0,001 – es gibt Unterschiede
- Aber: **nur Q1 ist leiser** (2,5 dB), Q2–Q5 fast gleich

**Sprechtext:**
„Jede Box zeigt die Lärmwerte einer Gruppe, die rote Linie die Mittelwerte. Die wohlhabendsten 20 Prozent sind etwa 2,5 dB leiser. Danach steigt der Lärm aber nicht weiter an – die am stärksten benachteiligten Gebiete sind nicht lauter als durchschnittliche. Es gibt also keine Treppe nach dem Motto ‚je ärmer, desto lauter‘.“

---

## Folie 16 – Regression als Streudiagramm

**Auf der Folie:** Feld C aus `ergebnis_leitfrage.png`
- Jeder Punkt = ein Planungsraum
- Gerade fast **waagerecht**: +0,3 dB pro Einheit Benachteiligung
- p = 0,32 bzw. 0,22 (mit Kontrollen) → nicht signifikant

**Sprechtext:**
„Hier sieht man alle Gebiete als Punkte. Die Punktwolke hat keine erkennbare Richtung, die Regressionsgerade ist fast flach. Der Effekt ist winzig – 0,3 dB hört kein Mensch – und statistisch nicht signifikant.“

---

## Folie 17 – Karte der Gebietstypen

**Auf der Folie:** `map_kmeans_cluster.png`

| Typ | Beschreibung | Wo? |
|---|---|---|
| C1 | leise · benachteiligt · günstig | Großsiedlungen am Stadtrand |
| C2 | leise · wohlhabend | Einfamilienhausgebiete |
| **C3** | **laut · benachteiligt · günstig** | **Wedding, Moabit, Schöneberg, Spandau-Mitte** |
| C4 | laut · wohlhabend · teuer | Innenstadt (Charlottenburg, Mitte, Prenzlauer Berg) |

**Sprechtext:**
„K-Means hat vier Gebietstypen gefunden, die sich fast wie ein Vier-Felder-Schema lesen: laut oder leise, benachteiligt oder wohlhabend. Für die Umweltgerechtigkeit ist der blaue Typ C3 entscheidend: Gebiete, die laut **und** benachteiligt sind. Sie liegen wie ein Ring um den teuren Innenstadtkern. Graue Flächen haben zu wenige Mietinserate und wurden nicht eingeteilt.“

**Übergang:** „Was das für unsere Leitfrage bedeutet, fasst Thanh zusammen.“
