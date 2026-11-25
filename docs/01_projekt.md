# 1. Das Projekt: Worum geht es?

## 1.1 Die Idee in einfachen Worten

Lärm ist nicht nur lästig, sondern ein Gesundheitsrisiko: Dauerhafter Verkehrslärm erhöht nachweislich das Risiko für Schlafstörungen, Bluthochdruck und Herz-Kreislauf-Erkrankungen. Gleichzeitig vermutet man, dass **Menschen mit wenig Geld häufiger an lauten Orten wohnen** – etwa weil Wohnungen an Hauptstraßen günstiger sind und wohlhabendere Haushalte sich ruhigere Lagen leisten können.

Diesen Gedanken nennt man **Umweltgerechtigkeit** (englisch *Environmental Justice*): Sind Umweltbelastungen wie Lärm, Luftverschmutzung oder fehlendes Grün ungleich verteilt – und zwar zulasten sozial schwächerer Gruppen?

Unser Projekt prüft diese Vermutung für **Berlin** mit echten, offiziellen Daten.

## 1.2 Leitfrage

> **Sind Berliner Planungsräume mit einer ungünstigeren sozialen Lage stärker von Lärm betroffen, und wie hängen Lärm, soziale Lage und Angebotsmieten zusammen?**

Die Leitfrage hat zwei Teile:
1. **Kernfrage:** Gibt es einen Zusammenhang zwischen sozialer Benachteiligung und Lärm?
2. **Erweiterung:** Wie passen die Mieten ins Bild? Sind laute Gegenden billiger (weil unattraktiv) oder teurer (weil zentral)?

## 1.3 Hypothesen

Eine Hypothese ist eine überprüfbare Vermutung. Wir formulieren drei:

| Hypothese | Inhalt | Womit geprüft? |
|---|---|---|
| **H1 – Umweltgerechtigkeit** | Planungsräume mit stärkerer sozialer Benachteiligung haben höhere Lärmwerte. | ANOVA, Regression (Modelle A1, A2) |
| **H2 – Lärm und Mieten** | Lärm hängt mit den Angebotsmieten zusammen (die Richtung kann durch die Lage beeinflusst sein). | Regression (Modell B) |
| **H3 – Gebietstypen** | Die Planungsräume lassen sich anhand von Lärm, Benachteiligung und Miete in sinnvolle Gruppen einteilen. | K-Means-Clustering |

## 1.4 Was genau untersuchen wir? (Analyseeinheit)

Wir untersuchen **keine Personen**, sondern **Gebiete**. Berlin ist offiziell in sogenannte **LOR** („Lebensweltlich orientierte Räume“) eingeteilt, in mehreren Ebenen:

```text
Berlin
 └── 12 Bezirke                (z. B. Neukölln)
      └── 58 Prognoseräume     (z. B. Neukölln-Nord)
           └── 143 Bezirksregionen
                └── 542 Planungsräume   <- unsere Analyseebene (z. B. „Rollberg“)
```

Ein Planungsraum ist ungefähr so groß wie ein Kiez und hat im Durchschnitt rund 7.000 Einwohner. Für jeden der 542 Planungsräume haben wir:
- einen **Lärmwert** (wie laut ist es dort im Durchschnitt?),
- einen **Benachteiligungswert** (wie ist die soziale Lage?),
- einen **Mietwert** (wie teuer sind angebotene Wohnungen?).

**Wichtig – ökologischer Fehlschluss:** Weil wir Gebiete vergleichen, dürfen wir keine Aussagen über einzelne Menschen machen. Wenn ein benachteiligtes Gebiet laut ist, heißt das nicht, dass dort jede arme Person an einer lauten Straße wohnt. Wir sagen immer „Gebiete mit …“ und nie „Menschen mit …“.

## 1.5 Vorgehen im Überblick

