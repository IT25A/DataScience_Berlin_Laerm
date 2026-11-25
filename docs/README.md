# Dokumentation: Lärm, soziale Lage und Mieten in Berlin

Diese Dokumentation erklärt unser Data-Science-Projekt so, dass man es **ohne Vorwissen** verstehen kann – weder über das Projekt noch über Statistik. Sie ist bewusst ausführlich. Wer nur einen schnellen Überblick will, liest Kapitel 1 und Kapitel 6.

## Lesereihenfolge

| Nr. | Datei | Worum geht es? | Für wen besonders wichtig? |
|---|---|---|---|
| 1 | [01_projekt.md](01_projekt.md) | Was wollen wir herausfinden und warum? Leitfrage, Hypothesen, Vorgehen | alle |
| 2 | [02_daten.md](02_daten.md) | Woher kommen die Daten, was steht drin, wie wurden sie aufbereitet? | Datenbeschaffung, Präsentation „Daten sammeln“ |
| 3 | [03_methoden.md](03_methoden.md) | Jedes statistische Verfahren einfach erklärt – mit Formeln und Beispielen | Präsentation „Algorithmen und Statistik“ |
| 4 | [04_code.md](04_code.md) | Jede Funktion im Python-Code: was sie tut, was rein- und rausgeht | wer den Code ausführt oder ändert |
| 5 | [05_outputs.md](05_outputs.md) | Jede Ausgabedatei: was sie zeigt und wie man sie liest | Präsentation „Output und Visualisierung“ |
| 6 | [06_ergebnis.md](06_ergebnis.md) | Was ist das Ergebnis? Was dürfen wir behaupten, was nicht? Typische Rückfragen | Präsentation „Ergebnis/Auswertung“ |
| 7 | [07_glossar.md](07_glossar.md) | Fachbegriffe, Methoden und Algorithmen mit Formeln und Beispielen | zum Nachschlagen und für die Präsentation |

## Die wichtigsten Begriffe in einem Satz

| Begriff | Bedeutung |
|---|---|
| **Planungsraum (PLR)** | Kleinste offizielle Gebietseinheit Berlins; die Stadt ist in 542 PLR aufgeteilt. Unsere „Beobachtungen“ sind diese 542 Gebiete. |
| **Prognoseraum** | Mittlere Gebietseinheit; 58 Prognoseräume, jeder fasst im Schnitt ca. 9 benachbarte PLR zusammen. |
| **dB(A)** | Dezibel, Maßeinheit für Lautstärke. Logarithmisch: +10 dB werden als etwa doppelt so laut empfunden. |
| **LDEN** | Lärmpegel über 24 Stunden, bei dem Abend- und Nachtlärm strenger gewichtet werden (EU-Standard). |
| **MSS** | „Monitoring Soziale Stadtentwicklung“ – offizieller Bericht des Landes Berlin über die soziale Lage aller PLR. |
| **Benachteiligungsindex** | Unsere eigene Kennzahl für soziale Benachteiligung, berechnet per PCA aus vier MSS-Indikatoren. 0 = Berliner Durchschnitt, höher = benachteiligter. |
| **PCA** | Hauptkomponentenanalyse: fasst mehrere stark zusammenhängende Variablen zu einer zusammen. |
| **Regression** | Verfahren, das schätzt, um wie viel sich eine Größe (z. B. Lärm) ändert, wenn sich eine andere (z. B. Benachteiligung) ändert. |
| **p-Wert** | Wie wahrscheinlich wäre ein mindestens so starkes Ergebnis, wenn es in Wahrheit gar keinen Zusammenhang gäbe? Unter 0,05 nennen wir ein Ergebnis „signifikant“. |
| **ANOVA** | Test, ob sich die Mittelwerte mehrerer Gruppen unterscheiden. |
| **K-Means** | Verfahren, das Gebiete automatisch in Gruppen (Cluster) ähnlicher Gebiete einteilt. |
| **Moran's I** | Kennzahl dafür, ob benachbarte Gebiete sich ähnlicher sind als zufällig zu erwarten. |
| **Geclusterte Standardfehler** | Korrektur der Regression dafür, dass benachbarte Gebiete nicht unabhängig voneinander sind. |

## Projektstruktur

```text
DataScience_Berlin_Laerm/
├── docs/                              <- diese Dokumentation
├── Plan.md                            <- Arbeitsplan, offene Punkte
├── Projekt_Recap.md                   <- kompakte Zusammenfassung aller Zahlen
└── berlin_laerm_sozialstruktur_starter/
    ├── aggregate_noise.py             <- Schritt 1: Lärmdaten laden und pro PLR zusammenfassen
    ├── berlin_data_science.py         <- Schritt 2: gesamte Analyse
    ├── requirements.txt               <- benötigte Python-Pakete
    ├── data/
    │   ├── raw/                       <- Originaldaten (Excel, GeoJSON)
    │   └── processed/                 <- aufbereitete Daten
    └── outputs/                       <- alle Ergebnisse (Tabellen, Grafiken, Karten)
```

## Ausführen in drei Schritten

```bash
cd berlin_laerm_sozialstruktur_starter
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python aggregate_noise.py        # nur nötig, wenn die Lärmdaten neu geladen werden sollen (mehrere Minuten)
python berlin_data_science.py    # ca. 1 Minute, schreibt alles nach outputs/
```

Hinweis zu den Branches:
- `beginner-code` (dieser Stand): gleiche Methoden und Ergebnisse wie `simplify-analysis`, aber der Python-Code ist für Einsteiger geschrieben (deutsche Namen, einfache Schleifen, viele Kommentare). Die Funktionsreferenz in [04_code.md](04_code.md) beschreibt diese Version.
- `simplify-analysis`: kompaktere Schreibweise des Codes, identische Ergebnisse.
- `fix/pca-mss-analysis`: ausführliche Version mit zusätzlichen Robustheitsprüfungen.
