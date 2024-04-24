from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import socket
from config import config
from utils import *
import ModelConfig
from model import *
import sys
from dataPreProcess import load_test_dataset
from web3 import Blockchain, ModelTransaction
app = Flask(__name__)
cors = CORS(app)

@app.route('/receive_data', methods=['POST'])
@cross_origin()
def receive_data():
    global Blockchain
    data = request.json
    client_ip = socket.gethostbyname(socket.gethostname()) 
    host_ip = request.remote_addr
    mtx = ModelTransaction(data['model_bytes'],data['mean'],data['std'],data['size'], host_ip, client_ip)
    Blockchain.add_transaction(mtx)
    Blockchain.mine_block()
    return jsonify(data), 200


@app.route('/send_last_block',methods=['POST'])
@cross_origin()
def send_data():
    global Blockchain
    last_block = Blockchain.chain[-1]
    if last_block.transactions:
        last_transaction = last_block.transactions[-1]
        block_data = {
            'model_bytes':last_transaction.model_bytes,
            'mean': last_transaction.mean,
            'std_dev': last_transaction.std_dev,
            'size': last_transaction.size
        }
        return jsonify(block_data), 200
    else:
        return jsonify({'message':'No transactions'}), 404

@app.route('/blocks', methods=['GET'])
@cross_origin()
def get_blocks():
    global Blockchain
    blocks_data = []
    for block in Blockchain.chain:
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
        'length': len(Blockchain.chain),
        'blocks': blocks_data
    }
    
    return jsonify(response), 200

Blockchain = Blockchain()
if __name__ == '__main__':
    dataset  = load_test_dataset(config.initialTrain,config.BATCH_SIZE)
    size,mean,std = localStatistics(dataset.test)
    try:
        model = ModelConfig.__dict__[config.ModeName]
    except KeyError:
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
    client_ip = '0' 
    host_ip =  '0'
    global_model = model(config.INPUT_SIZE, config.NUM_CLASSES )
    train_model(global_model, dataset.test, config.NUM_EPOCHS, config.LEARNING_RATE,mean,std)
    mtx = ModelTransaction(global_model.to_bytes().hex(),mean.tolist(),std.tolist(),size, host_ip, client_ip)
    Blockchain.add_transaction(mtx)
    Blockchain.mine_block()
    app.run(port=3000, debug=config.DEBUG, ssl_context=('./ssl/certificate.pem', './ssl/private_key.pem'))
    
    