# 7. Glossar: alle Methoden und Algorithmen

Dieses Glossar erklärt jede Methode, jedes Verfahren und jeden Fachbegriff, der im Projekt vorkommt – mit Formel, Rechenweg und Bedeutung für unser Projekt. Die Begriffe sind thematisch gruppiert und innerhalb der Gruppen in der Reihenfolge, in der sie in der Analyse vorkommen. Ein alphabetischer Index steht am Ende.

Alle Beispielzahlen stammen aus unserer Analyse (Bezugsjahr 2022).

**Schreibweise:**
- $n$ = Anzahl der Beobachtungen (Planungsräume)
- $x_i$ = Wert des $i$-ten Planungsraums
- $\bar{x}$ = Mittelwert
- $\sum_{i=1}^{n}$ = Summe über alle Planungsräume
- $\hat{\ }$ (Dach) = geschätzter Wert, z. B. $\hat{\beta}$

---

## A. Grundlagen der Statistik

### Beobachtung, Variable, Datensatz
- **Beobachtung:** eine Zeile der Tabelle – bei uns ein Planungsraum (542 Stück).
- **Variable:** eine Spalte – eine Eigenschaft, die man misst, z. B. Lärm, Kinderarmut, Miete.
- **Datensatz:** alle Beobachtungen mit allen Variablen.

### Mittelwert (arithmetisches Mittel)
**Was es ist:** Der „Durchschnitt“ – die Summe aller Werte geteilt durch ihre Anzahl.

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

**Beispiel:** Drei Gebiete mit 55, 57 und 62 dB → (55 + 57 + 62) / 3 = 58 dB.
**Im Projekt:** mittlerer Lärm aller 542 Planungsräume = 57,3 dB.
**Schwäche:** reagiert stark auf Ausreißer (ein Gebiet mit 100 dB würde den Mittelwert stark anheben).

### Median
**Was es ist:** Der Wert in der Mitte, wenn man alle Werte der Größe nach sortiert. Die Hälfte liegt darunter, die Hälfte darüber.

**Rechenweg:** Werte sortieren. Bei ungerader Anzahl ist der Median der mittlere Wert, bei gerader Anzahl der Mittelwert der beiden mittleren.
**Beispiel:** 55, 57, 62, 90 → Median = (57 + 62) / 2 = 59,5 (der Mittelwert wäre 66 – durch den Ausreißer 90 verzerrt).
**Im Projekt:** Die IBB gibt Mieten als Median an, damit einzelne Luxuswohnungen das Bild nicht verfälschen.

### Quartile, Quintile, Quantile
- **Quantil:** ein Wert, unter dem ein bestimmter Anteil der Daten liegt.
- **Quartile** teilen die sortierten Daten in 4 gleich große Teile (25 %, 50 % = Median, 75 %).
- **Quintile** teilen in 5 gleich große Teile (je 20 %).

**Im Projekt:** Wir teilen die Planungsräume nach dem Benachteiligungsindex in Quintile Q1 (20 % am wenigsten benachteiligt) bis Q5 (20 % am stärksten benachteiligt), je 107–108 Gebiete. Python: `pd.qcut(daten["benachteiligungsindex"], 5)`.

### Varianz
**Was es ist:** Maß dafür, wie stark die Werte um den Mittelwert streuen – der durchschnittliche quadrierte Abstand zum Mittelwert.

$$
s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2
$$

**Warum quadriert?** Damit sich positive und negative Abweichungen nicht gegenseitig aufheben.
**Warum $n-1$?** Weil der Mittelwert selbst aus den Daten geschätzt wird; das $n-1$ korrigiert eine leichte Unterschätzung („Bessel-Korrektur“).
**Im Projekt:** Varianz des Lärms = 13,3 dB².

### Standardabweichung (SD)
**Was es ist:** Die Wurzel der Varianz. Sie hat dieselbe Einheit wie die Daten und ist deshalb leichter zu deuten.

$$
s = \sqrt{s^2}
$$

**Faustregel:** Bei glockenförmigen Daten liegen ca. 68 % der Werte im Bereich $\bar{x} \pm 1s$ und ca. 95 % im Bereich $\bar{x} \pm 2s$.
**Im Projekt:** Lärm: Mittelwert 57,3 dB, SD 3,6 dB → zwei Drittel der Gebiete liegen zwischen ca. 54 und 61 dB.

### Verteilung, Schiefe
- **Verteilung:** Wie häufig welche Werte vorkommen (sichtbar im Histogramm).
- **Symmetrisch:** Mittelwert ≈ Median (z. B. Lärm).
- **Rechtsschief:** viele kleine, wenige sehr große Werte; Mittelwert > Median (z. B. Kinderarmut, Einwohnerdichte).

### Histogramm
Balkendiagramm, das zeigt, wie viele Beobachtungen in bestimmte Wertebereiche („Klassen“) fallen. x-Achse = Werte, y-Achse = Anzahl. Die zusätzliche Kurve (**KDE**, Kerndichteschätzung) ist eine geglättete Version des Histogramms.

