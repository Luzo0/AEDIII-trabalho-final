from flask import Flask, request, jsonify
import json
import hashlib
from time import time
import requests
from crypto_otrs import ring

app = Flask(__name__)

CENTRAL_AUTHORITY_URL = "http://127.0.0.1:5000"

blockchain = [
    {
        'index': 1,
        'timestamp': time(),
        'votes': ["Genesis Block"],
        'previous_hash': '1',
        'nonce': 0
    }
]

def create_new_block(vote_data, previous_block):
    new_block = {
        'index': previous_block['index'] + 1,
        'timestamp': time(),
        'votes': [vote_data],  # Assuming vote_data contains the vote information
        'previous_hash': calculate_hash(**previous_block),
        'nonce': 0  # This would normally be found through a mining process
    }
    return new_block

def calculate_hash(index, timestamp, votes, previous_hash, nonce):
    block_string = f"{index}{timestamp}{json.dumps(votes)}{previous_hash}{nonce}".encode()
    return hashlib.sha256(block_string).hexdigest()

def valid_block(block, previous_block):
    if block['previous_hash'] != calculate_hash(**previous_block):
        return False
    return True

def get_registered_public_keys():
    response = requests.get(f"{CENTRAL_AUTHORITY_URL}/public_keys")
    public_keys = response.json()["public_keys"]
    print(f"Number of registered public keys: {len(public_keys)}")
    return [key for key in public_keys]

def verify_vote(vote_block):
    message = vote_block['message'].encode()
    signature = vote_block['signature']
    public_keys = get_registered_public_keys()  # Ensure this returns the public keys in the correct format
    is_valid = ring.RVer(public_keys, message, signature)
    return is_valid

def is_duplicate_vote(new_vote_signature):
    for block in blockchain:
        for vote in block['votes']:
            if 'signature' in vote:
                # Assuming `ring` is the array of public keys used for signature verification
                is_from_same_signer, _ = ring.RTrace(get_registered_public_keys(), vote['signature'], new_vote_signature)
                if is_from_same_signer:
                    return True
    return False


@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(blockchain), 200

@app.route('/vote', methods=['POST'])
def receive_vote():
    vote_data = request.json
    if not verify_vote(vote_data):
        return jsonify({'message': 'Invalid vote signature'}), 400
    
    if is_duplicate_vote(vote_data['signature']):
        return jsonify({'message': 'Duplicate vote detected'}), 400

    previous_block = blockchain[-1]
    new_block = create_new_block(vote_data, previous_block)

    if valid_block(new_block, previous_block):
        blockchain.append(new_block)
        return jsonify({'message': 'Vote added to the blockchain'}), 201
    else:
        return jsonify({'message': 'Invalid block'}), 400

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

