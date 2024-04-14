# config.py

import os
class config:
    DEBUG = False
    NUM_EPOCHS = int(os.environ.get('NUM_EPOCHS', 10))
    LEARNING_RATE = float(os.environ.get('LEARNING_RATE', 0.001))
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 64))
    TEST_SIZE = float(os.environ.get('TEST_SIZE', 0.2))
    INPUT_SIZE = 118
    ENCODING_SIZE = 20
    NUM_CLASSES = 2
    Train= 'dataset/train/train_data.csv'
    Test= 'dataset/test/test_data.csv'
    DatasetPath='dataset/DatasetPKL/'
