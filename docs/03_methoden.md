# 3. Die Methoden: einfach erklärt, mit Formeln

Dieses Kapitel erklärt jedes Verfahren in vier Schritten:
1. **Idee** – was macht das Verfahren, in Alltagssprache?
2. **Formel** – die mathematische Grundlage.
3. **Beispiel** – mit echten Zahlen aus unserem Projekt.
4. **Wozu bei uns?** – welche Frage es in unserem Projekt beantwortet.

Wer die Formeln überspringt, versteht trotzdem alles Wesentliche.

**Schreibweise:** $n$ = Anzahl der Beobachtungen (bei uns meist 535 Planungsräume), $x_i$ = Wert des $i$-ten Planungsraums, $\sum$ = „Summe über alle“.

---

## 3.0 Grundbegriffe der Statistik

### Mittelwert, Median, Quartile
- **Mittelwert** $\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$ – alle Werte addieren und durch die Anzahl teilen.
- **Median** – der Wert in der Mitte, wenn man alle Werte sortiert. Er ist unempfindlich gegen Ausreißer.
- **Quartile** – teilen die sortierten Werte in vier gleich große Teile. 25 % der Werte liegen unter dem 1. Quartil (Q1), 75 % unter dem 3. Quartil (Q3).

*Beispiel:* Der mittlere Lärm (LDEN) aller 542 Planungsräume ist 57,3 dB, der Median 57,4 dB. Weil beide fast gleich sind, ist die Verteilung ungefähr symmetrisch.

### Varianz und Standardabweichung
Wie stark streuen die Werte um den Mittelwert?

$$
s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2 \qquad s = \sqrt{s^2}
$$

Die **Standardabweichung** $s$ (englisch SD) hat dieselbe Einheit wie die Daten. Faustregel: Bei einer glockenförmigen Verteilung liegen etwa zwei Drittel der Werte im Bereich Mittelwert ± 1 SD.

*Beispiel:* Lärm: Mittelwert 57,3 dB, SD 3,6 dB → die meisten Planungsräume liegen zwischen ca. 54 und 61 dB.

### Korrelation (Pearson r)
Misst, wie stark zwei Variablen **linear** zusammenhängen:

$$
r = \frac{\sum_i (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_i (x_i - \bar{x})^2}\,\sqrt{\sum_i (y_i - \bar{y})^2}}
$$

- $r = +1$: perfekter positiver Zusammenhang (je mehr x, desto mehr y),
- $r = 0$: kein linearer Zusammenhang,
- $r = -1$: perfekter negativer Zusammenhang.

Faustregel: |r| < 0,1 kein, 0,1–0,3 schwach, 0,3–0,5 mittel, > 0,5 stark.

*Beispiel:* Miete und Lärm: r = 0,38 (mittel, positiv). Benachteiligung und Lärm: r = 0,06 (praktisch kein linearer Zusammenhang).

### Hypothesentest und p-Wert
Jeder Test hat zwei Hypothesen:
- **Nullhypothese H₀:** „Es gibt keinen Effekt“ (z. B. „Benachteiligung hat keinen Einfluss auf Lärm“).
- **Alternativhypothese H₁:** „Es gibt einen Effekt.“

Der **p-Wert** beantwortet die Frage: *Wenn H₀ stimmt – wie wahrscheinlich ist es, rein zufällig ein mindestens so starkes Ergebnis zu bekommen wie das, was wir beobachtet haben?*

- p < 0,05 → so ein Ergebnis wäre unter H₀ sehr unwahrscheinlich → wir **verwerfen H₀** und nennen das Ergebnis **signifikant**.
- p ≥ 0,05 → das Ergebnis könnte gut Zufall sein → wir können H₀ **nicht verwerfen**.

Die Grenze 0,05 heißt **Signifikanzniveau** (α). Sie bedeutet: Wir akzeptieren eine 5-%-Chance, einen Effekt zu „finden“, den es gar nicht gibt.

**Achtung, häufige Missverständnisse:**
- p = 0,29 heißt **nicht** „mit 29 % Wahrscheinlichkeit gibt es keinen Effekt“.
- „Nicht signifikant“ heißt **nicht** „bewiesen, dass es keinen Effekt gibt“, sondern „die Daten liefern keinen überzeugenden Beleg für einen Effekt“.
- „Signifikant“ heißt **nicht** „groß“ oder „wichtig“. Ein winziger Effekt kann bei vielen Daten signifikant sein.

### Standardfehler
Der **Standardfehler** (SE) eines geschätzten Werts sagt, wie stark dieser Wert schwanken würde, wenn man die Untersuchung mit anderen, ähnlichen Daten wiederholte. Kleiner SE = genaue Schätzung. Er ist die Grundlage für den p-Wert:

