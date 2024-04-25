import torch
from sklearn.metrics import precision_score, recall_score, f1_score



def evaluate_model(model, test_loader, block_data=None):
    model.eval()
    correct = 0
    total = 0
    predicted_list = []
    targets_list = []
      
    with torch.no_grad():
        for inputs, targets in test_loader:
            classifications = model(inputs.float())
            predicted = torch.argmax(classifications, 1)
            
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
            
            predicted_list.extend(predicted.cpu().numpy())
            targets_list.extend(targets.cpu().numpy())
    
    accuracy = correct / total
    precision = precision_score(targets_list, predicted_list, average='binary')
    recall = recall_score(targets_list, predicted_list, average='binary')
    f1 = f1_score(targets_list, predicted_list, average='binary')
    print(f'Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}')
    return accuracy, precision, recall, f1