### Boxplot
Grafische Zusammenfassung einer Verteilung:
- **Box:** vom 1. Quartil (25 %) bis zum 3. Quartil (75 %) – hier liegen die mittleren 50 % der Werte.
- **Strich in der Box:** Median.
- **Whisker („Antennen“):** reichen bis zum letzten Wert innerhalb von 1,5 × Boxhöhe.
- **Punkte außerhalb:** Ausreißer.

**Im Projekt:** Feld A der Ergebnisgrafik zeigt den Lärm je Quintil als Boxplots.

### Ausreißer
Werte, die weit vom Rest entfernt liegen. Sie können echte Besonderheiten sein (z. B. Pankower Tor mit nur 17 Lärmpunkten und 100 % lauten Fassaden) oder Messfehler.

### Logarithmus
**Was es ist:** Die Umkehrung des Potenzierens: $\log_{10}(1000) = 3$, weil $10^3 = 1000$. Der **natürliche Logarithmus** $\ln$ hat die Basis $e \approx 2{,}718$.

**Wozu?**
1. **Dezibel** sind logarithmisch definiert (siehe Abschnitt B).
2. **Stauchen schiefer Daten:** Aus Einwohnerdichten zwischen 0 und 36.000 EW/km² wird mit $\ln(1+x)$ eine Skala von 0 bis ca. 10,5. Eine Verdopplung (1.000 → 2.000 oder 10.000 → 20.000) zählt dann jeweils gleich viel.

**Im Projekt:** `log_einwohnerdichte = ln(1 + Einwohnerdichte)`; das „+1“ verhindert $\ln(0)$, das nicht definiert ist.

### Dummy-Variable
Eine Variable, die nur 0 oder 1 sein kann und eine Ja/Nein-Eigenschaft kodiert.
**Im Projekt:** `innere_stadt` = 1, wenn der Planungsraum in der Inneren Stadt liegt, sonst 0. In der Regression ist ihr Koeffizient der Unterschied zwischen Innen- und Außenstadt.

---

## B. Lärm-Kennzahlen

### Dezibel, dB(A)
**Was es ist:** Maßeinheit für den Schallpegel. Sie ist **logarithmisch**:

$$
L = 10 \cdot \log_{10}\left(\frac{I}{I_0}\right)
$$

mit $I$ = Schallintensität (Energie) und $I_0$ = Hörschwelle.

**Konsequenzen:**
- +3 dB = doppelte Schallenergie (z. B. doppelt so viele Autos),
- +10 dB = zehnfache Energie, wird als **etwa doppelt so laut** empfunden,
- Unterschiede unter 1 dB sind nicht hörbar.

Das „(A)“ bedeutet A-Bewertung: Frequenzen werden so gewichtet, wie das menschliche Ohr sie wahrnimmt.

### LDEN (Day-Evening-Night-Level)
**Was es ist:** EU-Standard für den 24-Stunden-Lärmpegel. Abend und Nacht werden strenger gewichtet, weil Lärm dann stärker stört.

$$
L_{DEN} = 10 \cdot \log_{10}\left(\frac{1}{24}\left(12 \cdot 10^{\frac{L_{Tag}}{10}} + 4 \cdot 10^{\frac{L_{Abend}+5}{10}} + 8 \cdot 10^{\frac{L_{Nacht}+10}{10}}\right)\right)
$$

- Tag 6–18 Uhr (12 h), Abend 18–22 Uhr (4 h, +5 dB Zuschlag), Nacht 22–6 Uhr (8 h, +10 dB Zuschlag).

**Im Projekt:** Die Lärmkarte liefert LDEN für jeden Fassadenpunkt; wir übernehmen ihn.

### Fassadenpegel
Berechneter (nicht gemessener) Lärmpegel an einem Punkt vor einer Gebäudefassade. Berlin hat 3.799.746 solcher Punkte für die Lärmkarte 2022.

### Energetischer Mittelwert
**Problem:** Dezibel darf man nicht normal mitteln, weil sie logarithmisch sind.
**Lösung:** In Energie zurückrechnen, mitteln, wieder in dB umrechnen:

$$
L_{PLR} = 10 \cdot \log_{10}\left(\frac{1}{n}\sum_{i=1}^{n} 10^{L_i/10}\right)
$$

**Beispiel:** Fassaden mit 50 und 70 dB.
1. In Energie umrechnen: $10^{50/10} = 100.000$ und $10^{70/10} = 10.000.000$
2. Mitteln: $(100.000 + 10.000.000)/2 = 5.050.000$
3. Zurück in dB: $10 \cdot \log_{10}(5.050.000) = 67{,}0$ dB

(Der normale Mittelwert wäre 60 dB.)

**Eigenschaft:** Die lautesten Fassaden dominieren. **Im Projekt:** Hauptlärmwert `laerm_gesamt_lden_db` pro Planungsraum.

### Anteil Fassaden über 65 dB
**Formel:**

$$
\text{Anteil} = \frac{\text{Anzahl Fassadenpunkte mit } L > 65 \text{ dB}}{\text{Anzahl aller Fassadenpunkte}} \cdot 100\,\%
$$

**Bedeutung:** Wie viel Prozent der Fassaden im Gebiet stark belastet sind (65 dB = Schwellenwert der Lärmaktionsplanung). Anschaulicher als der energetische Mittelwert.

