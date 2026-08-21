# RailwAI

## Installation

Für die Installation und Ausführung des Projekts wird zunächst das GitHub-Repository lokal geklont und eine separate Conda-Umgebung eingerichtet. Anschliessend werden alle benötigten Python-Abhängigkeiten über die Datei `requirements.txt` installiert.

Die Daten für das Projekt **RailwAI** stammen aus zwei unterschiedlichen Quellen: dem **FTP-Server** und der **GeoVIS-API**. Der FTP-Server enthält die Rohdaten der Sensoren sowie, für bestimmte Projekte, die zugehörigen Videos. Über die GeoVIS-API können die verfügbaren Sensoren und deren Messdaten abgerufen werden.

```bash
cd C:/git
git clone https://github.com/TheoR14/RailwAI.git

conda create -n RailwAI python=3.11
conda activate RailwAI

cd C:/git/RailwAI
pip install -r requirements.txt
```

## FTP

Auf dem FTP-Server sind die Rohdaten der einzelnen Zugdurchfahrten für bestimmte Sensoren abgelegt. Für einige Projekte stehen zusätzlich Videos der Zugdurchfahrten zur Verfügung, die als Referenzdaten für die Bestimmung des Zugtyps verwendet werden.

* **`log.py`**
  Der Code enthält zwei funktionen `get_project()` und `get_project_video()`, die anhand des Dateinamens `file_pattern` erkennen, zu welchem Projekt die Datei gehört, und anschliessend die passenden FTP-Zugangsdaten und Verzeichnispfade zurückgeben.
  * `get_project()`: liefert die FTP-Zugangsdaten und den Pfad ür die ADTC-Rohdaten.
  * `get_project_video()`: liefert die FTP-Zugangsdaten und den Pfad für die Videoaufnahmen. Dabei wird zusätzlich das Datum aus dem Dateinamen extrahiert und für den Verzeichnispfad verwendet.

* **`data_download.py`**
  Die Funktion `downloader()` lädt die zum angegebenen `file_pattern` gehörenden Rohdaten vom FTP-Server herunter und speichert sie lokal im Ordner `RAW_DATA`.
  Zunächst werden über `get_project()` die FTP-Zugangsdaten und das entsprechende Verzeichnis abgerufen. Danach wird die Verbindung auf dem FTP-Server hergestellt und das Projektverzeichnis geöffnet. Lokal wird anschliessend ein Ordner unter `../RAW_DATA` für das jeweilige `file_pattern` erstellt. Die Dateien auf den FTP-Server, die das angagebene `file_pattern` enthalten werden heruntergeladen.

* **`data_decoder.py`**
  Die Funktion `decode()` dient dazu, die zuvor vom FTP-Server heruntergeladenen Rohdaten zu dekodieren und in CSV-Dateien umzuwandeln. Der Ordner mit den Rohdaten des jeweiligen `file_pattern` wird geöffnet und für die dekodierten Daten ein Ordner unter `../CSV_DATA` erstellt. Aus die Rohdaten werden anschliessend die Messfrequenz (Hz) und die Messdaten ausgelesen.
  Die Daten werden normalerweise mit einer Frequenz von etwa 1000 Hz gemessen, bei manchen Projekten kann die Frequenz jedoch auch bei etwa 4000 Hz liegen.
  Zum schluss werden die Zeit- und distanzwerte in einer CSV-Datei mit den Spalten `Time [s]`und `Distance[mm]` gespeichert. somit werden die codierte Rohdaten in ein einfach nutzbares Zeit-Distanz-Format umgewandelt.

* **`video_download.py`**
  Die Funktion `video_downloader()` dient dazu, die zum jeweiligen Datum gehörenden Videodateien vom FTP-Server herunterzuladen. Zunächst werden über `get_project_video()` die FTP-Zugangsdaten und das videoverzeichnis abgerufen. Das Datum wird dabei aus dem `file_pattern` ausgelesen und für die Bennenung des Speicherordners verwendet.
  Anschliessend wird eine Verbindung zum FTP-Server hergestellt und das entsprechenden Verzeichnis geöffnet. Lokal wird unter `../VIDEO/{datum}` ein Ordner erstellt. Alle Dateien werden heruntergeladen und im lokalen Ordner gespeichert.