$$
z = \frac{\text{Schätzwert}}{\text{Standardfehler}}
$$

Je größer |z|, desto kleiner der p-Wert. Ab |z| > 1,96 ist p < 0,05.

---

## 3.1 Standardisierung (z-Transformation)

### Idee
Unsere Variablen haben verschiedene Einheiten: Lärm in dB (Werte um 57), Kinderarmut in % (Werte zwischen 0 und 64), Miete in EUR/m². Wenn man sie direkt kombiniert, dominiert die Variable mit den größten Zahlen. Die Standardisierung bringt alle Variablen auf **dieselbe Skala**: Mittelwert 0, Standardabweichung 1.

### Formel

$$
z_i = \frac{x_i - \bar{x}}{s}
$$

Ein z-Wert sagt: **Wie viele Standardabweichungen liegt dieser Wert über (+) oder unter (−) dem Durchschnitt?**

### Beispiel
Planungsraum „Soldiner Straße“ (Wedding), Arbeitslosigkeit S1 = 9,24 %. Berliner Mittel 4,69 %, SD 2,59 %:

$$
z = \frac{9{,}24 - 4{,}69}{2{,}59} = 1{,}76
$$

Die Arbeitslosigkeit liegt dort 1,76 Standardabweichungen über dem Berliner Durchschnitt.

### Wozu bei uns?
- vor der **PCA** (sonst würde Kinderarmut mit der größten Streuung die PCA dominieren),
- vor **K-Means** (sonst würde die Miete mit ihrer Skala die Abstände bestimmen),
- der fertige **Benachteiligungsindex** ist selbst standardisiert: 0 = Berliner Durchschnitt, +1 = eine SD benachteiligter als der Durchschnitt.

---

## 3.2 Hauptkomponentenanalyse (PCA)

### Idee
Wir haben vier soziale Indikatoren (S1 Arbeitslosigkeit, S2 Alleinerziehende, S3 Transferbezug, S4 Kinderarmut). Sie hängen stark zusammen: Wo viele Menschen arbeitslos sind, beziehen auch viele Sozialleistungen, und viele Kinder leben in Armut. Im Grunde messen sie **dasselbe Phänomen** – soziale Benachteiligung – aus leicht verschiedenen Blickwinkeln.

Die PCA sucht die **eine Richtung**, in der die Daten am stärksten streuen, und fasst die vier Variablen zu einer neuen Variable zusammen: der **ersten Hauptkomponente (PC1)**. Diese ist unser Benachteiligungsindex.

**Bild dazu:** Stell dir eine Punktwolke vor, die wie eine Zigarre geformt ist. PC1 ist die Längsachse der Zigarre. Projiziert man jeden Punkt auf diese Achse, verliert man nur wenig Information – die Punkte unterscheiden sich vor allem entlang dieser Achse.

**Warum nicht einfach den Durchschnitt der vier Werte nehmen?**
1. Die Einheiten und Streuungen sind verschieden (Kinderarmut streut viel stärker als Arbeitslosigkeit).
2. Die PCA bestimmt die Gewichte **aus den Daten** statt willkürlich.
3. Sie sagt uns, **wie gut** eine einzige Zahl die vier Indikatoren zusammenfasst (erklärte Varianz).

### Formeln und Schritte

**Schritt 1 – Standardisieren:** Jeder Indikator wird z-transformiert (siehe 3.1). Ergebnis: Matrix $Z$ mit 535 Zeilen (PLR) und 4 Spalten (S1–S4).

**Schritt 2 – Korrelationsmatrix:** Für standardisierte Daten ist die Kovarianzmatrix gleich der Korrelationsmatrix $R$:

$$
R = \frac{1}{n-1} Z^\top Z
$$

Unsere Korrelationsmatrix:

|  | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|
| S1 Arbeitslosigkeit | 1 | 0,52 | 0,95 | 0,93 |
| S2 Alleinerziehende | 0,52 | 1 | 0,46 | 0,52 |
| S3 Transferbezug | 0,95 | 0,46 | 1 | 0,96 |
| S4 Kinderarmut | 0,93 | 0,52 | 0,96 | 1 |

S1, S3 und S4 sind fast identisch (r ≈ 0,95). S2 hängt schwächer mit den anderen zusammen.

**Schritt 3 – Eigenwerte und Eigenvektoren:** Man löst die Gleichung

$$
R\,v = \lambda\,v
$$

- Der **Eigenvektor** $v$ ist eine Richtung (die Gewichte der Indikatoren).
- Der **Eigenwert** $\lambda$ sagt, wie viel Varianz in dieser Richtung liegt.

