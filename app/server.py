#import hashlib
#from textwrap import dedent
#from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, render_template
import traceback
import numpy as np
import geopandas
import json
import pandas as pd
import random

## from our files
from blockchain import Blockchain
from map_data import Coordinate
from rtree_update import Rtree

# Instantiate our Node
app = Flask(__name__, template_folder='../templates', static_folder = '../static')

# Generate a globally unique address for this node
k=1000 #1000 usersl
node_identifiers = [str(uuid4()).replace('-', '') for i in range(k)]
# Instantiate the Blockchain
blockchain = Blockchain()
coordinate = Coordinate()
rtree = Rtree()
node_index=0
coordinate = Coordinate()
amenity_group = None
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

'''
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    input = {}
    for i in ["lat_min", "lng_min", "lat_max", "lng_max", "type_name"]:
        value = request.args.get(i)
        if i in ["lat_min", "lng_min", "lat_max", "lng_max"]:
            try:
                if value is None or value == "": return "Key '%s' must be filled in." % i, 400     ## check all coordinates params has been filled in
                value = float(value)
            except ValueError as e:
                return "The value of key '%s' must be float." % i, 400
        input[i] = value
    try:
        amenity_group = coordinate.get_amenity_from_osm(input["lat_min"], input["lng_min"], input["lat_max"], input["lng_max"])
    except Exception as e:
        return error_handling(e)
    response = {
        "get_coordinates_number": len(amenity_group),
        "info": amenity_group.to_dict('index')
    }
    #return jsonify(response), 200
    amenity_group= amenity_group.rename(columns={'lon': 'lng'})
    amenity_group=amenity_group.head(5)
    first_lat=amenity_group['lat'].iloc[0]
    first_lng=amenity_group['lng'].iloc[0]
    return render_template("geomap.html", center_lat=first_lat, center_lng=first_lng, loc=amenity_group[['lat','lng']].to_dict("records"))

## error handle and show traceback
def error_handling(e):
    traceback.print_exc()
    return ("%s: %s" % (type(e).__name__, e.args[0]), 400)
'''

@app.route('/geomap',methods=['GET'])
def geomap():
    locations = []
    for block in blockchain.chain:
        for trans in block['transactions']:
            locations.append({'lat': trans['location'][0], 'lon': trans['location'][1]})
    return render_template("geomap.html", loc=locations)

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.

    # for i in range(5):
    #     u1, u2 = np.random.choice(range(k), size=2, replace=False)
    #     lat = np.random.rand()*180-90
    #     lon = np.random.rand()*360-180
    #     #idx.insert(i, (lat, lon, lat, lon))
    #     blockchain.current_transactions.append({
    #             'sender': node_identifiers[u1],
    #             'verifer': node_identifiers[u2],
    #             'location': [lat, lon]
    #         })

    # Forge the new Block by adding it to the chain\
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash, None)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])  # this is a POST request, since we’ll be sending data to it.
def new_transaction(longitude, latitude, description):
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['longitude', 'latitude', 'description']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    new = blockchain.new_transaction(values['longitude'], values['latitude'],
                                       values['description'])

    response = {'message': f'Transaction will be added to Block {new}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

## get coordinate data api
'''
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    try:
        input = get_params_checking(request, ["lat_min", "lon_min", "lat_max", "lon_max", "type_name"], ["lat_min", "lon_min", "lat_max", "lon_max"])
        amenity_group = coordinate.get_amenity_from_osm(input["lat_min"], input["lon_min"], input["lat_max"], input["lon_max"])
    except Exception as e:
        return error_handling(e)
    response = {
        "get_coordinates_number": len(amenity_group),
        "info": amenity_group.to_dict('index')
    }
    return jsonify(response), 200
'''

@app.route('/get_one_coordinate_form_amenity_group', methods=['GET'])
def get_one_coordinate():
    if amenity_group is None: return "Please call get_coordinate API to get amenity_group.", 400

## API for Rtree
@app.route('/show_rtree_idx', methods=['GET'])
def show_rtree_idx():
    a, b = rtree.get_rtree_index()
    print(a, b)
    return "", 200

@app.route("/update_rtree_index", methods=['POST'])
def update_rtree_index():
    array_values = request.get_json()
    for values in array_values:
        required = ['action', 'point']
        if not all(k in values for k in required):
            return 'Missing values', 400
        point_required = ['lat', 'lon', 'name']
        if not all(k in values["point"] for k in point_required):
            return 'Point must have lat, lon and name', 400

        point_id = random.randint(100000000000, 999999999999)
        values["point"]["id"] = point_id
        response = rtree.update_index(values["point"], values["action"])
    return response, 200

@app.route("/get_nearest_k_points", methods=['GET'])
def get_nearest_k_points():
    try:
        input = get_params_checking(request, ["lat", "lon", "k"], ["lat", "lon"], ["k"])
        result = rtree.get_nearest_k_points(input["lat"], input["lon"], input["k"])
    except Exception as e:
        return error_handling(e)
    return jsonify(result), 200

## error handle and show traceback
def error_handling(e):
    traceback.print_exc()
    return ("%s: %s" % (type(e).__name__, e.args[0]), 400)

def get_params_checking(request, blank_checking, float_checking=None, integer_checking=None):
    input = {}
    for i in blank_checking:
        value = request.args.get(i)
        if value is None or value == "": raise ValueError("Key '%s' must be filled in." % i)      ## check all coordinates params has been filled in
        if i in float_checking:
            try:
                value = float(value)
            except ValueError:
                raise ValueError("The value of key '%s' must be float." % i)
        elif i in integer_checking:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("The value of key '%s' must be integer." % i)
        input[i] = value
    return input

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
