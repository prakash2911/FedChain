from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
import ModelConfig
from config import config 
from utils import *
from dataPreProcess import load_dataset
from Blockchain import Blockchain, ModelTransaction
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from model import *
import sys
import os
import socket

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/send_data', methods=['POST'])
@cross_origin()
def send_data():
    last_block = blockchain.chain[-1]
    response = {}
    if last_block.transactions:
        last_transaction = last_block.transactions[-1]
        data = last_transaction.model_bytes
    global_model.from_bytes(data)
    with open('./keys/public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    res = requests.post(config.relayChain+'/verify_decrypt_and_read',json={'encrypted_aes_key' : encrypted_aes_key.hex(),
        'iv':iv.hex(),
        'encrypted_data':encrypted_data.hex(),
        'tag' :  encryptor.tag.hex()
        },verify=False
    )
    
    return jsonify(response), res.status_code    

@app.route('/testmodel', methods=['GET','POST'])
@cross_origin()
def evaluated():
    response = {}
    last_block = blockchain.chain[-1]
    model = ModelConfig.__dict__[config.ModeName]
    model.from_bytes(last_block.transactions[-1].model_bytes)
    dataset  = load_dataset(config.Test,config.BATCH_SIZE)
    response['accuracy'] = evaluate_model(model,dataset.test,last_block.transactions[-1])
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
@cross_origin()
def mine_block():
    blockchain.mine_block()
    response = {'message': 'Block mined successfully!'}
    return jsonify(response), 200

@app.route('/blocks', methods=['GET'])
@cross_origin()
def get_blocks():
    blocks_data = []
    
    for block in blockchain.chain:
        block_data = {
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'block_number': block.block_number,
            'gas_used': block.gas_used,
            'contract_address':None,
            'type': block.type,
            'from_address': block.from_address,
            'to_address': block.to_address,
            'status': block.status,
        }
        blocks_data.append(block_data)
    
    response = {
        'length': len(blockchain.chain),
        'blocks': blocks_data
    }
    
    return jsonify(response), 200


@app.route('/localupdate', methods=['GET','POST'])
@cross_origin()
def localUpdate():
    data = request.get_json()
    dataset  = load_dataset(f'{config.Train}/{data["dataset"]}',config.Test,config.BATCH_SIZE)
    response = {}
    size,mean,std = localStatistics(dataset.train)
    last_block = blockchain.chain[-1]
    if last_block.transactions:
        last_transaction = last_block.transactions[-1]
        block_data = {
            'model_bytes':last_transaction.model_bytes,
            'mean': last_transaction.mean.tolist(),
            'std_dev': last_transaction.std_dev.tolist(),
            'size': last_transaction.size
        }
    try:
        model = ModelConfig.__dict__[config.ModeName]
    except KeyError:
        sys.exit(1)
    gobal_model = model(config.INPUT_SIZE, config.NUM_CLASSES )
    gobal_model.from_bytes(block_data['model_bytes'])
    response['before'] = evaluate_model(gobal_model, dataset.test,block_data)
    mean = Combined_Mean(mean, size ,block_data['mean'],block_data['size']) 
    std = Combined_Std(std, size, block_data['std_dev'], block_data['size'])
    autoencoder = model(config.INPUT_SIZE,config.NUM_CLASSES)
    train_model(autoencoder, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE, mean, std)
    weight = size / (size + block_data['size'])
    autoencoder.federate_from_bytes(block_data['model_bytes'],weight)
    response['after'] = evaluate_model(autoencoder, dataset.test,block_data)   
    host_ip = socket.gethostbyname(socket.gethostname()) 
    client_ip = request.remote_addr
    if abs(response['before'] - response['after']) < config.THRESHOLD:
        return response, 200
    else:
        model_tx = ModelTransaction(autoencoder.to_bytes(), mean, std,size+block_data['size'],host_ip,client_ip )
        blockchain.add_transaction(model_tx)
        blockchain.mine_block()
        return response, 200
    # model_tx = ModelTransaction(autoencoder.to_bytes(), mean, std,size+block_data['size'],host_ip,client_ip )
    # blockchain.add_transaction(model_tx)
    # blockchain.mine_block()
    return response, 200

blockchain = Blockchain()


def receive_public_key():
    response = requests.get(config.relayChain+'/get_public_key',verify=False)
    with open('./keys/public_key.pem', 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    dataset  = load_dataset(config.initialTrain,config.Test,config.BATCH_SIZE)
    
    size,mean,std = localStatistics(dataset.train)
    try:
        model = ModelConfig.__dict__[config.ModeName]
    except KeyError:
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    global_model = model(config.INPUT_SIZE, config.NUM_CLASSES )
    train_model(global_model, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE,mean,std)
    model_tx = ModelTransaction(global_model.to_bytes(),mean, std,size )
    blockchain.add_transaction(model_tx)
    blockchain.mine_block()
    app.run(host='0.0.0.0',ssl_context=(config.certificate,config.private_key),port=3001,debug=config.DEBUG)
    

