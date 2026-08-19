# RailwAI

Die Daten für das Projekt **RailwAI** stammen aus zwei unterschiedlichen Quellen: dem **FTP-Server** und der **GeoVIS-API**.

## FTP

Auf dem FTP-Server sind die Rohdaten der einzelnen Zugdurchfahrten für bestimmte Sensoren abgelegt. Für einige Projekte stehen zusätzlich Videos der Zugdurchfahrten zur Verfügung, die als Referenzdaten für die Bestimmung des Zugtyps verwendet werden.

* **`data_download.py`**
  Verbindet sich mit dem entsprechenden FTP-Server, sucht anhand des `file_pattern` nach den passenden ADTC-Rohdaten und lädt diese in den Ordner `RAW_DATA` herunter.

* **`data_decoder.py`**
  Dekodiert die vom FTP-Server heruntergeladenen Rohdaten und wandelt die 7-Bit-ASCII-/Hex-Daten in Messwerte um. Bei Bedarf wird die Abtastfrequenz von 4000 Hz auf 1000 Hz reduziert und die Daten werden als CSV-Dateien gespeichert.

* **`log.py`**
  Ordnet anhand des `file_pattern` das entsprechende Projekt zu und stellt die benötigten FTP-Zugangsdaten, den Port und den Remote-Ordner bereit. Für die Videos wird zusätzlich das Datum aus dem Identifier extrahiert, um den entsprechenden Videoordner auf dem FTP-Server zu bestimmen. Diese Datei ist nicht auf GitHub zu puschen.

* **`video_download.py`**
  Verbindet sich mit dem projektspezifischen FTP-Server, sucht nach den passenden Videodateien und lädt diese für den gewünschten Tag in den lokalen Ordner `VIDEO` herunter.

## GeoVIS

Über die **GeoVIS-API** können die Messdaten aller Sensoren abgerufen werden. Diese Daten sind bereits vorverarbeitet und enthalten hauptsächlich die relevanten Peaks der Sensorsignale. Sie werden verwendet, um die Geschwindigkeit der einzelnen Achsen zwischen aufeinanderfolgenden Sensorpaaren zu berechnen. Zusätzlich werden die Anzahl der Achsen sowie die mittlere Zuggeschwindigkeit im DataFrame `dfs_raw` gespeichert.

* **`DTC.env`**
  Enthält die Zugangsdaten für den Zugriff auf die GeoVIS-API. Diese Datei ist nicht auf GitHub zu puschen. 

* **`Geschwindigkeit.py`**
  Berechnet anhand der erkannten Peak-Zeitpunkte die Geschwindigkeit der einzelnen Zugachsen zwischen den Sensoren.

### API

* **`ADTC_Analyze_FHNW.py`**
  Stellt die Verbindung zur GeoVIS4.0-REST-API her und ermöglicht den Zugriff auf Projekte, Sensoren und deren Messdaten.

* **`Datenbezug_API.py`**
  Ruft die Messdaten der ausgewählten Sensoren für einen bestimmten Zeitraum über die GeoVIS-API ab, bereitet sie als Pandas-DataFrames auf und unterteilt die Messungen anhand von Zeitlücken in einzelne Zugdurchfahrten.

### Preprocessing

* **`Peak_Detektion.py`**
  Erkennt anhand definierter Schwellenwerte die relevanten negativen Peaks in den Sensordaten und speichert die erkannten Peaks für die jeweiligen Zeitpunkte und Sensoren.

# Code

## 01_CWT_generation

Als Ausgangspunkt wird ein eindeutiger Identifier (`filename`) verwendet, beispielsweise:

```python
filename = 'ADTC_83_2_L_adz_raw_20260812'
```

Dieser Identifier wird für die Verarbeitung aus beiden Datenquellen verwendet.

Zunächst werden anhand des Identifiers die entsprechenden Rohdaten vom FTP-Server heruntergeladen und dekodiert. Die dekodierten Sensordaten werden anschliessend als CSV-Dateien gespeichert und können dadurch weiterverarbeitet werden.

Parallel dazu wird derselbe Identifier verwendet, um über die GeoVIS-API die Messdaten der entsprechenden Sensoren für den jeweiligen Tag abzurufen. Da die Sensordaten zeitlich synchronisiert sind, können die Peaks der verschiedenen Sensoren miteinander verglichen werden.

Aus den Zeitunterschieden zwischen den erkannten Achsdurchfahrten und dem bekannten Abstand zwischen den Sensoren wird die Geschwindigkeit der einzelnen Achsen berechnet. Mithilfe dieser Geschwindigkeit und der Zeitdifferenzen zwischen den aufeinanderfolgenden Achsen kann anschliessend der Abstand zwischen den Achsen und daraus die Gesamtlänge des Zuges bestimmt werden.

Die ermittelte Zuglänge wird anschliessend verwendet, um die vom FTP-Server dekodierten CSV-Dateien zu standardisieren. Die Signale werden auf eine maximale Zuglänge von 400 m skaliert bzw. bei Bedarf gekürzt, sodass alle Zugdurchfahrten dieselbe maximale Länge besitzen. Dadurch können die verschiedenen Zugdurchfahrten miteinander verglichen und anschliessend einheitlich als CWT-Bilder dargestellt werden.

