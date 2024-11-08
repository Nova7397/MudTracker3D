import os
from torch.utils.data import DataLoader
import pytorch_lightning as pl
from torchvision import transforms
from PIL import ImageFile
from data.dataset_training import ParametersDataset
from data.balance_dataset_upsampling import balance_dataset
import torch.nn.functional as F
from torch import nn
import torch

ImageFile.LOAD_TRUNCATED_IMAGES = True

class ParametersDataModule(pl.LightningDataModule):
    def __init__(
        self,
        batch_size,
        data_dir,
        csv_file,
        dataset_name,
        mean,
        std,
        load_saved=False,
        transform=True,
        image_dim=(320, 320),
        per_img_normalisation=False,
        layer_height=True,
        extrusion=True,
    ):
        super().__init__()
        self.data_dir = data_dir
        self.dataset_name = dataset_name
        self.csv_file = csv_file
        self.batch_size = batch_size
        self.mean = mean
        self.std = std
        self.load_saved = load_saved
        self.transform = transform
        self.image_dim = image_dim
        self.per_img_normalisation = per_img_normalisation
        self.use_layer_height = layer_height
        self.use_extrusion = extrusion

        # Set up transformations
        if self.transform:
            self.pre_crop_transform = transforms.Compose(
                [
                    transforms.RandomRotation(10),
                    transforms.RandomPerspective(distortion_scale=0.1, p=0.1),
                ]
            )
            self.post_crop_transform = transforms.Compose(
                [
                    transforms.RandomResizedCrop(224, scale=(0.9, 1.0)),
                    transforms.RandomHorizontalFlip(),
                    transforms.ColorJitter(
                        brightness=0.1, contrast=0.1, hue=0.1, saturation=0.1
                    ),
                    transforms.ToTensor(),
                    transforms.Normalize(self.mean, self.std),
                ]
            )
        else:
            self.pre_crop_transform = None
            self.post_crop_transform = transforms.Compose(
                [
                    transforms.Resize(224),
                    transforms.ToTensor(),
                    transforms.Normalize(self.mean, self.std),
                ]
            )

    
    def setup(self, stage=None, save=True):
        # Balance and split the dataset using the revised function
        train_data, val_data, test_data, self.class_weights = balance_dataset(self.csv_file)

        # Use balanced and split datasets directly in ParametersDataset
        self.train_dataset = ParametersDataset(
            data=train_data,
            root_dir=self.data_dir,
            image_dim=self.image_dim,
            pre_crop_transform=self.pre_crop_transform,
            post_crop_transform=self.post_crop_transform,
            layer_height=self.use_layer_height,
            extrusion=self.use_extrusion,
            per_img_normalisation=self.per_img_normalisation,
        )

        self.val_dataset = ParametersDataset(
            data=val_data,
            root_dir=self.data_dir,
            image_dim=self.image_dim,
            pre_crop_transform=self.pre_crop_transform,
            post_crop_transform=self.post_crop_transform,
            layer_height=self.use_layer_height,
            extrusion=self.use_extrusion,
            per_img_normalisation=self.per_img_normalisation,
        )

        self.test_dataset = ParametersDataset(
            data=test_data,
            root_dir=self.data_dir,
            image_dim=self.image_dim,
            pre_crop_transform=self.pre_crop_transform,
            post_crop_transform=self.post_crop_transform,
            layer_height=self.use_layer_height,
            extrusion=self.use_extrusion,
            per_img_normalisation=self.per_img_normalisation,
        )
         
        train_size, val_size, test_size = int(len(self.train_dataset)), int(len(self.val_dataset)), int(len(self.test_dataset))

        if save:
            try:
                os.makedirs("data/{}/".format(self.dataset_name))
            except:
                pass
            torch.save(self.train_dataset, "data/{}/train.pt".format(self.dataset_name))
            torch.save(self.val_dataset, "data/{}/val.pt".format(self.dataset_name))
            torch.save(self.test_dataset, "data/{}/test.pt".format(self.dataset_name))


        if stage == "fit" or stage is None:
            if self.load_saved:
                self.train_dataset, self.val_dataset = torch.load(
                    "data/{}/train.pt".format(self.dataset_name)
                ), torch.load("data/{}/val.pt".format(self.dataset_name))

        # Assign test dataset for use in dataloader(s)
        if stage == "test" or stage is None:
            if self.load_saved:
                self.test_dataset = torch.load(
                    "data/{}/test.pt".format(self.dataset_name)
                )
          

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            num_workers=0,
            pin_memory=True,
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            num_workers=0,
            pin_memory=True,
        )
