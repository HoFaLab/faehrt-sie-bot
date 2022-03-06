import pandas as pd
import json


# reads historic water level data and returns it as DataFrame
def make_water_level_df() -> pd.DataFrame:
    with open("data/historic_input_data/historic_water_level_measurements.json") as f:
        water_data = json.load(f)

    df = pd.DataFrame(water_data)

    """ Data Excerpt
    [
        {
        "timestamp": "2022-01-18T00:01:00+01:00",
        "value": 381.0
        },
    ]
    """

    df.timestamp = pd.to_datetime(df.timestamp)
    df.timestamp = df.timestamp.dt.tz_localize(None)
    df.sort_values(by=["timestamp"], inplace=True)

    df = df.rename(columns={"value": "water_level"})

    return df

# reads historic wind data and returns it as DataFrame
def make_wind_data_df() -> pd.DataFrame:
    wind_data = pd.read_csv("data/historic_input_data/historic_wind_data.csv", delimiter=";")
    
    """ Data Excerpt
    STATIONS_ID;MESS_DATUM;QN;FF_10;DD_10;eor
    1975;202201180000;3;4.0; 290;eor
    """
    wind_data["MESS_DATUM"] = pd.to_datetime(wind_data["MESS_DATUM"], format='%Y%m%d%H%M')
    wind_data = wind_data.rename(columns={"MESS_DATUM": "timestamp"})
    wind_data.sort_values(by=["timestamp"], inplace=True)
    wind_data = wind_data.rename(columns={"FF_10": "wind_speed"})
    wind_data = wind_data.rename(columns={"DD_10": "wind_direction"})
    wind_data = wind_data.drop(columns=["QN", "STATIONS_ID", "eor"])

    return wind_data


if __name__ == "__main__":
    water_df = make_water_level_df()
    wind_df = make_wind_data_df()

    merged_df =  merged = pd.merge_asof(water_df, wind_df, on='timestamp')
    merged_df.to_csv("data/historic_data.csv")

    print(merged_df)