```text
 1. Daten beschaffen        Lärmkarte 2022, MSS 2025, IBB-Mieten 2025, Gebietsgrenzen
          │
 2. Daten aufbereiten       Lärm pro Planungsraum zusammenfassen, alles über die PLR-ID verknüpfen
          │
 3. Index bilden (PCA)      4 soziale Indikatoren -> 1 Benachteiligungsindex
          │
 4. Beschreiben             Mittelwerte, Verteilungen, Korrelationen
          │
 5. Testen (ANOVA)          Unterscheidet sich der Lärm zwischen armen und reichen Gebieten?
          │
 6. Modellieren             Regression: Wie stark hängt Lärm von Benachteiligung ab? Und die Miete?
          │
 7. Gruppieren (K-Means)    Welche Gebietstypen gibt es?
          │
 8. Räumlich prüfen         Moran's I: Ähneln sich Nachbargebiete? -> Korrektur der Regression
          │
 9. Darstellen              Karten und Ergebnisgrafik
```

Jeder Schritt baut auf dem vorherigen auf. Die Verfahren sind in [03_methoden.md](03_methoden.md) ausführlich erklärt.

## 1.6 Warum gerade diese Methoden?

| Methode | Warum brauchen wir sie? |
|---|---|
| **Standardisierung** | Die Variablen haben unterschiedliche Einheiten (dB, %, EUR). Damit man sie vergleichen und kombinieren kann, bringt man sie auf eine gemeinsame Skala. |
| **PCA** | Es gibt vier soziale Indikatoren, die fast dasselbe messen. PCA fasst sie zu einem einzigen, sauberen Index zusammen. |
| **Deskriptive Statistik** | Bevor man testet, muss man die Daten kennen: Wertebereiche, Ausreißer, Verteilungen. |
| **ANOVA** | Prüft, ob sich der Lärm zwischen Gruppen unterschiedlich benachteiligter Gebiete unterscheidet – ohne vorauszusetzen, dass der Zusammenhang eine gerade Linie ist. |
| **Multiple Regression** | Schätzt den Effekt der Benachteiligung auf Lärm und gleichzeitig andere Einflüsse (Dichte, Innenstadtlage), damit man Effekte nicht verwechselt. |
| **K-Means** | Findet Gebietstypen, ohne dass wir die Gruppen vorher festlegen. |
| **Moran's I** | Gebiete liegen nebeneinander und beeinflussen sich. Moran's I misst das; ohne diese Prüfung wären die Ergebnisse der Regression zu optimistisch. |
| **Geclusterte Standardfehler** | Die Korrektur, die aus dem Moran-Ergebnis folgt. |

## 1.7 Grenzen des Projekts (vorab)

Es ist wichtig, diese Punkte offen zu benennen – das ist kein Fehler, sondern wissenschaftliche Ehrlichkeit:

1. **Querschnitt:** Wir betrachten einen Zeitpunkt, keine Entwicklung über die Zeit. Ursache und Wirkung können wir damit nicht beweisen.
2. **Unterschiedliche Jahre:** Lärm 2022, Sozialdaten Ende 2024, Mieten 2025.
3. **Gebietsebene:** Keine Aussagen über Einzelpersonen (siehe oben).
4. **Lärmmessung:** Die Lärmwerte stammen von Gebäudefassaden, nicht von Wohnungen; sie sind nicht nach Einwohnern gewichtet.
5. **Mieten:** Angebotsmieten aus Inseraten sind nicht dasselbe wie die Mieten, die Bewohner tatsächlich zahlen.
6. **Korrelation ist keine Kausalität:** Wenn zwei Dinge zusammen auftreten, heißt das nicht, dass das eine das andere verursacht.

## 1.8 Ergebnis in drei Sätzen (Vorschau)

1. **H1 wird nicht gestützt:** Es gibt keinen signifikanten linearen Zusammenhang zwischen sozialer Benachteiligung und Lärm. Nur die wohlhabendsten Gebiete sind etwas leiser (ca. 2 dB).
2. **H2 wird gestützt:** Lautere Gebiete sind teurer, benachteiligte Gebiete billiger – weil zentrale Lagen beides sind: laut und begehrt.
3. **H3 wird gestützt:** Es gibt vier klar unterscheidbare Gebietstypen; rund ein Viertel der Gebiete ist zugleich laut und benachteiligt – konzentriert in bestimmten innerstädtischen Quartieren wie Wedding und Nord-Neukölln.

Die vollständige Interpretation steht in [06_ergebnis.md](06_ergebnis.md).
