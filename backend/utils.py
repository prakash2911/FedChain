
import numpy as np
import torch
import pickle

def Combinded_Mean(means, size, Gmean, Gsize):
    total = np.multiply(means, size) + np.multiply(Gmean, Gsize)
    final = total / (size + Gsize)
    return final

def Combinded_Std(stds, size, Gstd, Gsize):
    total = np.square(stds)*size + np.square(Gstd)*Gsize
    total = total/(Gsize+size)
    return np.sqrt(total)


def localStatistics(dataset):
    X = torch.cat([x for x, y in dataset])
    mean = X.mean(0, keepdim=True)
    stds = (X - mean).square().mean(0, keepdim=True)
    size = X.shape[0]
    return size,mean,stds


def save_dataset(dataset, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(dataset, f)