## GeoVIS

Über die **GeoVIS-API** können die Messdaten aller Sensoren abgerufen werden. Diese Daten sind bereits vorverarbeitet und enthalten hauptsächlich die relevanten Peaks der Sensorsignale. Sie werden verwendet, um die Geschwindigkeit der einzelnen Achsen zwischen aufeinanderfolgenden Sensorpaaren zu berechnen. Zusätzlich werden die Anzahl der Achsen sowie die mittlere Zuggeschwindigkeit im DataFrame `dfs_raw` gespeichert.

* **`DTC.env`**
  Enthält die Zugangsdaten für den Zugriff auf die GeoVIS-API. Diese Datei darf aus Sicherheitsgründen nicht auf GitHub veröffentlicht werden.
  `DTC.env` muss im Ordner `GeoVis` liegen und soll so aussehen:
  ```
  GEOVIS_LOGIN='max.muster@email.ch'
  GEOVIS_PASSWORD='password!'
  ```

* **`Geschwindigkeit.py`**
  Die Funktion `calc_speed()` berechnet die Geschwindigkeit eines Zuges anhand der erkannten Peaks der einzelnen Sensoren. Für jeden Zeitstempel werden die vorhandenen PEak-Daten überprüft und die Sensoren sowie ihre jeweiligen Messzeitpunkte ausgelesen. Anhand der Anzahl der Peaks wird dabei die Anzahl der erkannten Achsen bestimmt.
  Die Sensoren werden anschliessend paarweise zusammengefasst. Wenn beide Sensoren eines Paares gültige Messungen besitzen, wird für jede Achse der Mittlere Zeitpunkt zwischen den beiden Sensoren bestimmt. Zwischen den aufeinanderfolgenden Sensorpaaren wird aus dem bekannten Distanz und der Zeitdifferenz die *Geschwindigkeit pro Achse* berechnet. Dadurch wird die Geschwindigkeit für jede einzelne Achse separat bestimmt. Dies ist wichtig, da sich die Geschwindigkeit eines Zuges während der Messung verändern kann (wenn der Zug bremst oder beschleunigt). Durch die achsweise Geschwindigkeitsberechnung können diese Geschwindigkeitsänderungen berücksichtigt und  bei der weiteren Auswertung reduziert werden.
  Fehlende Geschwindigkeitswerte zwischen Sensorpaaren werden interpoliert.

### API

* **`ADTC_Analyze_FHNW.py`**
  Stellt die Verbindung zur GEOvis4.0-REST-API her und ermöglicht den Zugriff auf Projekte, Sensoren und deren Messdaten. Der Code wurde von Amberg zur Verfügung gestellt.
  Für das Projekt sind hier nur die drei funktionen `login()`, `getSensorsNames()` und `getSesnorsData()` relevant.

  * *`login()`*
  Die Funktion `login()` dient zur Autentifizierung bei der GEOvis4.0 REST-API. Sie erhält die Zugangsdaten als `login_data` und sendet diese mit einer `POST`-Anfrage an den Login-Endpunkt der API.

  * *`getSensorsNames()`*
  Die Funktion `getSensorsNames()` wird verwendet, u die Sensoren eines bestimmten GEOvis-Projektss abzurufen. Defür benötigt sie den zuvor erzeugten Login, die `projectID` und einen `filter`, mit dem die anfrage genauer definiert werden kann. Die Funkktion sendet diese Informationen an die GEOvis-API und gibt die zurückgegebenen Sensordaten als Python-Datenstruktur zurück.

  * *`getSensorsData()`*
  Die Funktion `getSensorsData()` dient zum Abrufen der Messdaten der Sensoren eines bestimmten Projekts. Auch hier werden der Login, die `projektID` und ein `filter` an die API übergeben. Die API liefert daraufhin die entsprechenden Sensormessdaten zurück, welche von der Funktion als Python-Datenstruktur zurückgegeben werden.