Bei 4 Variablen gibt es 4 Eigenwerte. Ihre Summe ist 4 (jede standardisierte Variable bringt Varianz 1 mit).

| Komponente | Eigenwert λ | Erklärte Varianz λ / 4 |
|---|---:|---:|
| PC1 | 3,235 | **80,7 %** |
| PC2 | 0,670 | 16,7 % |
| PC3 | 0,071 | 1,8 % |
| PC4 | 0,032 | 0,8 % |

**Erklärte Varianz:**

$$
\text{Anteil}_k = \frac{\lambda_k}{\sum_j \lambda_j}
$$

PC1 allein enthält 80,7 % der gesamten Information der vier Indikatoren. Das ist sehr viel – eine einzige Zahl reicht.

**Schritt 4 – Gewichte (Eigenvektor von PC1):**

| Indikator | Gewicht $v$ | Ladung $v \cdot \sqrt{\lambda}$ |
|---|---:|---:|
| S1 Arbeitslosigkeit | 0,538 | 0,967 |
| S2 Alleinerziehende | 0,361 | 0,649 |
| S3 Transferbezug | 0,537 | 0,966 |
| S4 Kinderarmut | 0,541 | 0,973 |

Die **Ladung** ist die Korrelation zwischen einem Indikator und PC1. Alle Ladungen sind positiv und hoch → PC1 misst „allgemeine soziale Benachteiligung“. S2 trägt etwas weniger bei, weil es schwächer mit den anderen zusammenhängt.

**Schritt 5 – Wert für jeden Planungsraum (Score):**

$$
\text{PC1}_i = \sum_{k=1}^{4} v_k \cdot z_{ik}
$$

**Schritt 6 – Index standardisieren:** Damit der Index leicht lesbar ist, wird PC1 noch einmal z-standardisiert (Mittelwert 0, SD 1). Das Vorzeichen wird so gewählt, dass **höhere Werte = mehr Benachteiligung** bedeuten.

### Durchgerechnetes Beispiel: Soldiner Straße (Wedding)

| | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|
| Rohwert | 9,24 % | 25,67 % | 21,81 % | 48,07 % |
| Berliner Mittel | 4,69 % | 24,00 % | 9,87 % | 20,75 % |
| SD | 2,59 | 6,30 | 6,09 | 13,56 |
| z-Wert | 1,76 | 0,27 | 1,96 | 2,02 |
| × Gewicht | 0,538 | 0,361 | 0,537 | 0,541 |
| = Beitrag | 0,95 | 0,10 | 1,05 | 1,09 |

PC1 = 0,95 + 0,10 + 1,05 + 1,09 = **3,18**. Die Standardabweichung aller PC1-Werte ist 1,80. Index = 3,18 / 1,80 = **+1,77**.

→ Die Soldiner Straße ist 1,77 Standardabweichungen benachteiligter als der Berliner Durchschnitt und gehört damit zu den rund 5 % am stärksten benachteiligten Planungsräumen Berlins.

### Qualitätskontrolle
Das MSS berechnet selbst einen amtlichen Status-Index (Summe der z-Werte S1–S4, erneut standardisiert). Unser PCA-Index korreliert damit zu **r = 0,998** – praktisch identisch. Das bestätigt, dass unsere Berechnung richtig ist und der Index das misst, was er messen soll.

### Wozu bei uns?
Der Benachteiligungsindex ist die zentrale Variable für H1 (Lärm ~ Benachteiligung), H2 (Miete ~ Benachteiligung) und H3 (K-Means).

---

## 3.3 Deskriptive Statistik und Visualisierung

### Idee
Bevor man testet, muss man die Daten kennenlernen: Welche Werte kommen vor? Gibt es Ausreißer? Sind die Daten schief verteilt?

### Werkzeuge
- **Kennzahlentabelle:** Anzahl, Mittelwert, SD, Minimum, Quartile, Maximum, Varianz.
- **Histogramm:** Balkendiagramm der Häufigkeiten. Die x-Achse zeigt die Werte, die y-Achse, wie viele Planungsräume diesen Wert haben. Die geglättete Linie (KDE) zeigt die Form der Verteilung.
- **Korrelationsmatrix:** Tabelle aller paarweisen Korrelationen, als farbige Heatmap. Rot = positiv, Blau = negativ, Weiß = kein Zusammenhang.

### Wozu bei uns?
- Prüfen, ob Werte plausibel sind (z. B. Lärm zwischen 46 und 73 dB – passt).
- Erkennen, dass die Einwohnerdichte sehr schief verteilt ist → deshalb Logarithmus.
- Erster Überblick über Zusammenhänge (z. B. dass Benachteiligung und Lärm kaum linear korrelieren, Benachteiligung und Miete aber deutlich negativ: r = −0,48).

