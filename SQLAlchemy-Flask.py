# Imports
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import datetime as dt

from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# create a flask app
app = Flask(__name__)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# create home page
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        "Welcome to the Honolulu weather measurements API!<br><br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/&lt;start&gt;<br>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for precipitation...")

    # sort date desc and grab first result
    precip_results = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(precip_results[0], "%Y-%m-%d")

    # get start date by subtracting 1 from year.
    # this could have issues during leap years, but I am ignoring that for now.
    start_date = dt.datetime(last_date.year - 1, last_date.month, last_date.day).date()

    # Perform a query to retrieve the data and precipitation scores
    precip_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).all()

    # place results in dataframe
    precip_df = pd.DataFrame(precip_results, columns = ["Date", "Precipitation"]).set_index("Date").dropna()

    # Sort the dataframe by date
    precip_df = precip_df.sort_values("Date")
    precip_dict = precip_df.T.to_dict()

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for stations...")

    station_results = session.query(Station.station, Station.name).all()

    station_df = pd.DataFrame(station_results, columns=["Station", "Name"]).set_index("Station")
    station_df = station_df.sort_values("Station")
    station_dict = station_df.T.to_dict()

    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for tobs...")

    # sort date desc and grab first result
    precip_results_2 = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(precip_results_2[0], "%Y-%m-%d")

    # get start date by subtracting 1 from year.
    # this could have issues during leap years, but I am ignoring that for now.
    start_date = dt.datetime(last_date.year - 1, last_date.month, last_date.day).date()

    # get most active station
    # group by stations, count temperature observations per station, sort descending
    station_count = session.query(Measurement.station, func.count(Measurement.tobs)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # most active station is first result from above
    station_most_active = station_count[0][0]

    # query temperature readings for last year, based on start date calculated earlier in notebook
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == station_most_active).\
        filter(Measurement.date > start_date).all()

    # convert to a dataframe
    tobs_df = pd.DataFrame(tobs_results, columns=["Date", "Tobs"]).set_index("Date")
    tobs_df = tobs_df.sort_values("Date")
    tobs_dict = tobs_df.T.to_dict()

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_temps(start):

    temp_results = calc_temps(start, "9999-12-31")

    temp_df = pd.DataFrame(temp_results, columns=["TMin", "TAvg", "TMax"])
    temp_dict = temp_df.T.to_dict()

    #temp_dict = {"Tmin": 80, "TAvg": 85, "TMax": 90}
    return jsonify(temp_dict)

# run the flask page
if __name__ == "__main__":
    app.run(debug=True)


# In[ ]:





# In[ ]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.


# In[ ]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)


# In[ ]:


# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation


# ## Optional Challenge Assignment

# In[ ]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")


# In[ ]:


# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip

# Use the start and end date to create a range of dates

# Stip off the year and save a list of %m-%d strings

# Loop through the list of %m-%d strings and calculate the normals for each date


# In[ ]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index


# In[ ]:


# Plot the daily normals as an area plot with `stacked=False`

