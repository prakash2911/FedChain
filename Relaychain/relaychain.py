from flask import Flask, request, jsonify,send_file
from flask_cors import CORS, cross_origin
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import config
from Blockchain import Blockchain, ModelTransaction
from dataPreProcess import load_test_dataset
import ModelConfig
from model import evaluate_model
import sys
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load keys

@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    return jsonify({}), 200

@app.route('/get_public_key', methods=['GET'])
@cross_origin()
def get_public_key():  
    return send_file(
        './keys/public_key.pem',
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='public_key.pem'
    )
@app.route('/testModel', methods=['POST'])
@cross_origin()
def testModel():
    global blockchain
    last_block = blockchain.chain[-1]
    if last_block.transactions:
        last_transaction = last_block.transactions[-1]
        gmodel = ModelConfig.__dict__[config.ModeName]
        model = gmodel(config.INPUT_SIZE,config.NUM_CLASSES)
        model.from_bytes(last_transaction.model_bytes)
        dataset = load_test_dataset(config.Test,config.BATCH_SIZE)
        accuracy = evaluate_model(model,dataset.test)
        return jsonify({'accuracy': accuracy}), 200
    else:
        return jsonify({'message':'No transactions'}), 404

    
@app.route('/verify_decrypt_and_read', methods=['POST'])
@cross_origin()
def verify_decrypt_and_read():
    with open('./keys/private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    encrypted_aes_key = bytes.fromhex(request.json['encrypted_aes_key'])
    iv = bytes.fromhex(request.json['iv'])
    encrypted_data = bytes.fromhex(request.json['encrypted_data'])
    tag = bytes.fromhex(request.json['tag'])
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv,tag))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    mtx = ModelTransaction(decrypted_data)
    blockchain.add_transaction(mtx)
    blockchain.mine_block()
    return jsonify({'message': 'Transaction added and block mined successfully!'}), 200

@app.route('/blocks', methods=['GET'])
@cross_origin()
def get_blocks():
    global blockchain
    blocks_data = []
    for block in blockchain.chain:
        block_data = {
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
        }
        blocks_data.append(block_data)
    
    response = {
        'length': len(blockchain.chain),
        'blocks': blocks_data
    }
    
    return jsonify(response), 200
        
blockchain = Blockchain()    
if __name__ == '__main__':
    app.run(host="0.0.0.0", ssl_context=(config.certificate,config.private_key),debug=config.DEBUG)