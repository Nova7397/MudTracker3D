import pandas as pd
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
import torch

def balance_dataset(csv_file, target_col_1="layer_height_class", target_col_2="extrusion_class", train_ratio=0.7, val_ratio=0.2):
    data = pd.read_csv(csv_file)
    
    # Define target combinations and desired counts for balancing
    target_combinations = [
        (1, 1), (1, 2), (2, 2), (1, 0)
    ]
    target_counts = {  # desired number of samples for each combination
        (1, 1): int(len(data) * 0.25),   #0.2
        (1, 2): int(len(data) * 0.25),  #0.27
        (2, 2): int(len(data) * 0.25),   #0.25
        (1, 0): int(len(data) * 0.25)    #0.3
    }

    # Balance each group
    balanced_data = []
    for comb in target_combinations:
        subset = data[(data[target_col_1] == comb[0]) & (data[target_col_2] == comb[1])]
        if len(subset) > target_counts[comb]:
            subset_balanced = resample(subset, replace=False, n_samples=target_counts[comb])
        else:
            subset_balanced = resample(subset, replace=True, n_samples=target_counts[comb])
        balanced_data.append(subset_balanced)
    
    # Concatenate all balanced groups and shuffle
    balanced_data = pd.concat(balanced_data).sample(frac=1).reset_index(drop=True)


    # Split the balanced data into train, validation, and test sets using pandas

    test_ratio = 1 - train_ratio - val_ratio  # Implied as the remainder after train and validation

    # First, split into training and temporary sets
    train_data, temp_data = train_test_split(balanced_data, test_size=(1 - train_ratio), random_state=42)

    # Then split the temporary set into validation and test sets
    val_data, test_data = train_test_split(temp_data, test_size=test_ratio / (1 - train_ratio), random_state=42)
    
    # Calculate class weights for each class combination
    counts = balanced_data.groupby([target_col_1, target_col_2]).size()
    weights = 1.0 / counts.values
    class_weights = torch.tensor(weights, dtype=torch.float)

    # Return train, val, test datasets as DataFrames, along with the class weights
    return train_data, val_data, test_data, class_weights
