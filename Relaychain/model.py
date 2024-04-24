import torch

def evaluate_model(model, test_loader,block_data=None):
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, targets in test_loader:
            classifications = model(inputs.float())
            predicted = torch.argmax(classifications, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
    accuracy = correct / total
    return accuracy