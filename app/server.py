#import hashlib
#import json
#from textwrap import dedent
#from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain import Blockchain
import numpy as np
import geopandas
import pandas as pd

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
k=1000 #1000 users
node_identifiers = [str(uuid4()).replace('-', '') for i in range(k)]
# Instantiate the Blockchain
blockchain = Blockchain()
node_index=0
gdf = pd.DataFrame({'Latitude': [],'Longitude': []})
gdf = geopandas.GeoDataFrame(
    gdf, geometry=geopandas.points_from_xy(gdf.Longitude, gdf.Latitude))

@app.route('/geomap',methods=['GET'])
def geomap():
    latitudes=[]
    longtitudes=[]
    for block in blockchain.chain:
        for transaction in block['transactions']:
            latitudes.append(transaction['location'][0])
            longtitudes.append(transaction['location'][1])
            
    new_gdf=pd.DataFrame({'Latitude': latitudes,'Longitude': longtitudes})
    new_gdf = geopandas.GeoDataFrame(
        new_gdf, geometry=geopandas.points_from_xy(new_gdf.Longitude, new_gdf.Latitude))
    gdf.append(new_gdf, ignore_index = True)
    response = {
        'latitudes': latitudes,
        'longtitudes': longtitudes
    }
    return jsonify(response), 200
    
@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    
    for i in range(50000):
        u1, u2 = np.random.choice(range(k), size=2, replace=False)
        blockchain.current_transactions.append({
                'sender': node_identifiers[u1],
                'verifer': node_identifiers[u2],
                'location': [np.random.rand()*180-90, np.random.rand()*360-180]
            })

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])  # this is a POST request, since we’ll be sending data to it.
def new_transaction(sender, recipient, amount):
    values = request.get_json()
    print("i am here: ",values)
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], 
                                       values['data'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    print(nodes)
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
