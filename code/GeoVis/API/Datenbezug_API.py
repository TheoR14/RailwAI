import pandas as pd
from GeoVis.API.ADTC_Analyze_FHNW import getSensorsData, getSensorsNames, login


def get_dfs_raw(
    login_data,
    project_id,
    projekt_db,
    startdatum,
    enddatum,
    sensor_name,
):
    header = login(login_data)

    sensor_filter = {
        "DatabaseId": projekt_db,
        "NameSearch": sensor_name,
        "SensorType": 13,  # Distance
        "RequestedValueTimeFormat": 1,
        "Unit": 2,  # mm
        "SensorState": 0,
    }
    sensors = getSensorsNames(header, project_id, sensor_filter)
    sensor_full_ids = [list(full_id.values())[0] for full_id in sensors.get("Data", [])]
    anzahl_sensoren = len(sensor_full_ids)

    if anzahl_sensoren == 0:
        return {}, 0

    rows = []
    for sensor in sensor_full_ids:
        payload = {
            "SensorsFullIds": [sensor],
            "StartDate": startdatum.isoformat(),
            "EndDate": enddatum.isoformat(),
            "RequestedValueTime": 1,
            "RequestedValueTimeFormat": 1,
            "GetLastData": True,
            "RequestedValues": [1],
        }

        resp = getSensorsData(header, project_id, payload)
        for sensor_block in resp.get("Data", []):
            sensor_id = sensor_block.get("SensorFullId")
            for entry in sensor_block.get("Data", []):
                values = entry.get("Values", [])
                if not values:
                    continue
                rows.append(
                    {
                        "Time": entry.get("Timeslot"),
                        "Value": values[0],
                        "Sensor": sensor_id,
                    }
                )

    if not rows:
        return {}, anzahl_sensoren

    df_api = pd.DataFrame(rows)
    df_api["Time"] = pd.to_datetime(df_api["Time"], errors="coerce")
    df_api = df_api.dropna(subset=["Time"]).sort_values("Time").reset_index(drop=True)

    if df_api.empty:
        return {}, anzahl_sensoren

    threshold = pd.Timedelta(minutes=1)
    df_api["group"] = (df_api["Time"].diff() > threshold).cumsum()

    dfs_raw = {}
    for _, group_df in df_api.groupby("group"):
        first_timestamp = group_df["Time"].iloc[0]
        group_df = group_df.drop(columns=["group"]).reset_index(drop=True)
        dfs_raw[first_timestamp] = {"Data": group_df}

    print('Datenbezug abgeschlossen.')

    return dfs_raw, anzahl_sensoren