---

## 3.4 Varianzanalyse (ANOVA)

### Idee
Wir teilen die 535 Planungsräume nach ihrem Benachteiligungsindex in **fünf gleich große Gruppen** (Quintile) zu je 107 Gebieten:
- Q1 = die 20 % am wenigsten benachteiligten,
- …
- Q5 = die 20 % am stärksten benachteiligten.

Die ANOVA prüft: **Unterscheidet sich der mittlere Lärm zwischen diesen Gruppen stärker, als man durch Zufall erwarten würde?**

Der große Vorteil gegenüber der Regression: Die ANOVA setzt **keinen geradlinigen Zusammenhang** voraus. Sie erkennt auch Muster wie „nur Q1 ist anders“ oder „in der Mitte am lautesten“.

### Formel
Die Grundidee ist ein Vergleich zweier Streuungen:
- **Streuung zwischen den Gruppen:** Wie weit liegen die Gruppenmittelwerte auseinander?
- **Streuung innerhalb der Gruppen:** Wie stark schwanken die Werte innerhalb jeder Gruppe?

$$
SS_{zwischen} = \sum_{g=1}^{k} n_g (\bar{x}_g - \bar{x})^2 \qquad
SS_{innerhalb} = \sum_{g=1}^{k} \sum_{i \in g} (x_i - \bar{x}_g)^2
$$

$$
F = \frac{SS_{zwischen} / (k-1)}{SS_{innerhalb} / (N-k)}
$$

mit $k$ = Anzahl Gruppen (5), $N$ = Anzahl Beobachtungen (535), $n_g$ = Größe der Gruppe $g$ (107).

- **F groß** → die Gruppen unterscheiden sich stark im Verhältnis zur Streuung innerhalb → kleiner p-Wert.
- **F ≈ 1** → die Unterschiede zwischen den Gruppen sind nicht größer als die zufällige Streuung.

Hypothesen:
- H₀: Alle fünf Gruppen haben denselben mittleren Lärm.
- H₁: Mindestens eine Gruppe unterscheidet sich.

### Unser Ergebnis

| Quintil | Q1 (geringste) | Q2 | Q3 | Q4 | Q5 (stärkste) |
|---|---:|---:|---:|---:|---:|
| mittlerer Lärm (dB) | 55,8 | 58,4 | 57,7 | 57,2 | 57,4 |

F = 7,97 (mit 4 und 530 Freiheitsgraden), p < 0,001 → H₀ wird verworfen; die Gruppen unterscheiden sich.

**Aber:** Die ANOVA sagt nur, **dass** es Unterschiede gibt, nicht **welche**. Der Blick auf die Mittelwerte zeigt: Nur Q1 fällt heraus (1,9 dB leiser). Q2 bis Q5 liegen innerhalb von 1,2 dB – es gibt keine Treppe „je benachteiligter, desto lauter“.

### Wozu bei uns?
Prüfung von H1 ohne Annahme einer geraden Linie. Die ANOVA deckt das **nichtlineare Muster** auf, das die Regression allein übersehen würde.

### Grenze
Die ANOVA nimmt (wie die normale Regression) an, dass die Beobachtungen unabhängig sind. Das stimmt räumlich nicht ganz (siehe Moran's I, 3.6). Der p-Wert ist deshalb eher zu optimistisch; bei p < 0,001 ändert das aber nichts an der Aussage, dass Q1 leiser ist.

---

## 3.5 Multiple lineare Regression

### Idee
Die Regression legt eine **Gerade (bzw. Ebene) durch die Punktwolke**, die die Daten am besten beschreibt. Sie beantwortet: *Um wie viel ändert sich y im Durchschnitt, wenn x um eine Einheit steigt?*

„Multiple“ heißt: mehrere Einflussgrößen gleichzeitig. Das ist wichtig, um Effekte **auseinanderzuhalten**. Beispiel: Wenn Innenstadtgebiete sowohl lauter als auch benachteiligter wären, würde eine einfache Regression den Lärm fälschlich der Benachteiligung zuschreiben. Nimmt man „Innere Stadt“ als **Kontrollvariable** ins Modell, wird dieser Lageeffekt herausgerechnet.

### Formel
Das Modell:

$$
y_i = \beta_0 + \beta_1 x_{1i} + \beta_2 x_{2i} + \dots + \beta_k x_{ki} + \varepsilon_i
$$

- $y_i$: Zielvariable (z. B. Lärm im Planungsraum $i$)
- $x_{1i}, x_{2i}, \dots$: Einflussvariablen (Prädiktoren)
- $\beta_0$: Achsenabschnitt (Konstante)
- $\beta_1, \beta_2, \dots$: **Koeffizienten** – um wie viel ändert sich $y$, wenn $x_j$ um 1 steigt und alle anderen $x$ gleich bleiben
- $\varepsilon_i$: Fehler (Residuum) – was das Modell nicht erklärt

**Kleinste-Quadrate-Methode (OLS, „Ordinary Least Squares“):** Die Koeffizienten werden so gewählt, dass die Summe der quadrierten Abstände zwischen Datenpunkten und Gerade minimal ist:

$$
\min_{\beta} \sum_{i=1}^{n} \left(y_i - \hat{y}_i\right)^2
\quad\Rightarrow\quad
\hat{\beta} = (X^\top X)^{-1} X^\top y
$$

Für den einfachen Fall mit nur einem $x$ gilt anschaulich:

$$
\hat{\beta}_1 = \frac{\text{Kov}(x, y)}{\text{Var}(x)} \qquad \hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}
$$