### Räumlicher Join (Punkt-in-Polygon)
Verfahren, um Punkte Flächen zuzuordnen: Für jeden Fassadenpunkt wird geprüft, in welchem Planungsraum-Polygon er liegt. Python: `gpd.sjoin(punkte, planungsraeume, predicate="within")`.

---

## C. Datenaufbereitung

### Join / Merge
Zusammenführen zweier Tabellen über eine gemeinsame Schlüsselspalte (bei uns die achtstellige Planungsraum-ID `plr_id`).
- **Left Join** (`how="left"`): Alle Zeilen der linken Tabelle bleiben erhalten; fehlt rechts ein Wert, wird er leer (NaN).
- **One-to-one-Prüfung** (`validate="one_to_one"`): Bricht ab, wenn eine ID doppelt vorkommt – verhindert unbemerkt verdoppelte Zeilen.

### Fehlender Wert (NaN)
„Not a Number“ – Platzhalter für einen fehlenden Wert. Wir ersetzen fehlende Werte **nicht** durch Schätzungen (keine Imputation), sondern lassen die betroffenen Gebiete in der jeweiligen Analyse weg.

### Mindestfallzahl
Regel, dass ein Wert nur verwendet wird, wenn er auf genügend Daten beruht. Die IBB gibt Mieten aus weniger als 21 Inseraten als nicht repräsentativ an → wir setzen sie auf NaN. Ergebnis 2022: 341 Gebiete mit Mietwert.

### Selektionseffekt (Stichprobenverzerrung)
Wenn das Weglassen von Fällen nicht zufällig ist, sondern bestimmte Gruppen betrifft. Bei uns fehlen im Mietmodell vor allem wohlhabende Einfamilienhausgebiete (wenige Inserate): 16 % aller Gebiete haben hohen Status, aber nur 10 % der Mietstichprobe.

### Ökologischer Fehlschluss
Der Fehler, von Eigenschaften eines Gebiets auf die einzelnen Menschen darin zu schließen. Beispiel: „Das Gebiet ist laut und arm“ heißt nicht, dass jede arme Person dort an einer lauten Straße wohnt.

### Querschnittsanalyse
Untersuchung zu **einem** Zeitpunkt (bei uns 2022). Sie zeigt Zusammenhänge, aber nicht, was Ursache und was Wirkung ist (dafür bräuchte man Längsschnittdaten über mehrere Zeitpunkte).

---

## D. Standardisierung und PCA

### Standardisierung (z-Transformation)
**Was es ist:** Umrechnung einer Variable auf Mittelwert 0 und Standardabweichung 1.

$$
z_i = \frac{x_i - \bar{x}}{s}
$$

**Bedeutung des z-Werts:** Wie viele Standardabweichungen liegt ein Wert über (+) oder unter (−) dem Durchschnitt?
**Beispiel:** Soldiner Straße, Arbeitslosigkeit 8,84 %; Mittel 4,34 %, SD 2,43 % → $z = (8{,}84 - 4{,}34)/2{,}43 = 1{,}86$.
**Wozu?** Damit Variablen mit unterschiedlichen Einheiten (dB, %, EUR) vergleichbar und kombinierbar werden. Vor PCA und K-Means notwendig.
**Python:** `StandardScaler().fit_transform(daten)`.

### Korrelationsmatrix
Tabelle aller paarweisen Korrelationen zwischen mehreren Variablen. Für standardisierte Daten $Z$ (n Zeilen, p Spalten):

$$
R = \frac{1}{n-1} Z^\top Z
$$

$Z^\top$ ist die transponierte Matrix (Zeilen und Spalten vertauscht). Die Diagonale ist immer 1.

### Eigenwert und Eigenvektor
**Was es ist:** Für eine quadratische Matrix $R$ ist $v$ ein Eigenvektor und $\lambda$ der zugehörige Eigenwert, wenn gilt:

$$
R\,v = \lambda\,v
$$

Das heißt: Multipliziert man die Matrix mit $v$, ändert sich nur die Länge von $v$ (um den Faktor $\lambda$), nicht die Richtung.

**Bedeutung in der PCA:**
- Eigenvektor = eine **Richtung** in den Daten (die Gewichte der Variablen),
- Eigenwert = wie viel **Varianz** in dieser Richtung liegt.

Bei 4 standardisierten Variablen gibt es 4 Eigenwerte, die sich zu 4 aufsummieren.

### Hauptkomponentenanalyse (PCA, Principal Component Analysis)
**Was sie macht:** Fasst mehrere stark korrelierte Variablen zu wenigen neuen Variablen (Hauptkomponenten) zusammen, ohne viel Information zu verlieren.

**Idee:** Die Punktwolke der Daten hat eine Richtung, in der sie am stärksten streut („Längsachse der Zigarre“). Diese Richtung ist die erste Hauptkomponente PC1. PC2 steht senkrecht darauf und erfasst die nächstgrößte Streuung usw.

**Algorithmus:**
1. Variablen standardisieren → Matrix $Z$
2. Korrelationsmatrix $R$ berechnen
3. Eigenwerte $\lambda_1 \geq \lambda_2 \geq \dots$ und Eigenvektoren $v_1, v_2, \dots$ von $R$ bestimmen
4. Scores berechnen: $\text{PC}_k = Z \cdot v_k$, d. h. für Gebiet $i$: $\text{PC1}_i = \sum_j v_{1j} \cdot z_{ij}$
5. Erklärte Varianz: $\lambda_k / \sum_j \lambda_j$

