# RailwAI

RailwAI ist ein Forschungsprojekt, in dem der Untergrund klassifiziert wird, und verschiedene Zugtypen identifiziert werden.

Die Erkennung basiert auf Messungen der Gleisauslenkung, die mit Beschleunigungssensoren erfasst wurden und in Continuous Wavelet umgewandelt werden, um in einem Deep-Learning-Algorithmus verwendet werden zu können.

Der Code dieses Projekts ist in mehrere Notebooks unterteilt:
## 01) Feature Engineering
### Auslenkungsdaten herunterladen
Die Auslenkungsdaten liegen auf einem FTP-Server in .dat-Dateien und müssen in .csv-Dateien umgewandelt werden.

In der .dat-Dateien ist die Messfrequenz des Sensors definiert (oft ca. 1 kHz oder ca. 4 kHz).

Die resultierende .csv-Dateien beinhalten zwei spalten:
- Time [s]
- Distance[mm]
### DataFrame generieren und kombinieren
Aus alle .csv-Dateien wird ein DataFrame (`df_raw`) generiert, das den Stammname jeder Datei (`file`) und der Zeitstempel (`timestamp_raw`) im Format *YYYY-MM-DD HH:MM:SS.SSS* beinhaltet.

Anhand Code XXX kann auf der GeoVis-Platform zugegriefen werden und die zeitsynchrone Peaks (`_Peak`) ausgelesen werden. Damit ist es nun möglich einen Dictionary (`dfs_raw_3`) zu generieren, das XXX beinhaltet.

Darauf basierend ist es möglich einen neuen DataFrame zu generieren (`df_passage_time`), das der Zeitstempel (`timestamp`), sowie einer Liste der Zeitstempel für jeder Sensor für einem Zugdurchfahrt (`timestamp_serie`) und einer Liste aller Zeitintervale zwischen jeder Radachse (`delta_t`).

Anhand diese Daten ist es nun möglich, die Gechwindigkeit für jeder Achsendurchfahrt über den Sensor in einer Liste zu ermitteln. Dieser Geschwindigkeit wird nun in einer DataFrame (`df_vel2`) als `v` gespeichert mit der Zugdurchfahrtszeit `timestamp`.

Nun ist es jetzt möglich einen neuen DaataFrame zu generieren indem man zwei DataFrame kombiniert anhand ihren Zeitstempel. Die zwei DataFrames sind:
- `df_passage_time`
- `df_vel2`
Der neuer DataFrame heisst nun `df_axes_merged`, inden weitere Attribute berechnet werden. Die Distanz zwischen der verschiedene Radachsen kann mittels {v=d/t}; {d=v*t} als `length` ermittelt werden und die gesamte Zuglänge (`total_length`) als der Summe alle Distanzen für einem Zugdurchfahrt erzeugt werden.

Das DataFrame `df_axes_merged` mit seinen neuen Attribute kann mit der DataFrame `df_raw` kombiniert werden, indem man beide anhand ihren Zeitstempel kombiniert. Es gibt nun zwischen der gelesene zeit in den Rohdaten (FTP-Server) und die zeitsynchronisierte Peaksdaten auf GeoVis einen Zeitunterschied von ca. 10 Sekunden, da die Messungen ca. 10 Sekunden vor den Zugdurchfahrt automatische gestartet werden, und die Peaksdataein verweisen direkt auf der Zeit der erste Achsendurchfahrt. Dafür wurde eine Toleranz von 20 Sekunden beim kombinieren eingeführt. Das resultierende DataFrame heisst `df_merged`.

Nacher werden die .csv-Datein bereinigt, indem die 10 Sekunden vor und nach den Zugdurchfahrt bereinigt wurden. Dafür wird das erste und letzte Achsendurchfahrt detektieren und alles davor und danach gelöscht. Der ersten Achsendurchfahrtzeit nachdem der Sensor angefangen zu messen hat ist in der DataFrame `df_merged` als `first_peak_raw` bezeichnet.
### CSV auf 400 m strecken
In der .csv-Dateien wird nun eine neue Spalte hinzugefügt `Length [m]`. Es ist damit nun möglich die .csv-Dateien auf eine gezielte Länge zu vergrössern (ca. 400 m), indem alle Auslenkungen = 0, die Länge bis 400 m extrapoliert wird, sowie die Zeit.
### CWT generieren
Nachdem alle .csv-Dateien die gleiche *Länge* haben, ist es nun möglcih auf der Länge standardizierte Continuous Wavelet Transform aus der Attribute `Time [s]` und `Distance[mm]` zu generieren.
