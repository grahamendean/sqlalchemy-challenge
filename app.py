#import dep
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import timedelta
import numpy as np
from flask import Flask, jsonify

#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#start flask
app = Flask(__name__)

#route welcome page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/start_end_date/<start>/<end>"
    )
#create precipitation page    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Last Year of Percipitation Data"""
    session=Session(engine)
    last_date = session.query(func.max(Measurement.date)).all()[0][0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    previous_year = last_date - dt.timedelta(365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=previous_year).all()
    return jsonify (results)

#create stations page
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    #return all stations
    stations=session.query(Station.station).all()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    last_date = session.query(func.max(Measurement.date)).all()[0][0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    previous_year = last_date - dt.timedelta(365)
    most_active = session.query(Measurement.station, func.count()).group_by(Measurement.station).\
    order_by(func.count().desc()).first()
    result = session.query(Measurement.tobs).filter(Measurement.station== 'USC00519281').\
    filter(Measurement.date >= previous_year).all()
    return jsonify(most_active, result)

@app.route("/api/v1.0/start_date/<start>")
def startdate(start):
    session=Session(engine)
    #get the min, max, avg filter by >=start
    results= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    group_by(Measurement.date).all()
    return jsonify(results)

@app.route("/api/v1.0/start_end_date/<start>/<end>")
def startenddate(start, end):
    session=Session(engine)
    #get min, max, avg filter by >=start, <= end
    results= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start, Measurement.date <= end).\
    group_by(Measurement.date).all()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)