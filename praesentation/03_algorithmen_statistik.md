# Teil 3: Algorithmen und Statistik (Anes, ca. 3,5 min)

## Folie 9 – Methodenüberblick

**Auf der Folie:**

```text
4 Sozialindikatoren ──PCA──► Benachteiligungsindex
                                   │
          ┌────────────────────────┼────────────────────┐
          ▼                        ▼                    ▼
       ANOVA                  Regression            K-Means
   (Gruppenvergleich)   (Stärke des Zusammenhangs) (Gebietstypen)
                                   │
                              Moran's I → räumliche Korrektur
```

**Sprechtext:**
„Wir haben fünf Methoden kombiniert. Jede beantwortet eine Teilfrage. Ich gehe sie kurz durch.“

---

## Folie 10 – PCA: aus 4 Indikatoren wird 1 Index

**Auf der Folie:**
- Die 4 Indikatoren hängen stark zusammen (r ≈ 0,95)
- **PCA** (Hauptkomponentenanalyse) fasst sie zu einer Zahl zusammen
- PC1 erklärt **81 %** der Information
- Kontrolle: stimmt zu **99,8 %** mit dem amtlichen Index überein
- Grafik: `pca_scree_ladungen.png`

**Sprechtext:**
„Wo viele Menschen arbeitslos sind, gibt es meist auch viel Kinderarmut – die vier Indikatoren messen im Grunde dasselbe. Die PCA sucht die Richtung, in der sich die Gebiete am stärksten unterscheiden, und fasst die vier Werte zu einem Benachteiligungsindex zusammen. Vorher werden alle Werte standardisiert, also auf Mittelwert 0 und Standardabweichung 1 gebracht, damit sie vergleichbar sind. Diese eine Zahl enthält 81 Prozent der Information. Und sie stimmt fast perfekt mit dem offiziellen Index des Senats überein.“

**Formel (kurz zeigen):** $z = \frac{x - \bar{x}}{s}$ → $\text{Index} = \sum_k v_k \cdot z_k$ (gewichtete Summe der z-Werte)

---

## Folie 11 – ANOVA und Regression

**Auf der Folie:**
- **ANOVA:** Gebiete in 5 Gruppen (Quintile) nach Benachteiligung → unterscheidet sich der mittlere Lärm?
- **Multiple Regression:** Wie viel dB mehr pro Einheit Benachteiligung?
  - Lärm = β₀ + β₁·Benachteiligung + β₂·Dichte + β₃·Innenstadt
- **Kontrollvariablen:** Dichte und Innenstadtlage herausrechnen
- **p-Wert < 0,05** → signifikant

**Sprechtext:**
„Für H1 nutzen wir zwei Verfahren. Die ANOVA teilt die Gebiete in fünf gleich große Gruppen, von wenig bis stark benachteiligt, und prüft, ob sich der Lärm zwischen den Gruppen unterscheidet. Die Regression legt eine Gerade durch die Daten und sagt, um wie viel Dezibel der Lärm steigt, wenn die Benachteiligung steigt. Dabei rechnen wir die Innenstadtlage und die Bevölkerungsdichte heraus – sonst könnten wir einen Lageeffekt fälschlich der Armut zuschreiben. Der p-Wert sagt, ob ein Ergebnis Zufall sein könnte: unter 0,05 nennen wir es signifikant.“

---

## Folie 12 – Räumliche Abhängigkeit: Moran's I

**Auf der Folie:**
- Nachbargebiete ähneln sich: laut neben laut
- **Moran's I** misst das: Lärm I = 0,46 (deutlich)
- Problem: klassische p-Werte werden zu optimistisch
- Lösung: Standardfehler nach **58 Prognoseräumen** gruppieren
- Beispiel: p = 0,068 → **0,318**

**Sprechtext:**
„Statistik geht normalerweise davon aus, dass alle Beobachtungen unabhängig sind. Bei Gebieten stimmt das nicht: Eine laute Hauptstraße geht durch mehrere Gebiete. Moran's I misst das – 0,46 ist eine deutliche räumliche Häufung. Deshalb korrigieren wir die Standardfehler, indem wir benachbarte Gebiete als Gruppe behandeln. Das ist wichtig: Ohne Korrektur läge unser einfaches Modell mit p = 0,068 knapp an der Grenze. Mit Korrektur ist p = 0,32 – also klar kein Effekt.“

---

## Folie 13 – K-Means: Gebietstypen finden

**Auf der Folie:**
- Gruppiert Gebiete automatisch nach **Lärm, Benachteiligung, Miete**
- Ablauf: Startpunkte → nächsten Mittelpunkt zuordnen → Mittelpunkte neu berechnen → wiederholen
- Anzahl Gruppen k = 4 (Elbow-Methode + Interpretierbarkeit)
- Grafik: `kmeans_elbow.png`

**Sprechtext:**
„Für H3 nutzen wir K-Means, ein Verfahren des unüberwachten Lernens. Es sucht selbst Gruppen von Gebieten, die sich in Lärm, sozialer Lage und Miete ähneln. Der Algorithmus setzt Mittelpunkte, ordnet jedes Gebiet dem nächsten zu, verschiebt die Mittelpunkte in die Mitte ihrer Gruppe und wiederholt das, bis sich nichts mehr ändert. Die Zahl der Gruppen haben wir mit der Elbow-Methode gewählt: Ab vier Gruppen bringt eine weitere kaum noch Verbesserung.“

**Übergang:** „Was dabei herauskommt, zeigt Gabi in den Grafiken.“
