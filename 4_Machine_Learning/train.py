import os
import argparse
import pytorch_lightning as pl
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning.callbacks import ModelCheckpoint
from data.data_module_training import ParametersDataModule
from model.network_module import ParametersClassifier

from train_config import *

def set_seed(seed):
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True
    pl.seed_everything(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)

def make_dirs(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory {path}: {e}")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s", "--seed", default=1234, type=int, help="Set seed for training"
    )
    parser.add_argument(
        "-e",
        "--epochs",
        default=MAX_EPOCHS,
        type=int,
        help="Number of epochs to train the model for",
    )

    args = parser.parse_args()
    seed = args.seed

    set_seed(seed)
    logs_dir = os.path.join("logs", f"logs-{DATE}", f"{seed}")
    logs_dir_default = os.path.join(logs_dir, "default")

    make_dirs(logs_dir)
    make_dirs(logs_dir_default)

    tb_logger = pl_loggers.TensorBoardLogger(logs_dir)
    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        dirpath=os.path.join("checkpoints", DATE, str(seed)),
        filename=f"MHResAttNet-{DATASET_NAME}-{DATE}-{{epoch:02d}}-{{val_loss:.2f}}-{{val_acc:.2f}}",
        save_top_k=3,
        mode="min",
    )


    model = ParametersClassifier(
        num_classes=3,
        lr=INITIAL_LR,
        transfer=False,

    )

    
    data = ParametersDataModule(
        batch_size=BATCH_SIZE,
        data_dir=DATA_DIR,
        csv_file=DATA_CSV,
        dataset_name=DATASET_NAME,
        mean=DATASET_MEAN,
        std=DATASET_STD,
    )

    
    if torch.cuda.is_available():
        available_gpus = torch.cuda.device_count()
        print(f"Detected {available_gpus} available GPU.")
        gpus = min(NUM_GPUS, available_gpus)
       
        trainer = pl.Trainer(
            num_nodes=NUM_NODES,
            gpus=gpus,
            accelerator='gpu',
            max_epochs=args.epochs,
            logger=tb_logger,
            weights_summary=None,
            precision=16,
            callbacks=[checkpoint_callback],
        )
    else:
        print("No GPU detected, using CPU for training.")
        trainer = pl.Trainer(
            num_nodes=NUM_NODES,
            gpus=0,
            accelerator=None,
            max_epochs=args.epochs,
            logger=tb_logger,
            weights_summary=None,
            precision=16,
            callbacks=[checkpoint_callback],
        )


    trainer.fit(model, data)

if __name__ == "__main__":
    main()


