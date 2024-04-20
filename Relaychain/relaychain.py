from flask import Flask, request, jsonify,send_file
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import config

app = Flask(__name__)

# Load keys
with open('./keys/private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )



@app.route('/get_public_key', methods=['GET'])
def get_public_key():
    with open('./keys/public_key.pem', 'rb') as f:
        public_key = f.read()

    return send_file(
        './keys/public_key.pem',
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='public_key.pem'
    )
    
@app.route('/verify_decrypt_and_read', methods=['POST'])
def verify_decrypt_and_read():
    try:
        encrypted_aes_key = bytes.fromhex(request.json['encrypted_aes_key'])
        iv = bytes.fromhex(request.json['iv'])
        encrypted_data = bytes.fromhex(request.json['encrypted_data'])
        # Decrypt AES key with RSA
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(aes_key)
        # Decrypt data with AES
        ciphertext = encrypted_data[:-16]  # Exclude the last 16 bytes for the authentication tag
        tag = encrypted_data[-16:]  # Get the last 16 bytes as the authentication tag
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return jsonify({'decrypted_data': decrypted_data.decode()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    
if __name__ == '__main__':
    app.run(ssl_context=(config.certificate,config.private_key),debug=True)