import pandas as pd
from scipy.signal import find_peaks


def detect_peaks(dfs_raw, min_peak_height=-0.3, min_signal_value=-5, verbose=False):
    """
    Ergaenzt pro Timestamp-Eintrag in dfs_raw ein Feld "Peaks".

    Erwartete Struktur:
    dfs_raw[timestamp] = {"Data": DataFrame mit Spalten [Time, Value, Sensor], ...}

    min_peak_height kann positiv oder negativ uebergeben werden.
    Beispiel: -0.3 und 0.3 werden gleich behandelt.

    Rueckgabe:
    - dfs_raw (gleiches Dict-Objekt, um "Peaks" erweitert)
    """
    peak_threshold = abs(float(min_peak_height))

    for key, val in dfs_raw.items():
        if "Data" not in val:
            if verbose:
                print(f"Key={key}: kein 'Data' vorhanden")
            val["Peaks"] = pd.DataFrame()
            continue

        werte = val["Data"].copy()

        if werte.empty or "Sensor" not in werte.columns or "Value" not in werte.columns:
            if verbose:
                print(f"Key={key}: keine verwertbaren Daten vorhanden")
            val["Peaks"] = werte.iloc[0:0].copy()
            continue

        keep_indices = []
        for sensor, df_sensor in werte.groupby("Sensor"):
            signal = df_sensor["Value"].astype(float).to_numpy()
            sample_idx = df_sensor.index.to_numpy()

            if len(signal) < 3:
                continue

            peak_idx, _ = find_peaks(-signal, height=(peak_threshold, None))
            peak_idx = peak_idx[signal[peak_idx] >= min_signal_value]

            if len(peak_idx) > 0:
                keep_indices.extend(sample_idx[peak_idx].tolist())

            if verbose:
                print(f"Key={key} | Sensor={sensor} | Peaks={len(peak_idx)}")

        if keep_indices:
            keep_indices = sorted(set(keep_indices))
            val["Peaks"] = werte.loc[keep_indices].copy()
        else:
            val["Peaks"] = werte.iloc[0:0].copy()

    print('Peak Detektion abgeschlossen.')

    return dfs_raw