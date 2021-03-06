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
import os

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
rtree = Rtree()
blockchain = Blockchain(rtree)              ## new blockchain need to new rtree first
coordinate = Coordinate()
node_index=0
coordinate = Coordinate()

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

@app.route('/geomap',methods=['GET'])
def geomap():
    locations = []
    for block in blockchain.chain:
        for trans in block['transactions']:
            locations.append({'lat': trans['location'][0], 'lon': trans['location'][1]})
    return render_template("geomap.html", loc=locations)


## API with blockchain
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Forge the new Block by adding it to the chain\
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash, None)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'remark': block['remark']
    }
    return jsonify(response), 200


@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    result = blockchain.valid_chain()
    return "The result of the chain validation is %s" % result, 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain,
    }
    return jsonify(response), 200


## get coordinate data API

@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    try:
        input = get_params_checking(request, ["lat_min", "lon_min", "lat_max", "lon_max"], ["lat_min", "lon_min", "lat_max", "lon_max"])
        amenity_group = coordinate.get_amenity_from_osm(input["lat_min"], input["lon_min"], input["lat_max"], input["lon_max"], type_name=input["types"])
    except Exception as e:
        return error_handling(e)
    response = {
        "get_coordinates_number": len(amenity_group),
        "info": amenity_group.to_dict('index')
    }
    return jsonify(response), 200

@app.route('/export_data', methods=['GET'])
def export_data():
    input = get_params_checking(request, ["file_name"])
    coordinate.amenity_group.to_csv('../coordinates/%s.csv' % input["file_name"], index=False)
    out_file = open("../coordinates/%s_remark.txt" % input["file_name"], "w")
    json.dump(coordinate.remark, out_file)
    return "Export files Finish.", 200


## API for input data
@app.route('/update_coordinate_by_input', methods=['POST'])  # this is a POST request, since we???ll be sending data to it.
def update_coordinate_by_input():
    array_values = request.get_json()
    count = 0
    for values in array_values:
        required = ['point']
        if not all(k in values for k in required):
            return 'Missing values', 400
        point_required = ['id', 'lat', 'lon', 'name']
        if not all(k in values["point"] for k in point_required):
            return 'Point must have id, lat, lon and name', 400

        # Create a new Transaction
        new = blockchain.new_transaction(values["point"]['id'], values["point"]['lat'], values["point"]['lon'], values["point"]['name'])
        count += 1

    response = {'message': f'{count} Transactions will be added to Block {new}'}
    return jsonify(response), 201

@app.route('/update_coordinate_by_search_result', methods=['POST'])  # this is a POST request, since we???ll be sending data to it.
def update_coordinate_by_search_result():
    count = 0
    if coordinate.check_amenity_group_none() == True: return "No Data have to update.", 200

    amenity_group_list = coordinate.get_amenity_group().reset_index().values.tolist()
    blockchain.new_remark(coordinate.remark)
    for item in amenity_group_list:
        point_id = item[0]
        lat = item[1]
        lon = item[2]
        name = item[3]

        # Create a new Transaction
        new = blockchain.new_transaction(point_id, lat, lon, name)
        count += 1
    amenity_group_list = None
    coordinate.make_amenity_group_to_none()

    response = {'message': f'{count} Transactions will be added to Block {new}'}
    return jsonify(response), 201

@app.route('/update_coordinates_from_files', methods=['GET'])
def import_data():
    input = get_params_checking(request, ["file_name"])
    if os.path.isfile("../coordinates/%s.csv" % input["file_name"]) == False: return "Files not found.", 400
    amenity_group = pd.read_csv('../coordinates/%s.csv' % input["file_name"])
    coordinate.write_amenity_group(amenity_group)

    in_file = open("../coordinates/%s_remark.txt" % input["file_name"], "r")
    remark = json.load(in_file)
    coordinate.write_remark(remark)
    response = {'message': f'{input["file_name"]}\'s informations has imported into amenity group.'}
    return jsonify(response), 200

## API for Rtree

@app.route("/get_nearest_k_points", methods=['GET'])
def get_nearest_k_points():
    try:
        input = get_params_checking(request, ["lat", "lon", "k", "types"], ["lat", "lon"], ["k"])
        result = rtree.get_nearest_k_points(blockchain, input["lat"], input["lon"], input["k"], input["types"])
        locations=[{'lat': input["lat"], 'lng': input["lon"]}]
        labels=["Your Location"]
        first_lat=result[0]['lat']
        first_lng=result[0]['lon']
        for item in result:
             locations.append({'lat': item['lat'], 'lng': item['lon']})
             labels.append(item['name'])
    except Exception as e:
        return error_handling(e)
    #return jsonify(result), 200
    return render_template("geomap.html", labels=labels, center_lat=first_lat, center_lng=first_lng, loc=locations)


@app.route('/')
def home():
   return render_template("home.html")


## rtree signature checking
def rtree_signature_checking(rtree, blockchain):
    current_rtree_signature = rtree.get_idx_signature()
    blockchain_rtree_signature = blockchain.last_block["rtree_signature"]
    return current_rtree_signature == blockchain_rtree_signature

## error handle and show traceback
def error_handling(e):
    traceback.print_exc()
    return ("%s: %s" % (type(e).__name__, e.args[0]), 400)

def get_params_checking(request, blank_checking, float_checking=[], integer_checking=[]):
    input = {}
    for i in request.args:
        input[i] = request.args.get(i)
    for i in blank_checking:
        value = input[i]
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