**Bestimmtheitsmaß R²:** Welcher Anteil der Unterschiede in $y$ wird durch das Modell erklärt?

$$
R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}
$$

R² = 0 → das Modell erklärt nichts; R² = 1 → das Modell erklärt alles.

**Test der Koeffizienten:** Für jeden Koeffizienten wird geprüft, ob er sich signifikant von 0 unterscheidet (H₀: $\beta_j = 0$). Dafür teilt man den Koeffizienten durch seinen Standardfehler (siehe 3.0). Der klassische Standardfehler kommt aus

$$
\widehat{\text{Var}}(\hat{\beta}) = \hat{\sigma}^2 (X^\top X)^{-1}, \qquad \hat{\sigma}^2 = \frac{1}{n-k-1}\sum_i \hat{\varepsilon}_i^2
$$

Diese Formel setzt voraus, dass die Fehler **unabhängig** voneinander sind. Genau das prüfen wir in 3.6 und korrigieren es in 3.7.

### Unsere drei Modelle

| Modell | Formel | Frage |
|---|---|---|
| **A1** | Lärm = β₀ + β₁ · Benachteiligung | Wie hängt Lärm allein mit Benachteiligung zusammen? |
| **A2** | Lärm = β₀ + β₁ · Benachteiligung + β₂ · log(Dichte) + β₃ · Innere Stadt | Bleibt der Zusammenhang, wenn man Dichte und Lage berücksichtigt? |
| **B** | Miete = β₀ + β₁ · Lärm + β₂ · Benachteiligung + β₃ · log(Dichte) + β₄ · Innere Stadt | Wie hängen Lärm und Benachteiligung mit der Miete zusammen? |

**Die Kontrollvariablen:**
- **log(1 + Einwohnerdichte):** Dichte Gebiete haben mehr Verkehr. Der Logarithmus sorgt dafür, dass der Schritt von 1.000 auf 2.000 EW/km² gleich viel zählt wie der von 10.000 auf 20.000 (beides eine Verdopplung).
- **Innere Stadt (0/1):** Eine sogenannte **Dummy-Variable**. Ihr Koeffizient ist der Unterschied zwischen Innen- und Außenstadt bei sonst gleichen Werten.

### Wie liest man einen Koeffizienten?
Weil der Benachteiligungsindex standardisiert ist, bedeutet sein Koeffizient: **Änderung der Zielgröße, wenn die Benachteiligung um eine Standardabweichung steigt.**

*Beispiel aus Modell A2:*
- Benachteiligung: β = +0,22 → pro SD mehr Benachteiligung im Mittel 0,22 dB mehr Lärm (winzig – 0,22 dB hört kein Mensch).
- Innere Stadt: β = +3,55 → Innenstadtgebiete sind bei gleicher Benachteiligung und Dichte im Mittel 3,6 dB lauter.

*Beispiel aus Modell B:*
- Lärm: β = +0,23 → pro dB mehr Lärm ist die Angebotsmiete im Mittel 0,23 EUR/m² höher.
- Benachteiligung: β = −2,09 → pro SD mehr Benachteiligung ist die Miete 2,09 EUR/m² niedriger.

### Wozu bei uns?
Hauptprüfung von H1 (Modelle A1, A2) und H2 (Modell B).

---

## 3.6 Räumliche Abhängigkeit: Moran's I