* **`Datenbezug_API.py`**
  Die Funktion `get_dfs_raw()` dient dazu, die Sensordaten für einen bestimmten Zeitraum über die GEOvis4.0-API abzurufen und für die weitere Verarbeitung aufzubereiten.

  Mit der `login()` Funktion von `ADTC_Analyze_FHNW.py` wird eine Verbindung zur API authentifiziert. Anschliessend wir dmit `getSensorsNames()` nach den gewünschten Sensoren gesucht. Dabei wird über den Filter festgelegt, dass nur **Distanzsensoren** mit der Datenbank-ID, dem gewünschten Sensornamen und der Einheit **mm** berücksichtigt werden.

  ```
  sensor_filter = {
        "DatabaseId": projekt_db,         # Datenbank-ID
        "NameSearch": sensor_name,
        "SensorType": 13,                 # Distance
        "RequestedValueTimeFormat": 1,
        "Unit": 2,                        # mm
        "SensorState": 0,
    }
  ```

  Für jeden gefundenen Sensor werden mit `getSensorsData()` die Messdaten innerhalb des angegebenen Zeitraums zwischen `startdatum` und `enddatum` abgerufen. Aus den zurückgegebenen Daten werden jeweils der Zeitpunkt, der Messwert und die Sensor-ID extrahiert und in einer List gesammelt. Die Messungen werden anhand von Zeitlücken vin mehr als einer Minute in einzelne Gruppen interteilt. Dadurch können die einzelnen Zugdruchfahrten voneinander getrennt werden.

  Die einzelne Gruppen werden danach in einem Dictionary `dfs_raw` gespeichert.

### Preprocessing

* **`Peak_Detektion.py`**
  Die Funktion `detect_peaks()` dient dazu, in den zuvor abgerufenen Sensordaten charakteristische PEaks der Distanzmessungen zu erkennen. Jeder Sensor wird separat analysiert und mithilfe von `find_peaks()` werden die relevanten ausschläge identifiziert.
  Die erkannten Peaks werden anschliessend im Directory `dfs_raw` unter dem Eintrag `"Peaks"` gepseichert. Diese Peak-Zeitpunkte dienen später als Grundlage für die Achsenerkennung und Geschwindigkeitsberechnung.

# Code

## 01_CWT_generation

Der Code `01_CWT_generation.ipynb` bildet die erste Stufe der Datenverarbeitung. Ausgangspunkt ist jeweils ein `filename`, der einem bestimmten Sensor, einem Projekt und einem bestimmten Datum entspricht.

### 1.1 FTP-Server Zugriff und Rohdaten

Zu Beginn werden anhand `filename` die zugehörigen Rohdaten vom FTP-Server heruntergeladen. Dazu wird die Funktion `downloader()` aus `data_download.py` verwendet.
Die heruntergeladenen Dateien werden im Ordner `RAW_DATA` gespeichert.

Anschliessend werden die Rohdaten mit der Funktion `decoder()` aus `data_decoder.py` dekodiert und in ein lesbares CSV-Format umgewandelt. Die resultierenden Dateien werden im Ordner `CSV_DATA` gespeichert.

### 1.2 GeoVIS-API Zugriff auf die Messdaten

Parallel dazu werden die Messdaten des entsprechenden Sensors über die GeoVIS-API abgerufen. Auch hier dient der `filename` als Grundlage für die Auswahl des entsprechenden Sensors und Zeitraums. 

Die Funktion `main()` aus `utils.py` ruft dabei schrittweise die verschiedenen Verarbeitungsschritte auf:
```
main() -> get_dfs_raw() -> detect_peaks -> calc_speed()
```

