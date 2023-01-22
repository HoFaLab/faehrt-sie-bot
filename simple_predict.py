###### Step 1: Install and Import Libraries# Install libraries
# pip install # Get time series data
import numpy as np
import pandas as pd 
# Visualization
import seaborn as sns
import matplotlib.pyplot as plt
# Model performance evaluation
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from datetime import datetime, timedelta


def time_since_last_extreme(timestamp):
    prev_extreme = get_previous_extreme(timestamp)

    return (timestamp - prev_extreme["timestamp"]).dt.total_seconds() / 60


# get last extrema timestamp and category. for repeating extrema:: max: return first, min: return last 
""" TODOOO just get the index here. and work with that"""
def get_previous_extreme(timestamp):
    # previous extreme can max be 8 hours away
    earliest_time = timestamp - timedelta(hours=8, minutes=0)

    filtered_extrema = extrema[extrema["timestamp"].between(
        earliest_time, # .item().strftime("%Y-%m-%d %H:%M:%S"),
        timestamp# .item().strftime("%Y-%m-%d %H:%M:%S")
        )]
    
    # often extrema values repeat within half an hour on a plateau    
    filtered_extrema.sort_values(by=["timestamp"], inplace=True, ascending=False)

    if filtered_extrema["min"].all():
        # min: return row with latest timestamp 
        return filtered_extrema.tail(1)["timestamp"] # , "min"
    elif filtered_extrema["max"].all():
        # max: return row with earliest timestamp
        return filtered_extrema.head(1)["timestamp"] #, "max"
    else:
        raise ValueError("min and max detected in 6h interval")



def wind_degree_to_cardinal(d):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(dirs)))
    
    dir = dirs[ix % len(dirs)]

    # if "W" in dir:
    #     return True

    # return False

    return dir


###### Step 2: Pull Data# Data start date
data = pd.read_csv("data/historic_data_wind_water_combined.csv")

data.head() # Drop one level of the column names
data.head()# Information on the dataframe
data.info()# Visualize data using seaborn

"""
sns.set(rc={'figure.figsize':(12,8)})
sns.lineplot(x=data.index, y=data['water_level'])
sns.lineplot(x=data.index, y=data['wind_speed'])
sns.lineplot(x=data.index, y=data['wind_direction'])
plt.legend(['water', 'speed', 'direction'])
plt.show()
"""
# TODO categorize wind direction?  <-- no effect?
# TODO add "time since last high", add trend. add last_low , last_high, 
# TODO the moon?
# TODO and then just dont use cyclic 

# Find local peaks
from scipy.signal import argrelextrema
n = 10*6*6  # number of points to be checked before and after, last 6 hours

data['min'] = data.iloc[argrelextrema(data['water_level'].values, np.less_equal,
                    order=n)[0]]['water_level']
data['max'] = data.iloc[argrelextrema(data['water_level'].values, np.greater_equal,
                    order=n)[0]]['water_level']


# Plot results

plt.scatter(data.index, data['min'], c='r')
plt.scatter(data.index, data['max'], c='g')
plt.plot(data.index, data['water_level'])

plt.show()
#print(data.head(50))
#print(data.describe())

# TODO for debugging: delete
#data = data.head(500)


data["timestamp"] = pd.to_datetime(data["timestamp"])


data_value = data["water_level"]
data_value.plot()


"""
check steigung an jeder stelle, speicher als kurve in abhängigkeit von 
    - seit des letzten extrema 
    - letztes extrema ist min oder max?
    
    - aufteilen in bevor/nach max.
    - plotten der werte
        - ab wann ist die steigung nicht mehr linear? und wie ist sie dann?
        - kann man den nicht linearen teil auf ne kurve fitten?
        - gibt es abhängigkeiten von mond, wind, etc?
"""

"""
create dataframe for extrema with category min/max and timestamp
create function to get timestamp of last min or last max
add time since last extrema and extrema category to data
create function to calculate current slope by current and successor value and 
"""

# create dataframe for extrema with category min/max and timestamp
extrema = data[["timestamp",  "min", "max"]].copy()
extrema = extrema.dropna(subset=["min", "max"], how="all")

# keep only the last occuring minimum (often minimum values repeat on a plateau)
minima = extrema.dropna(subset=["min"], how="all").drop(columns=["max"])
mask = (minima.shift(-1)["timestamp"]- minima["timestamp"]).dt.total_seconds() / 3600 > 1
minima.loc[mask, "is_last_min"] = True
minima = minima.dropna(subset="is_last_min", how="all")

# keep only the first occuring maximum (often maximum values repeat on a plateau)
maxima = extrema.dropna(subset=["max"], how="all").drop(columns=["min"])
mask = (maxima["timestamp"] - maxima.shift(1)["timestamp"]).dt.total_seconds() / 3600 > 1
maxima.loc[mask, "is_first_max"] = True
maxima = maxima.dropna(subset="is_first_max", how="all")

# merge min, max dataframes with data
data = pd.merge(data, minima, how="outer")
data = pd.merge(data, maxima, how="outer")

"""
time of last extreme
where on series gets last matching row
-> https://stackoverflow.com/questions/74797150/how-to-add-a-column-with-indices-of-the-last-occurrence-of-a-value-in-pandas
"""
data["time_last_min"] = data["timestamp"].where(data["is_last_min"].eq(True)).fillna(method="ffill")
data["time_first_max"] = data["timestamp"].where(data["is_first_max"].eq(True)).fillna(method="bfill")
data["time_between"] = (data["time_first_max"] - data["time_last_min"]).dt.total_seconds() / 60

# clean data
data = data[data["time_between"] < 7*60]

# TODO: DROP all rows where time between maxima > 7h*60min

analyze = data["time_between"].copy()

print(analyze.describe())
exit()



# add time since last extreme and extrema category to data

test_data = data.sample(1000)
test_data['c'] = test_data.apply(lambda row: get_previous_extreme(row["timestamp"]), axis=1)

print(test_data)
exit()

test_data[["last_extreme_time", "cat"]] = pd.DataFrame(test_data["last_extreme"].to_list(), index=test_data.index)
print(test_data["last_extreme_time"])
test_data["last_extreme_time"] = pd.to_datetime(test_data["last_extreme_time"])
test_data["time_since"] = (test_data["timestamp"] - test_data["last_extreme_time"]).dt.total_seconds()




wind_data.sort_values(by=["timestamp"], inplace=True, ascending=False)
extrema = extrema.set_index('timestamp')



