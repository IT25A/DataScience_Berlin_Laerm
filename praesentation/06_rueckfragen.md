# Mögliche Rückfragen und kurze Antworten

| Frage | Antwort | Wer? |
|---|---|---|
| Warum Daten von 2022 und nicht die neuesten? | Die Lärmkarte erscheint nur alle 5 Jahre; die aktuellste ist von 2022. Damit alles zusammenpasst, haben wir Sozialdaten und Mieten aus demselben Jahr genommen. Mit neueren Daten (2024/2025) kommen dieselben Ergebnisse heraus. | Amir |
| Warum eine PCA statt nur Arbeitslosigkeit? | Benachteiligung ist mehr als ein Indikator. Die PCA fasst vier Indikatoren objektiv zusammen (81 % der Information) und stimmt zu 99,8 % mit dem amtlichen Index überein. | Anes |
| Ist ein nicht signifikantes Ergebnis nicht ein Misserfolg? | Nein. Es widerlegt die einfache Vermutung „je ärmer, desto lauter“ und zeigt, wo das Problem tatsächlich liegt (Cluster C3). | Thanh |
| Wie passt „ANOVA signifikant“ zu „Regression nicht signifikant“? | Die Regression sucht eine gerade Linie, die ANOVA irgendeinen Gruppenunterschied. Es gibt einen Unterschied (Q1 leiser), aber keinen durchgehenden Anstieg. | Anes |
| Habt ihr berücksichtigt, dass Nachbargebiete sich ähneln? | Ja, mit Moran's I gemessen (0,46) und durch nach Prognoseräumen gruppierte Standardfehler korrigiert. Ohne Korrektur wäre p = 0,068, mit Korrektur 0,318. | Anes |
| Warum 4 Cluster? | Die Elbow-Kurve flacht ab k = 4 ab, und vier Gruppen ergeben eine klar deutbare Typologie (laut/leise × benachteiligt/wohlhabend). | Anes |
| Warum ist laut teurer? | Lärm steht für zentrale Lage. Zentrale Gebiete sind begehrt und verkehrsreich. Das ist ein Zusammenhang, keine Ursache. | Thanh |
| Warum fehlen Mieten für viele Gebiete? | Die IBB hält Werte aus weniger als 21 Inseraten für nicht verlässlich. Wir haben sie nicht geschätzt, um keine künstlichen Daten zu erzeugen. | Amir |
| Stimmen die Lärmdaten? | Es sind die offiziellen EU-Lärmkarten. Wir haben unsere Zusammenfassung stichprobenartig gegen den offiziellen Webdienst nachgerechnet – exakt gleich. | Amir |
| Was bedeuten 0,27 dB? | Nichts Hörbares. Unter 1 dB hört man keinen Unterschied; +3 dB entsprechen doppelt so viel Verkehr, +10 dB werden als doppelt so laut empfunden. | Gabi |
| Gilt das für einzelne Menschen? | Nein, nur für Gebiete (ökologischer Fehlschluss). Innerhalb eines Gebiets können ärmere Haushalte trotzdem öfter an lauten Straßen wohnen. | Gabi |
| Was würdet ihr als Nächstes machen? | Lärm nach Einwohnern gewichten, Vergleich mit der Lärmkarte 2027, weitere Umweltfaktoren (Luft, Grün, Hitze). | Thanh |

Ausführlichere Antworten: `docs/06_ergebnis.md`, Abschnitt 6.5. Begriffe: `docs/07_glossar.md`.
