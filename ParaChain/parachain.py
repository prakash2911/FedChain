from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
import ModelConfig
from config import config 
from utils import *
from dataPreProcess import load_dataset,load_test_dataset
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from model import *
import sys
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    return jsonify({}), 200

@app.route('/send_data', methods=['POST'])
@cross_origin()
def send_data():
    global blockchain
    res = requests.post(config.blockchain+'/send_last_block',verify=False).json()
    with open('./keys/public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(bytes.fromhex(res['model_bytes'])) + encryptor.finalize()
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
    
    return jsonify({"message": "bruh"}), res.status_code    


@app.route('/testmodel', methods=['GET','POST'])
@cross_origin()
def evaluated():
    res = requests.post(config.blockchain+'/send_last_block',verify=False)
    model = ModelConfig.__dict__[config.ModeName]
    model= model(config.INPUT_SIZE,config.NUM_CLASSES)
    model.from_bytes(bytes.fromhex(res.json()['model_bytes']))
    dataset = load_test_dataset(config.Test,config.BATCH_SIZE)
    response = {}
    response['accuracy'] = evaluate_model(model, dataset.test)
    return jsonify(response), 200


@app.route('/blocks', methods=['GET'])
@cross_origin()
def get_blocks():
    res = requests.get(config.blockchain+'/blocks',verify=False)
    return res.json(), res.status_code


@app.route('/localupdate', methods=['GET','POST'])
@cross_origin()
def localUpdate():
    global blockchain
    data = request.get_json()
    dataset  = load_dataset(f'{config.Train}/{data["dataset"]}',config.Test,config.BATCH_SIZE)
    response = {}
    size,mean,std = localStatistics(dataset.train)
    block_data = requests.post(config.blockchain+'/send_last_block',verify=False).json()
    try:
        model = ModelConfig.__dict__[config.ModeName]
    except KeyError:
        sys.exit(1)
    gobal_model = model(config.INPUT_SIZE, config.NUM_CLASSES )
    gobal_model.from_bytes(bytes.fromhex(block_data['model_bytes']))
    response['before'] = evaluate_model(gobal_model, dataset.test,block_data)
    mean = Combined_Mean(mean, size ,block_data['mean'],block_data['size']) 
    std = Combined_Std(std, size, block_data['std_dev'], block_data['size'])
    autoencoder = model(config.INPUT_SIZE,config.NUM_CLASSES)
    train_model(autoencoder, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE, mean, std)
    weight = size / (size + block_data['size'])
    autoencoder.federate_from_bytes(bytes.fromhex(block_data['model_bytes']),weight)
    response['after'] = evaluate_model(autoencoder, dataset.test,block_data)   
    
    if (response['before'] - response['after']) > config.THRESHOLD:
        return response, 200
    else:
        send_data ={
            'model_bytes':autoencoder.to_bytes().hex(),
            'mean':mean.tolist(),
            'std':std.tolist(),
            'size':size + block_data['size']
            
        }
        res = requests.post(config.blockchain+'/receive_data',json=send_data,verify=False)     
        return response, res.status_code


def receive_public_key():
    response = requests.get(config.relayChain+'/get_public_key',verify=False)
    with open('./keys/public_key.pem', 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=(config.certificate,config.private_key),port=3001,debug=config.DEBUG)
    