Mit `get_dfs_raw()` werden zunächst die Messdaten der entsprechenden Sensoren über die GeoVIS-API abgerufen und in einer geeigneten Datenstruktur gespeichert.
Anschliessend werden mit `detect_peaks()` die charakteristischen Peaks und Sensorsignale bestimmt. Jeder dieser Peaks entspricht dem Überfahren des Sensors durch eine Achse des Zuges.

Mit `calc_speed()` wird anschliessend die Geschwindigkeit für jede einzelne Achse bestimmt. die Berechnung der Geschwindigkeit pro Achse ermöglicht es, änderungen der Geschwindigkeit während der Zugdurchfahrt (Bremsen oder Beschleunigen) zu berücksichtigen und deren Einfluss zu reduzieren.

Aus der Geschwindigkeit einer Achse und der Zeitdifferenz zwischen aufeinanderefolgenden Achsen kann anschliessend deren Abstand berechnet werden:
```
d = v * Δt
```
Durch die Summierung der Abstände zwischen den einzelnen Achsen kann schliesslich die Gesamtlänge des zuges bestimmt werden.

### 1.3 Kombination von FTP- und API-Daten

Nachdem die Daten von beiden Quellen verarbeitet wurden, werden die Informationen des FTP-Servers und der GeoVIS-API miteinander kombiniert.

Die aus dem FTP-Server erzeugten CSV-Dateien enthalten das vollständige Sensorsignal. Für die weitere Verarbeitung werden diese zunächst auf den tatsächlischen Zeitraum der Zugdurchfahrt reduziert. Dabei wird der Bereich vom ersten erkannten Peak (erste Achse) bis zum letzten erkannten Peak (letzte Achse) ausgeschnitten.

Die gekürzten Dateien werden ebenfalls im Ordner `CSV_DATA` gespeichert und erhalten die Endung *_cut.csv*.

Anschliessend werden die zuvor über die GeoVIS-API berechneten Zuglängen in die gekürzten CSV-Dateien integriert.
Die Zeitpunkt der erkannten Achsen werden anschliessend relativ zum ersten peak dargestellt.

Parallel dazu wird aus den einzelnen Achsenabstände eine kumulative Zuglänge berechnet.

Da zwischen den erkannten Achsen kontinuerliche Werte benötigt werden, wird die Zuglänge anschliessend auf die Zeitpunkte der CSV-Daten interpoliert. Dadurch errhält jeder Messpunkt des CSV-sigmal eine entsprechende Position entrlang des Zuges in Metern. Die resultierenden Dateien enthalten somit nebem der ursprünglichen Zeit- und Messwertinformation zusätzliche die Spalte `Length [m]`.

**Standardisierung der Zuglänge**

Damit die verschiedenen Zugdurchfahrten später miteinander verglichen können , werden die CSV-DAteien anschliessen auf eine einheitliche Länge standardisiert.

Die Dateien werden bis zu einer maximalen Zuglänge von 400 m erweitert. Dadurch besitzen all Datensätze dieselbe räumliche Ausdehnung, unabhängig davon, ob der tatsächliche Zug 50 m, 100 m oder 300 m lang ist.

Die erweiterten Dateien werden mit der Endung *_ext.csv* gespeichert.

### 1.4 Generierung der CWT-Bilder

Nach der räumlichen Standardisierung können die CSV-DAten als **Continuous Wavelet Transform (CWT)** dargestelt werden.

Die CWT ermöglichen es, die im Sensorsignal enthaltenen FRequenzanteil in Abhängigkeit von der Zeit darzustellen. Dadurch ensteht eine 2D Bild, in dem die Signalstruktur des Zuges sichtbar wird.

Die CWT wird auf Basis der erweitertent CSV-Dateien erzeugt. Die horizontale Achse entspicht dabei der Zuglänge, während die vertikale Achse die untersuchten Frequenzen darstellt.

Für die Darstellung des gesamten Zuges wird eine Frequenzbereich von 0.2 - 5 Hz verwendet. Die erzeugten Bilder werden im Ordner `'images/total_length'` gespeichert.

**CWT der ersten Wagens bzw. der ersten Lokomotive**

