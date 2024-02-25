from FederatedModel import FederatedModel
from torch import nn
import torch.nn.functional as F
import itertools


class LinearModel(FederatedModel):
    def __init__(self, num_features, num_labels, args):
        super().__init__()
        self.fc1 = nn.Linear(num_features, num_labels)

    def forward(self, x):
        x = self.fc1(x)
        return x


class SingleLayer(FederatedModel):
    def __init__(self, num_features, num_labels, args):
        super().__init__()
        n = args.getint("neuron count")
        self.fc1 = nn.Linear(num_features, n)
        self.fc2 = nn.Linear(n, num_labels)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
