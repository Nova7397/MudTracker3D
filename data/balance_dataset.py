import pandas as pd
from sklearn.utils import resample
import torch
from torch.utils.data import random_split

def balance_dataset(csv_file, target_col_1, target_col_2, train_ratio=0.7, val_ratio=0.2):
    data = pd.read_csv(csv_file)
    
    # Define the combinations and balance settings for upsampling or downsampling
    target_combinations = [
        (1, 1), (1, 2), (2, 2), (2, 1), (1, 0)
    ]
    target_counts = { # target number for each combination
        (1, 1): int(len(data) * 0.2),
        (1, 2): int(len(data) * 0.27),
        (2, 2): int(len(data) * 0.25),
        (2, 1): int(len(data) * 0.28),
        (1, 0): int(len(data) * 0.3)
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

    # Split data into train, val, test
    train_size = int(len(balanced_data) * train_ratio)
    val_size = int(len(balanced_data) * val_ratio)
    test_size = len(balanced_data) - train_size - val_size

    train_data, val_data, test_data = random_split(balanced_data, [train_size, val_size, test_size])

    # Calculate weights for each class
    counts = balanced_data.groupby([target_col_1, target_col_2]).size()
    weights = 1.0 / counts.values
    class_weights = torch.tensor(weights, dtype=torch.float)

    return train_data, val_data, test_data, class_weights
