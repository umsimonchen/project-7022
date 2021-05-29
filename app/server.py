#import hashlib
#import json
#from textwrap import dedent
#from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain
from map_data import Coordinate
import traceback
import numpy as np
import geopandas
import json
import pandas as pd
from pandana.loaders import osm
from rtree import index

# Instantiate our Node
app = Flask(__name__, template_folder='../templates', static_folder = '../static')

# Generate a globally unique address for this node
k=1000 #1000 usersl
node_identifiers = [str(uuid4()).replace('-', '') for i in range(k)]
# Instantiate the Blockchain
blockchain = Blockchain()
coordinate = Coordinate()
node_index=0
amenity_group = None

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

@app.route('/geomap',methods=['GET'])
def geomap():
    locations = []
    for block in blockchain.chain:
        for trans in block['transactions']:
            locations.append({'lat': trans['location'][0], 'lng': trans['location'][1]})
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
    return jsonify(response), 200

## error handle and show traceback
def error_handling(e):
    traceback.print_exc()
    return ("%s: %s" % (type(e).__name__, e.args[0]), 400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