### Idee
Die normale Statistik nimmt an, dass jede Beobachtung unabhängig von den anderen ist – wie bei Münzwürfen. Bei Gebieten stimmt das nicht: **Benachbarte Gebiete ähneln sich.** Eine laute Hauptstraße verläuft durch mehrere Planungsräume; ein wohlhabendes Viertel endet nicht an einer Verwaltungsgrenze. Das nennt man **räumliche Autokorrelation** („Tobler's erstes Gesetz der Geographie“: Alles hängt mit allem zusammen, aber Nahes mehr als Fernes).

**Moran's I** misst, wie stark das der Fall ist.

### Wer ist Nachbar? (Gewichtsmatrix)
Wir nutzen die **Queen-Nachbarschaft** (wie die Dame im Schach): Zwei Planungsräume sind Nachbarn, wenn sie eine gemeinsame Grenze oder auch nur einen gemeinsamen Eckpunkt haben. Das wird in einer Matrix $W$ gespeichert: $w_{ij} = 1$, wenn $i$ und $j$ Nachbarn sind, sonst 0.

Die Matrix wird **zeilenstandardisiert**: Jede Zeile wird durch die Anzahl der Nachbarn geteilt, sodass $\sum_j w_{ij} = 1$. Dann ist $\sum_j w_{ij} x_j$ einfach der **Durchschnitt der Nachbarn** von $i$.

### Formel

$$
I = \frac{n}{\sum_i \sum_j w_{ij}} \cdot \frac{\sum_i \sum_j w_{ij}(x_i - \bar{x})(x_j - \bar{x})}{\sum_i (x_i - \bar{x})^2}
$$

Mit zeilenstandardisierten Gewichten ist $\sum_i \sum_j w_{ij} = n$, und mit $z_i = x_i - \bar{x}$ vereinfacht sich das zu:

$$
I = \frac{\sum_i z_i \cdot \left(\sum_j w_{ij} z_j\right)}{\sum_i z_i^2}
$$

**Anschaulich:** I misst, wie stark der Wert eines Gebiets mit dem Durchschnittswert seiner Nachbarn zusammenhängt – ähnlich einer Korrelation zwischen „ich“ und „meine Nachbarn“.

| Wert | Bedeutung |
|---|---|
| I > 0 | Ähnliche Werte liegen nebeneinander (laut neben laut, leise neben leise) – **Clusterung** |
| I ≈ 0 | Zufällige räumliche Verteilung (genau: Erwartungswert $-1/(n-1) \approx 0$) |
| I < 0 | Gegensätze liegen nebeneinander (Schachbrettmuster) – selten |

### Signifikanztest durch Permutation
Wie wissen wir, ob I = 0,46 „viel“ ist? Der Computer **mischt die Werte 999-mal zufällig** über die Karte (die Geometrie bleibt, die Werte werden vertauscht) und berechnet jedes Mal I. So entsteht eine Verteilung „wie I aussieht, wenn es keine räumliche Struktur gibt“. Der p-Wert ist der Anteil der Zufalls-Mischungen, die ein mindestens so großes I erreichen:

$$
p_{sim} = \frac{(\text{Anzahl Permutationen mit } I_{perm} \geq I_{beob}) + 1}{999 + 1}
$$

Der kleinstmögliche Wert ist 1/1000 = 0,001. Wenn p_sim = 0,001, hat **keine einzige** der 999 Mischungen ein so hohes I erreicht.

### Unsere Ergebnisse

| Variable | I | p_sim | Bedeutung |
|---|---:|---:|---|
| Lärm | 0,46 | ≤ 0,001 | laute Gebiete liegen neben lauten |
| Benachteiligungsindex | 0,43 | ≤ 0,001 | benachteiligte Gebiete liegen nebeneinander |
| Residuen Modell A1 | 0,47 | ≤ 0,001 | die Fehler der Regression sind räumlich gehäuft |
| Residuen Modell A2 | 0,30 | ≤ 0,001 | mit Kontrollvariablen weniger, aber immer noch gehäuft |

### Warum sind die Residuen so wichtig?
Ein **Residuum** ist der Fehler des Modells für ein Gebiet: tatsächlicher Lärm minus vorhergesagter Lärm. Wenn die Residuen räumlich geclustert sind, heißt das: Das Modell liegt in ganzen Stadtteilen systematisch daneben. Die 535 Planungsräume liefern dann **weniger unabhängige Information**, als die Zahl 535 vermuten lässt – ähnlich wie 10 Umfragen in derselben Familie weniger aussagen als 10 Umfragen in verschiedenen Familien.

Folge: Die klassischen Standardfehler sind **zu klein**, die p-Werte **zu optimistisch**. Deshalb brauchen wir die Korrektur in 3.7.

---

## 3.7 Räumlich geclusterte Standardfehler

### Idee
Wir sagen dem Modell: „Planungsräume, die im selben **Prognoseraum** liegen, sind nicht unabhängig – behandle sie als Gruppe.“ Berlin hat 58 Prognoseräume mit je 2 bis 21 Planungsräumen (im Schnitt 9). Innerhalb eines Prognoseraums dürfen die Fehler beliebig miteinander zusammenhängen; zwischen verschiedenen Prognoseräumen wird Unabhängigkeit angenommen.

**Wichtig:** Die **Koeffizienten bleiben exakt gleich**. Es ändert sich nur die Einschätzung der **Unsicherheit** (Standardfehler und damit p-Wert).

### Formel
Klassischer Standardfehler (siehe 3.5):

$$
\widehat{\text{Var}}_{klassisch}(\hat{\beta}) = \hat{\sigma}^2 (X^\top X)^{-1}
$$

Geclusterter Standardfehler („Sandwich-Schätzer“):

$$
\widehat{\text{Var}}_{cluster}(\hat{\beta}) = c \cdot (X^\top X)^{-1} \left( \sum_{g=1}^{G} X_g^\top \hat{\varepsilon}_g \hat{\varepsilon}_g^\top X_g \right) (X^\top X)^{-1}
$$

- $G$ = Anzahl der Cluster (58 Prognoseräume)
- $X_g$, $\hat{\varepsilon}_g$ = Daten und Residuen der Planungsräume im Prognoseraum $g$
- $c = \frac{G}{G-1}\cdot\frac{N-1}{N-K}$ = kleine Korrektur für endliche Stichproben

**Anschaulich:** Die „Füllung“ des Sandwiches ($\sum_g \ldots$) summiert die Residuen **innerhalb jedes Prognoseraums zuerst** auf. Wenn die Fehler in einem Prognoseraum alle in dieselbe Richtung zeigen (alle zu hoch oder alle zu niedrig), addieren sie sich auf statt sich auszugleichen → die geschätzte Unsicherheit wird größer.

### Unser Ergebnis

| Modell, Koeffizient | β | SE klassisch | p klassisch | SE geclustert | p geclustert |
|---|---:|---:|---:|---:|---:|
| A1: Benachteiligung → Lärm | +0,22 | 0,156 | 0,152 | 0,294 | **0,445** |
| A2: Benachteiligung → Lärm | +0,22 | 0,156 | 0,154 | 0,210 | **0,289** |
| A2: Innere Stadt → Lärm | +3,55 | 0,352 | < 0,001 | 0,677 | **< 0,001** |
| B: Lärm → Miete | +0,23 | 0,047 | < 0,001 | 0,056 | **< 0,001** |
| B: Benachteiligung → Miete | −2,09 | 0,170 | < 0,001 | 0,180 | **< 0,001** |

Die Standardfehler werden durch die Korrektur fast doppelt so groß (A1: 0,156 → 0,294). Die **Aussagen ändern sich nicht**: H1 bleibt nicht signifikant (noch deutlicher), H2 bleibt hochsignifikant. Damit ist das Ergebnis gegen den Einwand „Ihr habt die räumliche Abhängigkeit ignoriert“ abgesichert.

### Wozu bei uns?
Alle p-Werte in der Ergebnisgrafik und im Fazit sind die **geclusterten** p-Werte. Die klassischen stehen zum Vergleich in `regression_uebersicht.csv`.

---

## 3.8 K-Means-Clustering

### Idee
K-Means teilt die Planungsräume automatisch in $k$ Gruppen (**Cluster**) ein, sodass Gebiete innerhalb einer Gruppe sich möglichst ähnlich sind. „Ähnlich“ heißt hier: ähnlicher Lärm, ähnliche Benachteiligung, ähnliche Miete. Man muss vorher nur festlegen, **wie viele** Gruppen es geben soll ($k$).

Das ist **unüberwachtes Lernen**: Es gibt keine „richtigen“ Gruppen, die der Algorithmus lernen soll – er findet die Struktur selbst.

### Merkmale
Drei standardisierte Merkmale (Standardisierung ist nötig, sonst würde die Miete mit ihren Euro-Werten die Abstände dominieren):
1. Lärm (LDEN),
2. Benachteiligungsindex,
3. Angebotsmiete.

Weil die Miete nur für 434 Planungsräume vorliegt, werden diese 434 geclustert. Die übrigen erscheinen in der Karte grau.

### Algorithmus (Lloyd-Algorithmus)
1. **Start:** Wähle $k$ zufällige Startpunkte als Clustermittelpunkte („Zentroide“).
2. **Zuordnen:** Ordne jeden Planungsraum dem nächstgelegenen Zentroid zu (euklidischer Abstand im 3-dimensionalen Merkmalsraum):
   $$
   d(x_i, \mu_c) = \sqrt{\sum_{m=1}^{3}(x_{im} - \mu_{cm})^2}
   $$
3. **Aktualisieren:** Berechne jeden Zentroid neu als Mittelwert seiner zugeordneten Gebiete.
4. **Wiederholen** von Schritt 2 und 3, bis sich nichts mehr ändert.

Ziel ist, die **Inertia** (Summe der quadrierten Abstände zum eigenen Zentroid) zu minimieren:

$$
\text{Inertia} = \sum_{c=1}^{k} \sum_{i \in C_c} \lVert x_i - \mu_c \rVert^2
$$

Weil das Ergebnis vom zufälligen Start abhängt, wird der Algorithmus 20-mal mit verschiedenen Startpunkten ausgeführt (`n_init=20`) und das beste Ergebnis genommen. Ein fester Zufallsstartwert (`random_state=42`) sorgt dafür, dass bei jedem Lauf dasselbe herauskommt.

### Wahl von k: Elbow-Methode
Mehr Cluster verringern immer die Inertia (im Extremfall ist jedes Gebiet sein eigener Cluster, Inertia = 0). Man sucht den „Ellenbogen“: den Punkt, ab dem zusätzliche Cluster kaum noch Verbesserung bringen.

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Inertia | 1302 | 825 | 615 | 518 | 453 | 400 | 359 |
| Verbesserung | – | −477 | −210 | −97 | −65 | −53 | −41 |

Bis k = 4 sinkt die Inertia deutlich, danach nur noch wenig. Der Knick ist nicht ganz scharf (ehrlicherweise liegt er irgendwo zwischen 3 und 4). Den Ausschlag für **k = 4** gibt die **Interpretierbarkeit**: Mit 4 Clustern entsteht eine klare Typologie aus „laut/leise“ × „benachteiligt/wohlhabend“. Das ist eine bewusste, begründete Entscheidung.

### Benennung der Cluster
Für jeden Cluster wird der Mittelwert jedes standardisierten Merkmals berechnet. Liegt er über +0,25 SD, heißt das Merkmal „hoch“, unter −0,25 SD „niedrig“, dazwischen „mittel“. So entstehen automatisch Namen wie „C3: Lärm hoch · Benachteiligung hoch · Miete niedrig“. Die Cluster werden nach mittlerem Lärm sortiert (C1 = am leisesten).

### Unser Ergebnis

| Cluster | n | Lärm (dB) | Index | Miete (EUR/m²) | Typische Gebiete |
|---|---:|---:|---:|---:|---|
| C1 Lärm niedrig · Benachteiligung hoch · Miete niedrig | 88 | 54,8 | +1,00 | 9,7 | Großsiedlungen am Stadtrand (Marzahn-Hellersdorf, Hohenschönhausen, Gropiusstadt) |
| C2 Lärm niedrig · Benachteiligung niedrig · Miete mittel | 113 | 55,0 | −0,75 | 15,3 | Äußere Stadt, Einfamilienhausgebiete (Pankow, Steglitz-Zehlendorf, Köpenick) |
| C3 Lärm hoch · Benachteiligung hoch · Miete niedrig | 101 | 59,3 | +0,87 | 13,8 | Wedding, Nord-Neukölln, Schöneberg-Nord |
| C4 Lärm hoch · Benachteiligung niedrig · Miete hoch | 132 | 60,5 | −0,46 | 19,6 | Innenstadt: Charlottenburg, Mitte, Prenzlauer Berg, Friedrichshain |

### Wozu bei uns?
Prüfung von H3 und Identifikation des „mehrfach belasteten“ Gebietstyps C3.

---

## 3.9 Wie die Methoden zusammenspielen

```text
Rohdaten S1–S4 ──Standardisierung──► PCA ──► Benachteiligungsindex
                                                    │
        ┌───────────────────────────────────────────┼─────────────────────────┐
        ▼                                           ▼                         ▼
     ANOVA                                    Regression A1/A2/B          K-Means
 (Unterschiede zwischen                    (Stärke des Zusammenhangs,  (Gebietstypen,
  Quintilen, nichtlinear)                   mit Kontrollvariablen)      mit Lärm + Miete)
                                                    │
                                              Residuen
                                                    ▼
                                              Moran's I
                                     (sind die Fehler räumlich gehäuft?)
                                                    │  ja
                                                    ▼
                                     geclusterte Standardfehler
                                       (korrigierte p-Werte)
```

Jede Methode beantwortet eine andere Teilfrage. Zusammen ergeben sie ein vollständiges Bild:
- **ANOVA** zeigt: Es gibt Unterschiede, aber nur Q1 ist anders.
- **Regression** zeigt: Ein linearer Zusammenhang ist nicht nachweisbar; die Lage erklärt mehr.
- **Moran + geclusterte SE** zeigen: Dieses Ergebnis hält auch, wenn man die räumliche Struktur berücksichtigt.
- **K-Means** zeigt: Die Belastung konzentriert sich auf einen bestimmten Gebietstyp.
