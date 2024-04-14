from flask import Flask, jsonify, request,Response
import numpy as np
from ModelConfig import AutoencoderWithClassifier
from config import config 
from utils import *
from dataPreProcess import load_dataset
from Blockchain import Blockchain, ModelTransaction,Block
from model import *
app = Flask(__name__)

@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.mine_pending_transactions()
    response = {'message': 'Block mined successfully!'}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.to_dict())
    response = {'chain': chain_data, 'length': len(chain_data)}
    return jsonify(response), 200


@app.route('/localupdate', methods=['GET','POST'])
def localUpdate():
    data = request.get_json()
    dataset  = load_dataset(config.Train,config.Test,data['percentage'],config.BATCH_SIZE)

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
    
    

    mean = Combinded_Mean(mean, size ,block_data['mean'],block_data['size']) 
    std = Combinded_Std(std, size, block_data['std_dev'], block_data['size'])
    autoencoder = AutoencoderWithClassifier(config.INPUT_SIZE, config.ENCODING_SIZE, config.NUM_CLASSES)
    train_model(autoencoder, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE, mean, std)
    weight = size / (size + block_data['size'])
    autoencoder.federate_from_bytes(block_data['model_bytes'],weight)
    # response = {'mean': mean.tolist(), 'std': std.tolist()}
    model_tx = ModelTransaction(autoencoder.to_bytes(), mean, std )
    blockchain.add_transaction(model_tx)
    blockchain.mine_block()
    last_block = blockchain.chain[-1]
    if last_block.transactions:
        last_transaction = last_block.transactions[-1]
        block_data = {
            'model_bytes':last_transaction.model_bytes,
            'mean': last_transaction.mean.tolist(),
            'std_dev': last_transaction.std_dev.tolist(),
            'size': last_transaction.size
        }
    
    return jsonify("Done"), 200

blockchain = Blockchain()
if __name__ == "__main__":
    global_model = AutoencoderWithClassifier(config.INPUT_SIZE, config.ENCODING_SIZE, config.NUM_CLASSES)
    model_tx = ModelTransaction(global_model.to_bytes(), np.zeros((1, 118), dtype=np.float64), np.zeros((1, 118), dtype=np.float64) )
    blockchain.add_transaction(model_tx)
    blockchain.mine_block()
    app.run(debug=True,host='0.0.0.0')

