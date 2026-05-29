import numpy as np
import pandas as pd

def calc_speed(dfs_raw, anzahl_sensoren, DISTANZ_BASIS_M=4.8):
    """
    Berechnet die Geschwindigkeit pro Achse und Sensor basierend auf Peak-Zeitpunkten.

    Parameter
    ----------
    dfs_raw : dict
        Dictionary mit Zeitstempeln als Keys und Messdaten (inkl. Peaks) als Values.
    
    anzahl_sensoren : int
        Gesamtanzahl der Sensoren im System. Bestimmt die feste Paarbildung (1,2), (3,4), ...

    DISTANZ_BASIS_M : float, optional (default=4.8)
        Basisabstand zwischen zwei direkt benachbarten Sensorpaaren in Metern.

    Returns
    -------
    None
        Die Funktion ergänzt dfs_raw direkt um folgende Einträge:
        
        - geschw_pro_achse_sensor_local : dict
            Geschwindigkeit pro Achse für jeden Sensor
        
        - sensorpaar_name_mapping : dict
            Mapping von Sensorpaaren zu ursprünglichen Sensornamen
        
        - Anzahl_Achsen : int
            Anzahl erkannter Achsen
        
        - mittel_Geschw_zug : float
            Mittlere Geschwindigkeit über alle Sensoren und Achsen
    """

    for ts, content in dfs_raw.items():
        # print(f"\n--- Timestamp: {ts} ---")

        if "Peaks" not in content or content["Peaks"] is None or content["Peaks"].empty:
            print(f"{ts} -> uebersprungen: keine Peaks")
            continue

        df_ts = content["Peaks"].copy()

        if "Sensor" not in df_ts.columns or "Time" not in df_ts.columns:
            print(f"{ts} -> uebersprungen: Spalten Sensor/Time fehlen")
            continue

        df_ts["Sensor_raw"] = df_ts["Sensor"].astype(str)

        try:
            df_ts["Sensor"] = (
                df_ts["Sensor_raw"]
                .str.split("_")
                .str[-2]
                .astype(int)
            )
        except Exception as e:
            print(f"{ts} -> uebersprungen: Sensor-Parsing fehlgeschlagen: {e}")
            continue

        sensor_id_to_name = (
            df_ts[["Sensor", "Sensor_raw"]]
            .drop_duplicates()
            .groupby("Sensor")["Sensor_raw"]
            .first()
            .to_dict()
        )

        df_ts["Time"] = pd.to_datetime(df_ts["Time"], errors="coerce")
        df_ts = df_ts.dropna(subset=["Time"]).copy()

        if df_ts.empty:
            print(f"{ts} -> uebersprungen: keine gueltigen Zeiten")
            continue

        sensor_counts = df_ts.groupby("Sensor").size().sort_index()
        # print("Peaks pro Sensor:")
        # print(sensor_counts)

        if sensor_counts.empty:
            print(f"{ts} -> uebersprungen: keine Sensorzaehlungen")
            continue

        anzahl_achsen = int(round(float(sensor_counts.median())))
        # print(f"Bestimmte Achsenzahl (Median): {anzahl_achsen}")

        if anzahl_achsen < 4:
            print(f"{ts} -> uebersprungen: anzahl_achsen < 4")
            continue

        valid_sensors = sensor_counts[sensor_counts == anzahl_achsen].index.tolist()
        # print(f"Vollstaendige Sensoren: {valid_sensors}")

        achsenzeiten_sensor = {}
        for sensor_id in valid_sensors:
            df_sensor = (
                df_ts[df_ts["Sensor"] == sensor_id]
                .sort_values("Time")
                .reset_index(drop=True)
            )
            achsenzeiten_sensor[sensor_id] = df_sensor["Time"].tolist()

        if len(sensor_counts.index.tolist()) < 2:
            content["geschw_pro_achse_sensor_local"] = {}
            content["sensorpaar_name_mapping"] = {}
            content["Anzahl_Achsen"] = anzahl_achsen
            content["mittel_Geschw_zug"] = np.nan
            continue

        # feste Paarlogik basierend auf anzahl_sensoren
        pair_list = [(i, i + 1) for i in range(1, anzahl_sensoren, 2)]
        # print(f"Moegliche Sensorgruppen: {pair_list}")

        pair_times = {}
        pair_state = {}

        for pair_idx, (s1, s2) in enumerate(pair_list, start=1):

            if s1 not in achsenzeiten_sensor and s2 not in achsenzeiten_sensor:
                pair_times[pair_idx] = None
                pair_state[pair_idx] = "invalid"
                continue

            t1 = (
                pd.Series(achsenzeiten_sensor[s1]).reset_index(drop=True)
                if s1 in achsenzeiten_sensor else pd.Series(dtype="datetime64[ns]")
            )
            t2 = (
                pd.Series(achsenzeiten_sensor[s2]).reset_index(drop=True)
                if s2 in achsenzeiten_sensor else pd.Series(dtype="datetime64[ns]")
            )

            len1_ok = len(t1) == anzahl_achsen
            len2_ok = len(t2) == anzahl_achsen

            if len1_ok and len2_ok:
                t_mean = t1 + (t2 - t1) / 2
                pair_times[pair_idx] = t_mean.reset_index(drop=True)
                pair_state[pair_idx] = "both_true_equal"

            elif len1_ok:
                pair_times[pair_idx] = t1.reset_index(drop=True)
                pair_state[pair_idx] = "left_only"

            elif len2_ok:
                pair_times[pair_idx] = t2.reset_index(drop=True)
                pair_state[pair_idx] = "right_only"

            else:
                pair_times[pair_idx] = None
                pair_state[pair_idx] = "invalid"

        valid_pairs = [idx for idx in sorted(pair_times.keys()) if pair_times[idx] is not None]

        geschw_matrix_pairs = []
        transition_midpoints = []

        for prev_pair, curr_pair in zip(valid_pairs[:-1], valid_pairs[1:]):
            prev_times = pair_times[prev_pair]
            curr_times = pair_times[curr_pair]

            pair_gap = curr_pair - prev_pair
            dist = DISTANZ_BASIS_M * pair_gap

            geschw_achsen = []
            for i in range(anzahl_achsen):
                dt = (curr_times.iloc[i] - prev_times.iloc[i]).total_seconds()
                v = float(dist / abs(dt)) if dt != 0 else np.nan
                geschw_achsen.append(v)

            geschw_matrix_pairs.append(geschw_achsen)
            transition_midpoints.append((prev_pair + curr_pair) / 2.0)

        pair_positions = np.arange(1, len(pair_list) + 1, dtype=float)
        pair_speed_raw = np.full((len(pair_positions), anzahl_achsen), np.nan)

        if len(geschw_matrix_pairs) > 0:
            transition_midpoints = np.array(transition_midpoints)
            transition_array = np.array(geschw_matrix_pairs)

            for achse_idx in range(anzahl_achsen):
                y = transition_array[:, achse_idx]

                finite_mask = np.isfinite(y)
                x_valid = transition_midpoints[finite_mask]
                y_valid = y[finite_mask]

                if len(y_valid) == 0:
                    continue
                elif len(y_valid) == 1:
                    pair_speed_raw[:, achse_idx] = y_valid[0]
                else:
                    pair_speed_raw[:, achse_idx] = np.interp(
                        pair_positions, x_valid, y_valid,
                        left=np.nan, right=np.nan
                    )

        pair_speed_interp = pair_speed_raw.copy()

        for achse_idx in range(anzahl_achsen):
            col = pair_speed_interp[:, achse_idx]
            finite_mask = np.isfinite(col)

            if finite_mask.sum() == 0:
                continue
            elif finite_mask.sum() == 1:
                col[:] = col[finite_mask][0]
            else:
                x_valid = pair_positions[finite_mask]
                y_valid = col[finite_mask]

                col[:] = np.interp(pair_positions, x_valid, y_valid)

                left_mask = pair_positions < x_valid[0]
                if np.any(left_mask):
                    x1, x2 = x_valid[0], x_valid[1]
                    y1, y2 = y_valid[0], y_valid[1]
                    m = (y2 - y1) / (x2 - x1)
                    col[left_mask] = y1 + m * (pair_positions[left_mask] - x1)

                right_mask = pair_positions > x_valid[-1]
                if np.any(right_mask):
                    x1, x2 = x_valid[-2], x_valid[-1]
                    y1, y2 = y_valid[-2], y_valid[-1]
                    m = (y2 - y1) / (x2 - x1)
                    col[right_mask] = y2 + m * (pair_positions[right_mask] - x2)

            pair_speed_interp[:, achse_idx] = col

        pair_idx_to_tuple = {idx: pair for idx, pair in enumerate(pair_list, start=1)}
        geschw_pro_achse_pair_interp = {}

        for row_idx, pair_idx in enumerate(range(1, len(pair_list) + 1)):
            pair_tuple = pair_idx_to_tuple[pair_idx]
            geschw_pro_achse_pair_interp[pair_tuple] = pair_speed_interp[row_idx, :].tolist()

        geschw_pro_achse_sensor_local = {}

        for pair_tuple, v_list in geschw_pro_achse_pair_interp.items():
            s1, s2 = pair_tuple
            geschw_pro_achse_sensor_local[s1] = list(v_list)
            geschw_pro_achse_sensor_local[s2] = list(v_list)

        all_local_speeds = [
            v for v_list in geschw_pro_achse_sensor_local.values()
            for v in v_list if pd.notna(v)
        ]
        mittel_Geschw_zug = float(np.mean(all_local_speeds)) if all_local_speeds else np.nan

        sensorpaar_name_mapping = {
            pair: (
                sensor_id_to_name.get(pair[0], f"Sensor_{pair[0]}"),
                sensor_id_to_name.get(pair[1], f"Sensor_{pair[1]}")
            )
            for pair in pair_list
        }

        content["geschw_pro_achse_sensor_local"] = geschw_pro_achse_sensor_local
        content["sensorpaar_name_mapping"] = sensorpaar_name_mapping
        content["Anzahl_Achsen"] = anzahl_achsen
        content["mittel_Geschw_zug"] = mittel_Geschw_zug

        # print("\nUebersicht geschw_pro_achse_sensor_local:")
        # print(f"  Anzahl Schluessel: {len(geschw_pro_achse_sensor_local)}")
        # for sensor_id, v_list in geschw_pro_achse_sensor_local.items():
        #     print(f"  Sensor {sensor_id}: {len(v_list)} Werte")

    print("Lokale Paar- und Sensorgeschwindigkeiten gespeichert.")
    return dfs_raw