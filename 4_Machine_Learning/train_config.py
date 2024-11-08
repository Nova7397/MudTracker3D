import os
from datetime import datetime
import numpy as np
import torch
from pytorch_lightning import seed_everything
from torchvision import transforms
import pandas as pd
from matplotlib import pyplot as plt


DATE = datetime.now().strftime("%d%m%Y")

dataset_switch = 1


DATA_DIR = r"D:\MUDTRACKER3D\MudTracker3D\4_Machine_Learning\dataset" 

print(f"DATA_DIR: {DATA_DIR}")

if dataset_switch == 0:
    DATASET_NAME = "dataset_test"
    DATA_CSV = os.path.join(
        DATA_DIR,
        "balanced_dataset_300_per_combination.csv",
    )
    DATASET_MEAN = [0.16853632, 0.17632364, 0.10495131]
    DATASET_STD = [0.05298341, 0.05527821, 0.04611006]
elif dataset_switch == 1:
    DATASET_NAME = "full_dataset"
    DATA_CSV = os.path.join(
        DATA_DIR,
        "final_dataset_full_filteredA1&B1.csv",
    )
    DATASET_MEAN = [0.2915257, 0.27048784, 0.14393276]
    DATASET_STD = [0.066747, 0.06885352, 0.07679665]


INITIAL_LR = 0.001

BATCH_SIZE = 64 #32
MAX_EPOCHS = 40 #50

NUM_NODES = 1
NUM_GPUS = 1
ACCELERATOR = "gpu"


def set_seed(seed):
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True
    seed_everything(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)


def make_dirs(path):
    try:
        os.makedirs(path)
    except:
        pass

preprocess = transforms.Compose(
    [
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.2915257, 0.27048784, 0.14393276],
            [0.2915257, 0.27048784, 0.14393276],
        )
    ],
)