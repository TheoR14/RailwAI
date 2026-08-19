import warnings
from datetime import datetime, timedelta
from GeoVis.Preprocessing.Peak_Detektion import detect_peaks
from GeoVis.API.Datenbezug_API import get_dfs_raw
from GeoVis.Geschwindigkeit import calc_speed

def date_extractor(value):
    micro_sec = value * 100
    sec = micro_sec / 1_000_000
    hour = int(sec // 3600)
    rest_sec = sec - hour * 3600
    minute = int(rest_sec // 60)
    second = rest_sec - minute * 60

    return f'{hour:02d}:{minute:02d}:{second:06.3f}'

def main(login_data, PROJECT_ID, Projekt_DB, sensor_name, datum):
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # define the research period
    startdatum = datetime(int(datum[0:4]), int(datum[4:6]), int(datum[6:8]), 0, 0) # at 00:00
    enddatum = startdatum + timedelta(days=1) # one day later

    print("Start Calculation:", startdatum.isoformat())
    print("End Calculation  :", enddatum.isoformat())

    dfs_raw_1, anzahl_sensoren = get_dfs_raw(
        login_data=login_data,
        project_id=PROJECT_ID,
        projekt_db=Projekt_DB,
        startdatum=startdatum,
        enddatum=enddatum,
        sensor_name=sensor_name,
    )
    print(f"Gefundene Sensoren: {anzahl_sensoren}")

    if PROJECT_ID == "1113":
        pattern = r'ADTC_(\d+)_'
        distance = 4.8
    elif PROJECT_ID == "817":
        pattern = r'D_(\d+)'
        distance = 4.93 # mean value
    elif PROJECT_ID == "1191":
        # distance = 4.8
        distance = 3
    elif PROJECT_ID == "810": #St. Gallen
        distance = 4.8
    else:
        raise ValueError("Unknown PROJECT_ID")
    
    dfs_raw_2 = detect_peaks(dfs_raw_1, min_peak_height=-0.3)
    dfs_raw_3 = calc_speed(dfs_raw_2, anzahl_sensoren, distance)

    return dfs_raw_3