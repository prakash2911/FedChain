class DummyPlatform:
    modelBytes = None
    epoch = 0
    dataSize = 0
    means = None
    stds = None

    @staticmethod
    def initAccounts(amount: int):
        return [DummyPlatform.Account() for i in range(amount)]

    class Account:
        def deploy(self, modelBytes):
            DummyPlatform.modelBytes = modelBytes

        def obtainContract(self):
            pass

        def getUpdateEvents(self, receipts):
            return receipts

        def getMeanEvents(self, receipts):
            return receipts

        def getStdEvents(self, receipts):
            return receipts

        def globalUpdate(self, modelBytes):
            DummyPlatform.modelBytes = modelBytes
            DummyPlatform.epoch += 1
            DummyPlatform.dataSize = 0
            return None

        def localUpdate(self, *vargs):
            DummyPlatform.dataSize += vargs[1]
            return (vargs[1], vargs[2])

        def globalMeans(self, means):
            DummyPlatform.means = means
            return None

        def localMeans(self, *vargs):
            return (vargs[0], vargs[1])

        def globalStds(self, stds):
            DummyPlatform.stds = stds
            return None

        def localStds(self, *vargs):
            return (vargs[0], vargs[1])

        # The following public accessor functions don't need to use account
        def getModel(self):
            return DummyPlatform.modelBytes

        def getEpoch(self):
            return DummyPlatform.epoch

        def getDataSize(self):
            return DummyPlatform.dataSize

        def getMeans(self):
            return DummyPlatform.means

        def getStds(self):
            return DummyPlatform.stds
