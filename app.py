import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Start a session to run a few queries
session = Session(engine)

# query to determine the most active station
station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
most_active_id = station_activity[0][0]

#query to determine the most recent date
last_date_tuple = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
date_time_str = last_date_tuple[0]
last_date = dt.datetime.strptime(date_time_str, '%Y-%m-%d')
session.close()
#query to determine the date a year before the most recent date


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h3>Welcome to My API!!!</h3>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>api/v1.0/tobs</a><br/>"

        f"<br/>"
        f"Insert  '/start_date/' or '/start_date/end_date/' into url for date specific results:<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
        session = Session(engine)

        results_q1 = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.prcp != 'None').order_by(Measurement.date.desc()).\
            filter(Measurement.date >= (last_date.date()-dt.timedelta(days=365))).\
            all()

        session.close()

        all_prcp = []
        for date, prcp in results_q1:
            prcp_dict = {}
            prcp_dict["date"] = date
            prcp_dict["prcp"] = prcp
            all_prcp.append(prcp_dict)

        return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # List the stations
    stations = session.query(Measurement.station).\
        group_by(Measurement.station).all()

    session.close()

    all_stations = [station[0] for station in stations]
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date_tuple = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_time_str = last_date_tuple[0]
    last_date = dt.datetime.strptime(date_time_str, '%Y-%m-%d')

    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_id = station_activity[0][0]

    # Perform a query to retrieve the dates and tobs for most active station
    results_q2 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_id).\
        filter(Measurement.tobs != 'None').order_by(Measurement.date.desc()).\
        filter(Measurement.date >= (last_date.date()-dt.timedelta(days=365))).\
        all()

    session.close()

    all_temp = []
    for date, temp in results_q2:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = temp
        all_temp.append(temp_dict)

    return jsonify(all_temp)


@app.route("/api/v1.0/<start>")
def start(start):
        session = Session(engine)
        results_q4 = session.query(func.min(Measurement.tobs),\
            func.avg(Measurement.tobs),\
            func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        session.close()

        stats_in_range = []
        for min_tobs, avg_tobs, max_tobs in results_q4:
            in_range_dict = {}
            in_range_dict["min_tobs"] = min_tobs
            in_range_dict["avg_tobs"] = avg_tobs
            in_range_dict["max_tobs"] = max_tobs
            stats_in_range.append(in_range_dict)
        return jsonify(stats_in_range)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results_q4 = session.query(func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    stats_in_range = []
    for min_tobs, avg_tobs, max_tobs in results_q4:
        in_range_dict = {}
        in_range_dict["min_tobs"] = min_tobs
        in_range_dict["avg_tobs"] = avg_tobs
        in_range_dict["max_tobs"] = max_tobs
        stats_in_range.append(in_range_dict)
    return jsonify(stats_in_range)

if __name__ == '__main__':
    app.run(debug=True)

