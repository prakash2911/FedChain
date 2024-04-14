import torch
import torch.nn as nn
import torch.optim as optim


import torch
import torch.nn as nn
import torch.optim as optim

def train_model(model, train_loader, num_epochs, learning_rate, mean, standard_deviation):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Convert mean and standard deviation to tensors
   
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, targets in train_loader:
            # Normalize the input data using Z-score normalization
            inputs_normalized = (inputs - mean) / standard_deviation
            
            optimizer.zero_grad()
            outputs, classifications = model(inputs_normalized)
            loss = criterion(classifications, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
        
        epoch_loss = running_loss / len(train_loader.dataset)
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}')


# Define the evaluation function
def evaluate_model(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, targets in test_loader:
            _, classifications = model(inputs)
            predicted = torch.argmax(classifications, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
    accuracy = correct / total
    print(f'Accuracy: {accuracy:.4f}')
