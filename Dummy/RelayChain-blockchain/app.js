const express = require('express');
const bodyParser = require('body-parser');
const { Gateway, Wallets } = require('fabric-network');
const path = require('path');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());

// Endpoint to store data on the blockchain
app.post('/send_last_block', async (req, res) => {
    try {
        const { key, value } = req.body;

        const ccpPath = path.resolve(__dirname, '..', 'fabric-samples', 'test-network', 'organizations', 'peerOrganizations', 'org1.example.com', 'connection-org1.json');

        const gateway = new Gateway();
        await gateway.connect(ccpPath, {
            wallet: Wallets.newFileSystemWallet(path.join(__dirname, 'wallet')),
            identity: 'user1',
            discovery: { enabled: true, asLocalhost: true }
        });

        const network = await gateway.getNetwork('mychannel');
        const contract = network.getContract('mychaincode');

        await contract.submitTransaction('StoreData', key, value);

        await gateway.disconnect();

        res.status(200).json({ message: 'Data stored successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Error storing data', error: error.message });
    }
});

// Endpoint to retrieve data from the blockchain
app.get('/receive_data/:key', async (req, res) => {
    try {
        const key = req.params.key;

        const ccpPath = path.resolve(__dirname, '..', 'fabric-samples', 'test-network', 'organizations', 'peerOrganizations', 'org1.example.com', 'connection-org1.json');

        const gateway = new Gateway();
        await gateway.connect(ccpPath, {
            wallet: Wallets.newFileSystemWallet(path.join(__dirname, 'wallet')),
            identity: 'user1',
            discovery: { enabled: true, asLocalhost: true }
        });

        const network = await gateway.getNetwork('mychannel');
        const contract = network.getContract('mychaincode');

        const result = await contract.evaluateTransaction('RetrieveData', key);

        await gateway.disconnect();

        res.status(200).json({ data: result.toString() });
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving data', error: error.message });
    }
});

// Start the Express server
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});