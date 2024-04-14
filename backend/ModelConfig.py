import torch.nn as nn
from FederatedLearning import FederatedModel
class AutoencoderWithClassifier(FederatedModel):
    def __init__(self, input_size, encoding_size, num_classes):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(True),
            nn.Linear(64, 32),
            nn.ReLU(True),
            nn.Linear(32, encoding_size),
        )
        self.classifier = nn.Sequential(
            nn.Linear(encoding_size, 16),
            nn.ReLU(True),
            nn.Linear(16, num_classes)
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_size, 32),
            nn.ReLU(True),
            nn.Linear(32, 64),
            nn.ReLU(True),
            nn.Linear(64, input_size),
            nn.Sigmoid()
        )
        self.model = nn.Sequential(self.encoder, self.classifier, self.decoder)

    def forward(self, x):
        x_encoded = self.model[0](x)
        x_classify = self.model[1](x_encoded)
        x_decoded = self.model[2](x_encoded)
        return x_decoded, x_classify
