import hashlib
import time
import json

class ModelTransaction:
    def __init__(self, model_bytes, mean=[], std_dev=[],size=0,host_ip='',client_ip=''):
        self.model_bytes = model_bytes
        self.mean = mean
        self.std_dev = std_dev
        self.size = size
        self.from_address = self.ip_to_eth_address(host_ip)
        self.to_address = self.ip_to_eth_address(client_ip)

    def to_dict(self):
        return {
            'model_bytes': self.model_bytes,
            'mean': self.mean,
            'std_dev': self.std_dev,
            'size': self.size,
        }
    def ip_to_eth_address(self,ip_address):
        ip_bytes = ip_address.encode()
        hashed_ip = hashlib.sha256(ip_bytes).digest()
        eth_address_bytes = hashed_ip[:20]
        eth_address = '0x' + eth_address_bytes.hex()
        return eth_address

class Block:
    def __init__(self, transactions, previous_hash,block_number,from_address,to_address,gas_used=30000):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.block_number = block_number+1
        self.gas_used = gas_used
        self.from_address =  from_address
        self.to_address = to_address
        self.type = '0x2'
        self.status = 1
        self.contract_address = ''
        self.logs = ()
        self.hash = self.calculate_hash()
       
        
        
        
    def calculate_hash(self):
        transaction_dicts = [tx.to_dict() for tx in self.transactions]
        block_data = json.dumps({
            'transactions': transaction_dicts,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'block_number': self.block_number,
            'gas_used': self.gas_used,
            'contract_address': self.contract_address,
            'logs':self.logs,
            'type': self.type,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'status': self.status
        }, sort_keys=True).encode()
        return hashlib.sha256(block_data).hexdigest()
    

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block([], '0' * 64,0,0,'0x','0x')
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def mine_block(self):
        last_block = self.chain[-1]
        new_block = Block(self.transactions, last_block.hash,last_block.block_number,last_block.from_address,last_block.to_address)
        self.chain.append(new_block)
        self.transactions = []

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