Zusätzliche zu Darstellung des gesamten Zuges wurd der erste Wagen separat betrachtet.

Dazu wird das CSV-Sigmal anhand der ersten vier erkannten Peaks gekürzt. Da die ersten vier Peaks den Achsen des ersten Wagens entsprechen, kann der entsprechende Abschnitt des Zuges isoliert werden.

Diese gekürzten Dateien werden mit der Endung *_lok.csv* gespeichert.

Auf Basis dieser Dateien wird ebenfalls eine CWT erzeugt. Für diese Darstellung wird ein grösser Frequenzbereich von 0.2 - 15 Hz verwendet. Die resultierenden Bilder werden im Ordner `'images/lok'` gespeichert.

**Kombination der CWT-Bilder**

Zum Schluss werden die beiden zuvor erzeugten CWT-Darstellungen zu einem RGB-Bild kombiniert. Dabei werden die Informationen auf die drei Farbkanäle verteilt:
- Rot: CWT der gesamten Zug (max. 400 m)
- Grün: CWT der ersten Wagen/Lok (max. 50 m)
- Blau: nicht verwendet (bleibt leer)

Diese Kombination ermöglicht es beide Informationen in einem einzigen Bild darzustellen. Die resultierenden RGB-bilder werden im Ordner `'images/combined'` gespeichert.

## 02_video_reference_data

Der Code `02_video_reference_data.ipynb` dient dazu, die verfügbaren Videos den entsprechenden Zugdurchfahrten zuzuordnen und daraus Refernzdaten für das Training des KI-Modells zu erstellen.

### 2.1 Videos herunterladen

Wie bereits bei Code `01_CWT_generation.ipynb` wird der `filename` verwendet, um das entsprechende Projekt und Datum zu bestimmen.

Die Videos werden mit der Funktion `video_downloader()` aus `video_download.py` vom FTP-Server heruntergeladen. sie werden im Ordner `VIDEO` gespeichert, in einem Unterordner abgelegt, der dem jeweiligen Datum entspricht.

### 2.1 Videos den Zugdurchfahrten zuordnen

Die Kamera wird durch eine Bewegung innerhalb ihres Sichtfeldes aufgelöst. Dadurch wwerden nicht nur Züge aufgenommen, die auf dem Gleis mit den installierten Sensoren fahren, sondern auch Züge, die auf dem benachbarten Gleis in der entgegengesetzen Richtung fahren.

Aus diesme Grund enthält der Download mehr Videos als tatsächliche Zugdurchfahrten auf dem Sensoren vorhanden sind.

Um nur die relevanten Videos zu behalten, werden die Zeitstempel der in Code `01_CWT_generation.ipynb` erkannten Zugdurchfahrten verglichen. Dadurch können die videos den entsprechenden Sensor-durchfahrten zugeordnet werden. 

Videos, die zeitlich keiner Zugdurchfahrt auf dem èberwachten Gleis entsprechen, werden entfernt. Dadurch verbleiben nur die Videos, die zu den von den Sensoren erfassten Zügen gehören.

### 2.3 Manuelle Klassifikation der Zugtypen

Für die verbleibenden Videos wird anschliessend eine CSv-Datei erstellt, welche die Namen der vorhandenen Videos enthält.

Die videos werden danach manuell betrachtet und klassifiziert. Dabei wird zwischen den beiden für das Prpjekt relevante Zugtypen unterschieden:
- Triebzug
- Lokzug

Diese manuell bestimmten Klassen dienen als Referenzdaten für die spätere Training des KI-Modells.

### 2.4 Zusammenführung der Video- und Sensordaten

Nachdem jedem Video ein Zugtyp zugewiesen wurde, wird die erzeugte CSV-Datei mit den entsprechenden Sensordaten aus Code `01_CWT_generation.ipynb` zusammengeführt.

Dadurch entsreht ein neuer DataFrame. der neben den Messdaten der Zugdurchfahrt zusätzlich den manuell bestimmten Zugtyp enthält.

