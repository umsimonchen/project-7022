# -*- coding: utf-8 -*-
"""
Created on Sat May 22 12:08:12 2021

@author: simon
"""
import geopandas
import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect, url_for
import matplotlib as plt

app = Flask(__name__, template_folder='../templates', static_folder = '../static')
#app._static_folder = '../static'

df = pd.DataFrame(
    {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
     'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
     'Latitude': [-34.58, -15.78, -33.45, 4.60, 10.48],
     'Longitude': [-58.66, -47.91, -70.66, -74.08, -66.86]})
df = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))

df2 = pd.DataFrame(
    {'City': ['Macau','Guangzhou'],
     'Country': ['Macau','China'],
     'Latitude': [23.45, 23.56],
     'Longitude': [123.45,122.34]})
df2 = geopandas.GeoDataFrame(
    df2, geometry=geopandas.points_from_xy(df2.Longitude, df2.Latitude))

df = df.append(df2, ignore_index = True)
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))


ax = world.plot()
df.plot(ax=ax, color='red')
fig = ax.get_figure()
fig.savefig('../static/images/geomap.png')
#cities.plot(ax=ax,color='red')

@app.route('/')
def home():
   return render_template("home.html")

@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form = request.form
        return render_template('data.html',form = form)

    
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)