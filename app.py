import numpy as np
import pandas as pd
from datetime import *
import datetime as dt
import sqlalchemy
from sqlalchemy.types import Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
inspector = inspect(engine)

###########################################################
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Climate Analysis!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f" - Dates and Temperatures Observed from 2016/08/23 to 2017/08/23 <br/>"
        f"/api/v1.0/stations"
        f" - List of Stations<br/>"
        f"/api/v1.0/tobs"
        f" - Temperature Observed from 2016/08/23 to 2017/08/23 <br/>"
        f"/api/v1.0/<start>"
        f" - Minimum Temperature, Average Temperature and Maximun Temperature for a given start day<br/>"
        f"/api/v1.0/<start>/<end>"
        f" - Minimum Temperature, Average Temperature and Maximun Temperature for a given start-end range<br/>"
    )


@app.route("/api/v1.0/precipitation")
def pcrp():
    # Query to retrieve the last 12 months
    date_max = session.query(func.max(Measurement.date)).first()[0]
    date_max = dt.datetime.strptime(date_max, "%Y-%m-%d").date()
    year_before = date_max - timedelta(365)

    prcp = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= year_before)
        .order_by(Measurement.date)
        .all()
    )
    prcp_df = (pd.DataFrame(prcp)).set_index("date").sort_index(ascending=True)
    prcp_dict = dict(zip(prcp_df.index, prcp_df.prcp))

    return jsonify(prcp_dict)  # Convert que query results to a dict


@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station).all()
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temperature():
    # Query to retrieve the last 12 months
    date_max = session.query(func.max(Measurement.date)).first()[0]
    date_max = dt.datetime.strptime(date_max, "%Y-%m-%d").date()
    year_before = date_max - timedelta(365)

    temperature_list = (
        session.query(Measurement.tobs)
        .filter(Measurement.date >= year_before)
        .order_by(Measurement.date.desc())
        .all()
    )
    return jsonify(temperature_list)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    temp_data = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .all()
    )
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def trip_range(start=None, end=None):
    sel = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]

    if not end:
        temp_data = session.query(*sel).filter(Measurement.date >= start).all()
        return jsonify(temp_data)
    temp_data = (
        session.query(*sel)
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    return jsonify(temp_data)


if __name__ == "__main__":
    app.run(debug=True)
