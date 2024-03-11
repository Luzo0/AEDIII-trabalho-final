from flask import Flask, request, jsonify
app = Flask(__name__)

# This will store registered public keys
registered_public_keys = []

@app.route('/register', methods=['POST'])
def register_public_key():
    public_key = request.json.get('public_key')
    if public_key and public_key not in registered_public_keys:
        registered_public_keys.append(public_key)
        return jsonify({"message": "Public key registered successfully."}), 200
    return jsonify({"message": "Invalid request or public key already registered."}), 400

@app.route('/public_keys', methods=['GET'])
def get_public_keys():
    return jsonify({"public_keys": registered_public_keys}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)