**Im Projekt:** 4 Indikatoren (S1 Arbeitslosigkeit, S2 Alleinerziehende, S3 Transferbezug, S4 Kinderarmut) → PC1 erklärt **81,2 %** → PC1 ist unser **Benachteiligungsindex**.
**Python:** `PCA().fit_transform(z_werte)`.

### Erklärte Varianz
Anteil der Gesamtstreuung, der von einer Hauptkomponente erfasst wird:

$$
\text{Anteil}_k = \frac{\lambda_k}{\sum_j \lambda_j}
$$

Bei uns: PC1 = 3,254 / 4 = 81,2 %; PC2 = 16,5 %; PC3 = 1,6 %; PC4 = 0,7 %.

### Ladung (Loading)
Korrelation zwischen einer Originalvariable und einer Hauptkomponente:

$$
\text{Ladung}_{jk} = v_{kj} \cdot \sqrt{\lambda_k}
$$

**Bei uns (PC1):** Kinderarmut 0,97, Arbeitslosigkeit 0,97, Transferbezug 0,97, Alleinerziehende 0,66. Alle positiv und hoch → PC1 misst „allgemeine soziale Benachteiligung“.

### Scree-Plot
Balkendiagramm der Eigenwerte bzw. erklärten Varianzen. Ein hoher erster Balken und ein steiler Abfall danach („Geröllhalde“) zeigt, dass eine Komponente ausreicht.

### Benachteiligungsindex
Unsere zentrale Sozialvariable: PC1, nochmals standardisiert (Mittelwert 0, SD 1), Vorzeichen so gewählt, dass höhere Werte mehr Benachteiligung bedeuten.

$$
\text{Index}_i = \frac{\text{PC1}_i - \overline{\text{PC1}}}{s_{\text{PC1}}}
$$

**Lesart:** 0 = Berliner Durchschnitt; +1 = eine Standardabweichung benachteiligter; −1 = eine SD weniger benachteiligt.
**Validierung:** Korrelation mit dem amtlichen MSS-Status-Index r = 0,998.

---

## E. Zusammenhänge messen

### Kovarianz
Maß dafür, ob zwei Variablen gemeinsam steigen und fallen:

$$
\text{Kov}(x, y) = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})
$$

Positiv = gleiche Richtung, negativ = entgegengesetzt. Nachteil: hängt von den Einheiten ab.

### Korrelationskoeffizient nach Pearson (r)
Standardisierte Kovarianz, immer zwischen −1 und +1:

$$
r = \frac{\text{Kov}(x, y)}{s_x \cdot s_y} = \frac{\sum_i (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_i (x_i - \bar{x})^2}\,\sqrt{\sum_i (y_i - \bar{y})^2}}
$$

| r | Deutung |
|---|---|
| ±1 | perfekter linearer Zusammenhang |
| > 0,5 | stark |
| 0,3–0,5 | mittel |
| 0,1–0,3 | schwach |
| < 0,1 | kein linearer Zusammenhang |

**Im Projekt:** Miete–Lärm r = 0,42; Benachteiligung–Miete r = −0,51; Benachteiligung–Lärm r = 0,08.
**Wichtig:** r misst nur **lineare** Zusammenhänge und sagt nichts über Ursache und Wirkung.

### Rangkorrelation nach Spearman (ρ)
Spearman misst, ob zwei Variablen in ähnlicher **Rangfolge** steigen oder fallen. Zuerst werden die Werte in Rangplätze umgewandelt; danach berechnet man darauf die Pearson-Korrelation:

$$
\rho = \operatorname{corr}(\operatorname{Rang}(x), \operatorname{Rang}(y))
$$

Ohne gleiche Rangplätze lässt sie sich auch so schreiben:

$$
\rho = 1 - \frac{6\sum_{i=1}^{n} d_i^2}{n(n^2-1)}
$$

$d_i$ ist die Differenz der beiden Rangplätze für Beobachtung $i$. Bei gleichen Werten (Bindungen) werden mittlere Ränge vergeben; die Software berechnet die Korrelation der Rangplätze direkt.

**Unterschied zu Pearson:** Pearson misst einen linearen Zusammenhang der Zahlenwerte; Spearman erfasst, ob die Reihenfolge ähnlich bleibt, auch wenn der Zusammenhang nicht exakt geradlinig ist. Beide Werte liegen zwischen −1 und +1.
**Im Projekt:** Für den Vergleich der Mietdaten 2022 und 2025 beträgt Pearson-r 0,823 und Spearman-ρ 0,835. Die Rangfolge der Mieten in den Gebieten blieb damit ähnlich. Berechnet wird nur für Planungsräume mit gültigen Mietwerten in beiden Jahren.

### Korrelation vs. Kausalität
**Korrelation:** Zwei Dinge treten gemeinsam auf. **Kausalität:** Das eine verursacht das andere. Aus Querschnittsdaten folgt nur Korrelation. Beispiel: Laute Gebiete sind teurer – nicht, weil Lärm die Miete erhöht, sondern weil zentrale Lage beides bewirkt (**Störvariable**, „Confounder“).

