import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from config import *


class FederatedModel(nn.Module):

    def copy_from(self, other):
        """
        Cop model paramateres from other model to this.
        """
        global_param = other.parameters()
        local_param = self.parameters()
        for local_t, global_t in zip(local_param, global_param):
            local_t.detach().copy_(global_t)

    def zero(model):
        for param in model.parameters():
            param.detach().zero_()

    def add(self, other):
        for a_t, b_t in zip(self.parameters(), other.parameters()):
            a_t.detach().add_(b_t)

    def print(self):
        for param in self.parameters():
            print(f"params: {param}")

    def divide(self, divisor):
        for param in self.parameters():
            param.detach().mul_(1.0/divisor)

    def to_bytes(self):
        bytestr = b''
        for param in self.parameters():
            arr = param.detach().numpy().astype(EXTERNAL_DTYPE.numpy)
            bytestr += arr.tobytes()
        return bytestr

    def from_bytes(self, bytestr: bytes):
        for param in self.parameters():
            arr = param.detach().numpy()
            bytesize = arr.size * EXTERNAL_DTYPE.size
            arr[:] = np.frombuffer(bytestr[:bytesize], dtype=EXTERNAL_DTYPE.numpy).reshape(arr.shape)
            bytestr = bytestr[bytesize:]
        assert(len(bytestr) == 0)
        return bytestr

    def federate_from_bytes(self, bytestr: bytes, weight):
        for param in self.parameters():
            arr = param.detach().numpy()
            bytesize = arr.size * EXTERNAL_DTYPE.size
            arr += weight * np.frombuffer(bytestr[:bytesize], dtype=EXTERNAL_DTYPE.numpy).reshape(arr.shape)
            bytestr = bytestr[bytesize:]
        assert(len(bytestr) == 0)
        return bytestr




def combine_means(means: list):
    N = sum([x for x, y in means])
    total = np.sum(np.concatenate([n*mean for n, mean in means]), axis=0, keepdims=True)
    return total / N

def combine_stds(var: list):
    N = sum([x for x, y in var])
    total = np.sum(np.concatenate([n*mean for n, mean in var]), axis=0, keepdims=True)
    return np.sqrt(total / N)

