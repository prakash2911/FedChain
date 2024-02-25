import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from FederatedModel import *
from config import *

from log import log

class FL:
    LossFunc = None
    Xdtype = INTERNAL_DTYPE.numpy
    # will be set by driver function
    Xfeatures = None

    class User:
        def __init__(self, account, model):
            self.account = account
            self.model = model


    class Client(User):
        """
        Each FL Client is responsible for the following functions in blockchain:
        1. Keep track of the latest model in blockchain.
        2. Backpropagate this global model with the private dataset.
        3. Report the updates back to the blockchain.
        """

        count = 0
        def __init__(self, account, model, dataloader):

            super(FL.Client, self).__init__(account, model)
            self.dataloader = dataloader
            account.obtainContract()
            self.index = FL.Client.count
            FL.Client.count += 1

        def localMeans(self):

            X = torch.cat([x for x, y in self.dataloader])
            size = X.shape[0]
            mean = X.mean(0, keepdim=True)
            # Commit to blockchain
            tx_receipt = self.account.localMeans(size, mean.numpy().tobytes())
            return tx_receipt

        def getMeans(self):

            # NOTE: using Tensor instead of tensor gives a warning about non-writable
            self.means = torch.tensor(np.frombuffer(self.account.getMeans(), dtype=FL.Xdtype).reshape((1, FL.Xfeatures)))

        def localStds(self):

            X = torch.cat([x for x, y in self.dataloader])
            size = X.shape[0]
            stds = (X - self.means).square().mean(0, keepdim=True)
            # Commit to blockchain
            tx_receipt = self.account.localStds(size, stds.numpy().tobytes())
            return tx_receipt

        def getStds(self):

            self.stds = torch.tensor(np.frombuffer(self.account.getStds(), dtype=FL.Xdtype).reshape((1, FL.Xfeatures)))
            # Handle 0 stds to avoid division by zero
            self.stds[self.stds == 0.0] = 1.0

        def localUpdate(self):

            # Load the latest model from blockchain
            epoch = self.account.getEpoch()
            modelBytes = self.account.getModel()
            self.model.from_bytes(modelBytes)

            datasize = 0
            for X, y in self.dataloader:
                datasize += X.shape[0]

            train_loss = 0.0

            global LOCAL_EPOCHS, LEARNING_RATE, MOMENTUM
            optimizer = torch.optim.SGD(self.model.parameters(), lr=LEARNING_RATE, momentum=MOMENTUM)
            for i in range(LOCAL_EPOCHS):
                for batch, (X, y) in enumerate(self.dataloader):
                    normX = (X - self.means) / self.stds
                    pred = self.model(normX)
                    loss = FL.LossFunc(pred, y)
                    train_loss += loss.item()

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

            # len(dataloader) == number of batches
            loss = train_loss / (len(self.dataloader) * LOCAL_EPOCHS)
            log.info(f"FL Client {self.index} local loss: {loss}")

            # Commit to blockchain
            tx_receipt = self.account.localUpdate(epoch, datasize, self.model.to_bytes())

            return tx_receipt


    class Server(User):

        def __init__(self, account, model):
            super(FL.Server, self).__init__(account, model)
            account.deploy(model.to_bytes())

        def combineMeans(self, receipts):
            means = combine_means([
                (n, np.frombuffer(byteMeans, dtype=FL.Xdtype).reshape((1, FL.Xfeatures)))
                for n, byteMeans in self.account.getMeanEvents(receipts)
                ]).astype(FL.Xdtype)
            tx_receipt = self.account.globalMeans(means.tobytes())
            return tx_receipt

        def combineStds(self, receipts):
            stds = combine_stds([
                (n, np.frombuffer(byteMeans, dtype=FL.Xdtype).reshape((1, FL.Xfeatures)))
                for n, byteMeans in self.account.getStdEvents(receipts)
                ]).astype(FL.Xdtype)
            tx_receipt = self.account.globalStds(stds.tobytes())
            return tx_receipt

        def skipPreprocess(self):
            means = np.zeros((1, FL.Xfeatures), dtype=FL.Xdtype)
            stds = np.ones((1, FL.Xfeatures), dtype=FL.Xdtype)
            self.account.globalMeans(means.tobytes())
            self.account.globalStds(stds.tobytes())

        def averageUpdates(self, receipts):
            epoch = self.account.getEpoch()
            totalDataSize = self.account.getDataSize()
            log.info(f"Averaging model from {len(receipts)} local update(s)...")
            self.model.zero()
            for size, modelBytes in self.account.getUpdateEvents(receipts):
                # Weight of each update should be proportional to the dataset size
                weight = size / totalDataSize
                self.model.federate_from_bytes(modelBytes, weight)
            # Model is now ready
            # Update model on blockchain
            tx_receipt = self.account.globalUpdate(self.model.to_bytes())
            log.info(f"Epoch {epoch} finished and committed to blockchain.")

            return tx_receipt

        def getModel(self):
            modelBytes = self.account.getModel()
            self.model.from_bytes(modelBytes)
            return self.model