### Störvariable (Confounder)
Eine dritte Variable, die zwei andere gleichzeitig beeinflusst und so einen Scheinzusammenhang erzeugt. Bei uns: die Innenstadtlage. Gegenmittel: als Kontrollvariable in die Regression aufnehmen.

---

## F. Hypothesentests

### Hypothese, Nullhypothese, Alternativhypothese
- **Hypothese:** überprüfbare Vermutung (z. B. H1: „Benachteiligte Gebiete sind lauter“).
- **Nullhypothese $H_0$:** „Es gibt keinen Effekt / keinen Unterschied.“
- **Alternativhypothese $H_1$:** „Es gibt einen Effekt.“

Ein Test prüft, ob die Daten stark genug gegen $H_0$ sprechen.

### Teststatistik
Eine aus den Daten berechnete Zahl, die zusammenfasst, wie stark die Daten von $H_0$ abweichen (z. B. F-Wert, z-Wert).

### p-Wert
**Definition:** Die Wahrscheinlichkeit, ein mindestens so extremes Ergebnis zu beobachten, **falls $H_0$ wahr ist**.

- Kleiner p-Wert → das Ergebnis wäre unter $H_0$ sehr unwahrscheinlich → Indiz gegen $H_0$.
- Großer p-Wert → das Ergebnis ist mit $H_0$ gut vereinbar.

**Häufige Fehldeutungen:**
- p ist **nicht** die Wahrscheinlichkeit, dass $H_0$ stimmt.
- „Nicht signifikant“ heißt **nicht** „kein Effekt bewiesen“.
- „Signifikant“ heißt **nicht** „groß“ oder „wichtig“.

### Signifikanzniveau (α)
Vorher festgelegte Grenze, meist α = 0,05. Ist p < α, nennt man das Ergebnis **signifikant** und verwirft $H_0$.

### Fehler 1. und 2. Art
- **Fehler 1. Art:** $H_0$ verwerfen, obwohl sie stimmt („falscher Alarm“). Wahrscheinlichkeit = α.
- **Fehler 2. Art:** $H_0$ beibehalten, obwohl ein Effekt existiert („übersehener Effekt“).

### Freiheitsgrade (df)
Anzahl der Werte, die frei variieren können, nachdem bestimmte Größen (z. B. Mittelwerte) aus den Daten geschätzt wurden. Sie bestimmen die Form der Verteilung, mit der der p-Wert berechnet wird. Bei der ANOVA: $k-1$ und $N-k$ (bei uns 4 und 531).

### Varianzanalyse (ANOVA)
**Was sie macht:** Prüft, ob sich die **Mittelwerte mehrerer Gruppen** unterscheiden.

**Hypothesen:** $H_0$: alle Gruppenmittelwerte gleich. $H_1$: mindestens einer verschieden.

**Formeln:**

$$
SS_{zwischen} = \sum_{g=1}^{k} n_g (\bar{x}_g - \bar{x})^2
\qquad
SS_{innerhalb} = \sum_{g=1}^{k} \sum_{i \in g} (x_i - \bar{x}_g)^2
$$

$$
F = \frac{SS_{zwischen} / (k-1)}{SS_{innerhalb} / (N-k)}
$$

- $SS$ = „Sum of Squares“ (Quadratsumme),
- $k$ = Anzahl der Gruppen, $N$ = Gesamtzahl, $n_g$ = Größe der Gruppe $g$, $\bar{x}_g$ = Gruppenmittelwert.

**Idee:** Ist die Streuung **zwischen** den Gruppen groß im Verhältnis zur Streuung **innerhalb** der Gruppen, ist F groß und p klein.

**Voraussetzungen:** unabhängige Beobachtungen, ungefähr normalverteilte Werte, ähnliche Streuung in den Gruppen.

**Im Projekt:** Lärm nach Quintilen: F = 14,27, p < 0,001. Mittelwerte Q1–Q5: 55,3 · 58,8 · 57,7 · 57,4 · 57,3 dB → nur Q1 (wohlhabendste Gebiete) ist leiser.
**Python:** `stats.f_oneway(gruppe1, gruppe2, ...)`.

---

## G. Regression

### Lineare Regression (einfach)
**Was sie macht:** Legt eine Gerade durch die Punktwolke, die beschreibt, wie sich $y$ im Mittel ändert, wenn $x$ steigt.

$$
y_i = \beta_0 + \beta_1 x_i + \varepsilon_i
$$

- $\beta_0$ = Achsenabschnitt (Wert von $y$ bei $x = 0$)
- $\beta_1$ = Steigung (Änderung von $y$ pro Einheit $x$)
- $\varepsilon_i$ = Fehler/Residuum

Schätzung bei einer Einflussvariable:

$$
\hat{\beta}_1 = \frac{\text{Kov}(x, y)}{\text{Var}(x)}, \qquad \hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}
$$

### Multiple lineare Regression
Wie oben, aber mit mehreren Einflussvariablen gleichzeitig:

$$
y_i = \beta_0 + \beta_1 x_{1i} + \beta_2 x_{2i} + \dots + \beta_k x_{ki} + \varepsilon_i
$$