Der resultierende DataFrame wird für jedes Datum als CSV-Datei gespeichert `'DataframeVideo/df_video_merged_{datum}.csv'`

## 03_model_training

### 3.1 Datenaufteilung

Sobald die Referenzdaten aus `DataframeVideo` und die entsprechenden kombinierte CWT-Bilder aus `01_CWT_generation.ipynb` vorhanden sind, werden beide Datensätze miteinander verknüpft. Dadurch erhält jedes CWT-Bild ein entsprechendes Klassenlabel (`Lok` oder `Trieb`).

Die gelabelten Bilder werden anschliessend in Trainings-, Validierungs- und Testdaten aufgeteilt:

* **70 %** -> Training
* **15 %** -> Validierung
* **15 %** -> Test

Die Aufteilung wird im Ordner `images/AI-train` gespeichert. Innerhalb der Ordner `train`, `val` und `test` werden die Bilder zusätzlich nach ihrer Klasse in die Unterordner `Lok` und `Trieb` sortiert.

### 3.2 Vorbereitung der Bilddaten

Die CWT-Bilder werden zunächst in Trainings-, Validierungs-, und Testdaten aufgeteilt. Anschliessned werden die drei Datensätze mithilfe der in `dataset.py` definierten Klasse `CustomImageDataset` als PyTorch-Datasets geladen. `CustomImageDataset` durchsucht dabei die jeweiligen Unterordner nach den vorhandenen Klassen und weisst den Bildern automatisch die entsprechenden Klassenlabels zu. Die Bilder werde anschliessend in Tensoren umgewandelt und mit den für **EfficientNet-B3** verwendeten Mittelwerten und Standardabweichungen normalisiert. Über `DataLoader` werden die Trainings-, Validierungs- und Testdaten schliesslich in Batches für das Training bzw. die Evaluation bereitgestellt.

### 3.3 Training des Modells

Anschliessend wird das **EfficientNet-B3-Modell** mit den vorbereiteten Trainingsdaten trainiert.

Nach jeder Epoche wird die Leistung des Modells auf den Validierungsdaten überprüft. Das Modell mit der bisher besten **Validation Accuracy (`val_acc`)** wird gespeichert. Wird in einer späteren Epoche eine höhere `val_acc` erreicht, wird das zuvor gespeicherte Modell durch das neue Modell ersetzt.

Das beste trainierte Modell wird im Ordner `model` gespeichert:

```text
model/
└── efficientnet_b3_traintyp.pth
```

### 3.4 Evaluation des trainierten Modells

Das trainierte **EfficientNet-B3-Modell** wird zunächst geladen und in den Evaluaitonsmodus versetzt. anschliessend wird es auf den zuvor zurückgehaltenen Testdaten angewendet. Für jedes Bild wird die vorergesagt Klasse sowie deren Wahrscheinlichkeit bestimmt.

Die Vorhersagen werden anschliessend mit den tatsächlichen Labels verglichen. Daraus werden die Test Accuracy un der F1-Score berechnet. Zusätzliche wird eine Konfusionsmatricx erstellt, welche die anzahl der korrekten und fehlerhaften Klassifikationen pro Klasse darstellt.

## 04_inference

Im letzten Schritt wird das zuvor trainierte **EfficientNet-B3-Modell** verwendet, um neue, bisher unbekannte CWT-Bilder zu klassifizieren.

Die zu klassifizierenden Bilder werden im Ordner `images/inference` abgelegt. Das trainierte Modell `efficientnet_b3_traintyp.pth` wird aus dem Ordner `model` geladen und anschliessend auf die neuen Bilder angewendet.

Für jedes Bild wird vorhergesagt, ob es sich um einen **Lok** oder einen **Trieb** handelt. Die Klassifikationsergebnisse werden anschliessend zusammen mit den entsprechenden Informationen als CSV-Datei im Ordner `model` gespeichert:

```text
model/
├── efficientnet_b3_traintyp.pth
└── inference_results.csv
```
