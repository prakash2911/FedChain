import os
import pandas as pd
from sklearn.model_selection import train_test_split

def split_dataset(path, train_folder='dataset/train', test_folder='dataset/test', test_size=0.2):
    # Create folders if they don't exist
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Read the CSV dataset
    dataset = pd.read_csv(path)

    # Split dataset into training and testing sets
    train_data, test_data = train_test_split(dataset, test_size=test_size, random_state=0)

    train_data.to_csv(f"{train_folder}/train_data.csv", index=False)
    test_data.to_csv(f"{test_folder}/test_data.csv", index=False)


split_dataset('./dataset/nid.csv')