$\beta_j$ = Änderung von $y$, wenn $x_j$ um 1 steigt **und alle anderen $x$ gleich bleiben** („unter Kontrolle der anderen Variablen“).

In Matrixschreibweise: $y = X\beta + \varepsilon$, wobei $X$ eine Spalte mit Einsen (für $\beta_0$) und eine Spalte pro Einflussvariable enthält.

**Im Projekt:**
- A1: Lärm = β₀ + β₁·Benachteiligung
- A2: Lärm = β₀ + β₁·Benachteiligung + β₂·log(Dichte) + β₃·Innere Stadt
- B: Miete = β₀ + β₁·Lärm + β₂·Benachteiligung + β₃·log(Dichte) + β₄·Innere Stadt

### Methode der kleinsten Quadrate (OLS)
**Was sie macht:** Wählt die Koeffizienten so, dass die Summe der quadrierten Abstände zwischen den Datenpunkten und der Regressionsgeraden minimal wird:

$$
\min_{\beta} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$

Lösung (Normalgleichung):

$$
\hat{\beta} = (X^\top X)^{-1} X^\top y
$$

$(X^\top X)^{-1}$ ist die inverse Matrix. **Python:** `sm.OLS(y, sm.add_constant(X)).fit()`.

### Vorhergesagter Wert und Residuum
- **Vorhersage:** $\hat{y}_i = \hat{\beta}_0 + \hat{\beta}_1 x_{1i} + \dots$
- **Residuum:** $\hat{\varepsilon}_i = y_i - \hat{y}_i$ = tatsächlicher minus vorhergesagter Wert. Positiv: das Gebiet ist lauter als das Modell erwartet.

### Kontrollvariable
Eine Variable, die ins Modell aufgenommen wird, um ihren Einfluss herauszurechnen. Bei uns: Einwohnerdichte und Innere Stadt. Beispiel: In A2 ist Innere Stadt +3,58 dB – Innenstadtgebiete sind bei gleicher Benachteiligung und Dichte 3,6 dB lauter.

### Bestimmtheitsmaß (R²)
Anteil der Streuung von $y$, die das Modell erklärt:

$$
R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}
$$

0 = erklärt nichts, 1 = erklärt alles. **Bei uns:** A1 0,006 (0,6 %), A2 0,225, B 0,512.
**Adjustiertes R²:** bestraft zusätzliche Variablen leicht, damit man Modelle mit unterschiedlich vielen Variablen vergleichen kann.

### Standardfehler eines Koeffizienten (klassisch)
Wie genau ist ein Koeffizient geschätzt? Klassisch (unter der Annahme unabhängiger Fehler mit gleicher Streuung):

$$
\widehat{\text{Var}}(\hat{\beta}) = \hat{\sigma}^2 (X^\top X)^{-1}, \qquad \hat{\sigma}^2 = \frac{1}{n-k-1}\sum_i \hat{\varepsilon}_i^2
$$

Der Standardfehler ist die Wurzel des passenden Diagonalelements.

### t-/z-Test eines Koeffizienten
Prüft $H_0: \beta_j = 0$:

$$
z = \frac{\hat{\beta}_j}{SE(\hat{\beta}_j)}
$$

Ab $|z| > 1{,}96$ ist p < 0,05 (zweiseitig). Bei klassischen OLS-Fehlern nutzt statsmodels die t-Verteilung, bei geclusterten Fehlern die Normalverteilung (z).

### Konfidenzintervall (95 %)
Bereich, in dem der wahre Koeffizient mit 95 % Sicherheit liegt:

$$
\hat{\beta}_j \pm 1{,}96 \cdot SE(\hat{\beta}_j)
$$

**Enthält das Intervall die 0, ist der Effekt nicht signifikant.** Bei uns (A2, Benachteiligung): [−0,155; 0,690] → enthält 0 → nicht signifikant.

### F-Test des Gesamtmodells
Prüft, ob das Modell **insgesamt** mehr erklärt als ein Modell ohne Einflussvariablen. In A2: p = 3,6·10⁻⁹ – signifikant wegen „Innere Stadt“.

---

## H. Räumliche Statistik

