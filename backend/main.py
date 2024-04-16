from flask import Flask, jsonify, request
import ModelConfig
from config import config 
from utils import *
from dataPreProcess import load_dataset
from Blockchain import Blockchain, ModelTransaction,Block
from model import *
import sys
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
    gobal_model = model(config.INPUT_SIZE, config.NUM_CLASSES, config.ENCODING_SIZE)
    gobal_model.from_bytes(block_data['model_bytes'])
    response['before'] = evaluate_model(gobal_model, dataset.test,block_data)
    mean = Combined_Mean(mean, size ,block_data['mean'],block_data['size']) 
    std = Combined_Std(std, size, block_data['std_dev'], block_data['size'])
    autoencoder = model(config.INPUT_SIZE,config.NUM_CLASSES,config.ENCODING_SIZE)
    train_model(autoencoder, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE, mean, std)
    weight = size / (size + block_data['size'])
    autoencoder.federate_from_bytes(block_data['model_bytes'],weight)
    response['after'] = evaluate_model(autoencoder, dataset.test,block_data)    
    model_tx = ModelTransaction(autoencoder.to_bytes(), mean, std,size+block_data['size'] )
    blockchain.add_transaction(model_tx)
    blockchain.mine_block()
    
    return response, 200

blockchain = Blockchain()
if __name__ == "__main__":
    dataset  = load_dataset(config.initialTrain,config.Test,config.BATCH_SIZE)
    size,mean,std = localStatistics(dataset.train)
    try:
        model = ModelConfig.__dict__[config.ModeName]
    except KeyError:
        sys.exit(1)
    
    global_model = model(config.INPUT_SIZE, config.NUM_CLASSES , config.ENCODING_SIZE)
    train_model(global_model, dataset.train, config.NUM_EPOCHS, config.LEARNING_RATE,mean,std)
    model_tx = ModelTransaction(global_model.to_bytes(),mean, std,size )
    blockchain.add_transaction(model_tx)
    blockchain.mine_block()
    app.run(host='0.0.0.0',debug=config.DEBUG)