Für die Klassifikation des Zugtyps wird zusätzlich nur der vordere Bereich des Zuges, also die Lok bzw. der erste Wagen eines Triebzuges, betrachtet. Hierfür werden die CSV-Signale auf die ersten vier relevanten Peaks reduziert. Aus diesem Signalbereich werden ebenfalls CWT-Bilder erzeugt. Die maximale Länge dieses Bereichs beträgt 50 m. Ist der tatsächliche vordere Bereich beispielsweise nur 20 m lang, werden die fehlenden 30 m mit dem Wert 0 aufgefüllt, damit alle Bilder dieselbe standardisierte Länge besitzen.

Im letzten Schritt werden die beiden CWT-Darstellungen zu einem RGB-Bild mit zwei belegten Kanälen kombiniert:

* **Rot (R):** CWT der gesamten Zugdurchfahrt
* **Grün (G):** CWT der Lok bzw. des ersten Wagens
* **Blau (B):** bleibt leer

Dadurch enthält jedes kombinierte Bild gleichzeitig Informationen über die gesamte Zuglänge und über den vorderen Bereich des Zuges, der für die Unterscheidung zwischen Triebzug und Lokzug besonders relevant ist.

## 02_video_reference_data

Wie bereits bei `01_CWT_generation` wird ein eindeutiger **Identifier** benötigt, um die Videos für den gewünschten Tag herunterzuladen.

Die Videos werden mit der Funktion `video_downloader()` aus `FTP/video_download.py` vom entsprechenden FTP-Server heruntergeladen und im Ordner `VIDEO` im jeweiligen Tagesordner gespeichert.

Für jeden Identifier wird im entsprechenden Tagesordner eine Datei `reference_video.csv` erstellt. Diese enthält die Informationen zu den einzelnen Zugdurchfahrten und kann um die Spalte `train_typ` ergänzt werden. In dieser Spalte wird der anhand der Videoaufnahmen bestimmte Zugtyp eingetragen.

Der Zugtyp wird für jede Zugdurchfahrt **manuell anhand der Videoaufnahmen bestimmt** und als Referenzinformation gespeichert. Dabei wird zwischen:

* `Lok`
* `Triebzug`

unterschieden.

Anschliessend werden die Informationen aus den Sensordaten mit den aus den Videos bestimmten Referenzdaten zusammengeführt. Daraus wird ein DataFrame erstellt und im Ordner `DataframeVideo` gespeichert. Dieser DataFrame enthält für jede Zugdurchfahrt sowohl die aus den Sensordaten berechneten Informationen als auch den zugehörigen Referenz-Zugtyp.

## 03_model_training

Sobald die Referenzdaten aus `DataframeVideo` und die entsprechenden CWT-Bilder aus `01_CWT_generation` vorhanden sind, werden beide Datensätze miteinander verknüpft. Dadurch erhält jedes CWT-Bild ein entsprechendes Klassenlabel (`Lok` oder `Triebzug`).

Die gelabelten Bilder werden anschliessend in Trainings-, Validierungs- und Testdaten aufgeteilt:

* **70 %** → Training
* **15 %** → Validierung
* **15 %** → Test

Die Aufteilung wird im Ordner `images/AI-train` gespeichert. Innerhalb der Ordner `train`, `val` und `test` werden die Bilder zusätzlich nach ihrer Klasse in die Unterordner `Lok` und `Triebzug` sortiert.

### Vorbereitung der Bilddaten

Mit `dataset.py` werden die Trainings-, Validierungs- und Testbilder für das **EfficientNet-B3-Modell** vorbereitet. Die Bilder werden transformiert und mit den für EfficientNet-B3 verwendeten Mittelwerten und Standardabweichungen normalisiert. Anschliessend werden sie als PyTorch-Datasets geladen und über `DataLoader` in Batches für das Training, die Validierung und den Test bereitgestellt.

### Training des Modells

Anschliessend wird das **EfficientNet-B3-Modell** mit den vorbereiteten Trainingsdaten trainiert.

Nach jeder Epoche wird die Leistung des Modells auf den Validierungsdaten überprüft. Das Modell mit der bisher besten **Validation Accuracy (`val_acc`)** wird gespeichert. Wird in einer späteren Epoche eine höhere `val_acc` erreicht, wird das zuvor gespeicherte Modell durch das neue Modell ersetzt.

Das beste trainierte Modell wird im Ordner `model` gespeichert:

```text
model/
└── efficientnet_b3_traintyp.pth
```

## 04_inference

Im letzten Schritt wird das zuvor trainierte **EfficientNet-B3-Modell** verwendet, um neue, bisher unbekannte CWT-Bilder zu klassifizieren.

Die zu klassifizierenden Bilder werden im Ordner `images/inference` abgelegt. Das trainierte Modell `efficientnet_b3_traintyp.pth` wird aus dem Ordner `model` geladen und anschliessend auf die neuen Bilder angewendet.

Für jedes Bild wird vorhergesagt, ob es sich um einen **Lok** oder einen **Triebzug** handelt. Die Klassifikationsergebnisse werden anschliessend zusammen mit den entsprechenden Informationen als CSV-Datei im Ordner `model` gespeichert:

```text
model/
├── efficientnet_b3_traintyp.pth
└── inference_results.csv
```