### Räumliche Autokorrelation
Benachbarte Gebiete haben ähnlichere Werte als weit entfernte („Tobler's erstes Gesetz der Geographie“: Alles hängt mit allem zusammen, aber Nahes mehr als Fernes). Problem für klassische Statistik, die unabhängige Beobachtungen annimmt.

### Räumliche Gewichtsmatrix (W)
Tabelle, die festlegt, wer Nachbar von wem ist: $w_{ij} = 1$, wenn Gebiet $i$ und $j$ Nachbarn sind, sonst 0.

### Queen-Nachbarschaft
Nachbarn sind Gebiete mit gemeinsamer Grenze **oder** gemeinsamem Eckpunkt (wie die Dame im Schach, die in alle Richtungen ziehen kann). Alternative: Rook (nur gemeinsame Grenzen). **Python:** `Queen.from_dataframe(gebiete)`.

### Zeilenstandardisierung
Jede Zeile von $W$ wird durch die Anzahl der Nachbarn geteilt, sodass $\sum_j w_{ij} = 1$. Dann ist $\sum_j w_{ij} x_j$ der **Durchschnitt der Nachbarn** (räumlicher Lag).

### Moran's I
**Was es misst:** Wie stark der Wert eines Gebiets mit den Werten seiner Nachbarn zusammenhängt.

$$
I = \frac{n}{\sum_i \sum_j w_{ij}} \cdot \frac{\sum_i \sum_j w_{ij}(x_i - \bar{x})(x_j - \bar{x})}{\sum_i (x_i - \bar{x})^2}
$$

Mit zeilenstandardisierten Gewichten und $z_i = x_i - \bar{x}$:

$$
I = \frac{\sum_i z_i \cdot \left(\sum_j w_{ij} z_j\right)}{\sum_i z_i^2}
$$

| I | Bedeutung |
|---|---|
| > 0 | Ähnliches liegt nebeneinander (Clusterung) |
| ≈ 0 (genau $-1/(n-1)$) | zufällige Verteilung |
| < 0 | Gegensätze liegen nebeneinander (Schachbrett) |

**Im Projekt:** Lärm I = 0,46; Benachteiligung 0,43; Residuen A2 0,31 – alle deutlich geclustert.
**Python:** `Moran(werte, nachbarn, permutations=999)`.

### Permutationstest (für Moran's I)
**Was er macht:** Prüft, ob ein beobachtetes I größer ist als durch Zufall erwartet.
**Ablauf:**
1. I für die echten Daten berechnen,
2. die Werte 999-mal zufällig auf die Gebiete verteilen (Geometrie bleibt gleich) und jedes Mal I berechnen,
3. zählen, wie oft das Zufalls-I mindestens so groß war:

$$
p_{sim} = \frac{\#\{I_{perm} \geq I_{beob}\} + 1}{999 + 1}
$$

Kleinstmöglicher Wert: 0,001 („keine einzige Zufallsmischung war so extrem“). Ein fester Zufallsstartwert (`np.random.seed(42)`) macht das Ergebnis reproduzierbar.

### Geclusterte Standardfehler (Cluster-robuste Standardfehler)
**Problem:** Wenn Residuen räumlich gehäuft sind, sind die Beobachtungen nicht unabhängig. Klassische Standardfehler werden zu klein, p-Werte zu optimistisch.

**Lösung:** Gebiete werden zu Gruppen (Clustern) zusammengefasst – bei uns die **58 Prognoseräume**. Innerhalb eines Clusters dürfen die Fehler beliebig zusammenhängen.

**Formel („Sandwich-Schätzer“):**

$$
\widehat{\text{Var}}_{cluster}(\hat{\beta}) = c \cdot (X^\top X)^{-1} \left( \sum_{g=1}^{G} X_g^\top \hat{\varepsilon}_g \hat{\varepsilon}_g^\top X_g \right) (X^\top X)^{-1}
$$

- $G$ = Anzahl Cluster (58), $X_g$ und $\hat{\varepsilon}_g$ = Daten und Residuen im Cluster $g$,
- $c = \frac{G}{G-1}\cdot\frac{N-1}{N-K}$ = Korrektur für kleine Stichproben.

**Anschaulich:** Die Residuen werden erst innerhalb jedes Prognoseraums aufsummiert. Zeigen sie alle in dieselbe Richtung, addieren sie sich → größere Unsicherheit.

**Wichtig:** Die Koeffizienten bleiben **gleich**; nur Standardfehler und p-Werte ändern sich.
**Im Projekt:** A1: SE 0,156 → 0,285; p 0,068 → 0,318. Ohne Korrektur läge A1 fast an der Signifikanzgrenze; mit Korrektur bleibt davon nichts.
**Python:** `sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": prognoseraum_nummer})`.

---

## I. Clustering

### Clustering / Clusteranalyse
Verfahren, das Beobachtungen automatisch in Gruppen ähnlicher Beobachtungen einteilt. **Unüberwachtes Lernen:** Es gibt keine vorgegebenen „richtigen“ Gruppen.

### Euklidischer Abstand
Die „Luftlinie“ zwischen zwei Punkten in einem Raum mit mehreren Merkmalen:

$$
d(a, b) = \sqrt{\sum_{m=1}^{M} (a_m - b_m)^2}
$$

**Beispiel (standardisiert, 3 Merkmale):** Gebiet a = (1, 0, −1), Zentroid b = (0, 1, 0) → $d = \sqrt{1 + 1 + 1} = 1{,}73$.

### Zentroid
Mittelpunkt eines Clusters = Mittelwert aller zugehörigen Beobachtungen in jedem Merkmal.

### K-Means
**Was es macht:** Teilt die Daten in $k$ Cluster, sodass die Summe der quadrierten Abstände jedes Punktes zu seinem Zentroid minimal ist.

**Zielfunktion (Inertia):**

$$
\text{Inertia} = \sum_{c=1}^{k} \sum_{i \in C_c} \lVert x_i - \mu_c \rVert^2
$$

**Algorithmus (Lloyd):**
1. **Initialisieren:** $k$ Startzentroide wählen (bei scikit-learn mit „k-means++“, das gut verteilte Startpunkte wählt).
2. **Zuordnen:** Jeden Punkt dem nächstgelegenen Zentroid zuordnen (euklidischer Abstand).
3. **Aktualisieren:** Jeden Zentroid als Mittelwert seiner Punkte neu berechnen.
4. **Wiederholen** von 2 und 3, bis sich die Zuordnung nicht mehr ändert.

Weil das Ergebnis vom Start abhängen kann, wird der Algorithmus 20-mal gestartet (`n_init=20`) und das Ergebnis mit der kleinsten Inertia genommen. `random_state=42` macht ihn reproduzierbar.

**Voraussetzung:** Merkmale standardisieren, sonst dominiert das Merkmal mit der größten Skala.

**Im Projekt:** Merkmale Lärm, Benachteiligungsindex, Miete; 341 Gebiete; k = 4 → C1 leise/benachteiligt/günstig (74), C2 leise/wohlhabend (90), **C3 laut/benachteiligt/günstig (88)**, C4 laut/wohlhabend/teuer (89).
**Python:** `KMeans(n_clusters=4, random_state=42, n_init=20).fit_predict(z_werte)`.

### Elbow-Methode
**Was sie macht:** Hilft, die Clusterzahl $k$ zu wählen. Man berechnet K-Means für k = 1, 2, 3, … und zeichnet die Inertia. Mehr Cluster senken die Inertia immer; man sucht den „Ellenbogen“, ab dem weitere Cluster kaum noch etwas bringen.
**Im Projekt:** Inertia 1023 → 629 → 480 → 387 → 332 → … Die Kurve flacht ab k = 4 ab; zusammen mit der Interpretierbarkeit → k = 4.

### Clusterprofil
Mittelwerte jedes Merkmals pro Cluster. Bei uns wird jedes Merkmal als „hoch“ (> +0,25 SD), „niedrig“ (< −0,25 SD) oder „mittel“ bezeichnet, woraus die Clusternamen entstehen.

---

## J. Visualisierung

### Choroplethenkarte
Karte, in der Flächen (hier Planungsräume) nach dem Wert einer Variable eingefärbt sind. Die Farbskala (Legende) zeigt, welche Farbe welchem Wert entspricht.

### Heatmap
Farbige Tabelle, in der jede Zelle nach ihrem Wert eingefärbt ist; bei uns für die Korrelationsmatrix (rot = positiv, blau = negativ).

### Streudiagramm (Scatterplot)
Jeder Punkt ist eine Beobachtung, x- und y-Achse sind zwei Variablen. Mit Regressionsgerade zeigt es den linearen Zusammenhang (Feld C der Ergebnisgrafik).

---

## K. Software-Begriffe

| Begriff | Bedeutung |
|---|---|
| **DataFrame** | Tabelle in pandas (Zeilen = Beobachtungen, Spalten = Variablen) |
| **GeoDataFrame** | DataFrame mit Geometrie-Spalte (geopandas) |
| **CRS / EPSG:25833** | Koordinatensystem; 25833 = UTM-Zone 33N in Metern |
| **GeoJSON / GeoPackage** | Dateiformate für Geodaten |
| **WFS** | Web Feature Service: Internetschnittstelle für Geodaten (hier: Lärmkarte) |
| **random_state / seed** | fester Startwert für Zufallszahlen → reproduzierbare Ergebnisse |
| **fit / transform** | scikit-learn: `fit` lernt Parameter aus Daten, `transform` wendet sie an |

---

## Alphabetischer Index

| Begriff | Abschnitt |
|---|---|
| Achsenabschnitt | G |
| ANOVA | F |
| Ausreißer | A |
| Benachteiligungsindex | D |
| Bestimmtheitsmaß R² | G |
| Boxplot | A |
| Choroplethenkarte | J |
| Clusterprofil | I |
| Dezibel | B |
| Dummy-Variable | A |
| Eigenwert, Eigenvektor | D |
| Elbow-Methode | I |
| Energetischer Mittelwert | B |
| Erklärte Varianz | D |
| Euklidischer Abstand | I |
| F-Test | F, G |
| Fehler 1./2. Art | F |
| Fehlender Wert (NaN) | C |
| Freiheitsgrade | F |
| Geclusterte Standardfehler | H |
| Histogramm | A |
| Hypothese | F |
| Join / Merge | C |
| K-Means | I |
| Konfidenzintervall | G |
| Kontrollvariable | G |
| Korrelation (Pearson) | E |
| Korrelationsmatrix | D |
| Kovarianz | E |
| Ladung | D |
| LDEN | B |
| Logarithmus | A |
| Median | A |
| Mindestfallzahl | C |
| Mittelwert | A |
| Moran's I | H |
| Ökologischer Fehlschluss | C |
| OLS | G |
| p-Wert | F |
| PCA | D |
| Permutationstest | H |
| Quartile, Quintile | A |
| Queen-Nachbarschaft | H |
| Querschnittsanalyse | C |
| Räumliche Autokorrelation | H |
| Räumlicher Join | B |
| Regression | G |
| Residuum | G |
| Rangkorrelation (Spearman) | E |
| Scree-Plot | D |
| Selektionseffekt | C |
| Signifikanzniveau | F |
| Standardabweichung | A |
| Standardfehler | G |
| Standardisierung | D |
| Störvariable | E |
| Varianz | A |
| Zentroid | I |
| z-Wert | D |
