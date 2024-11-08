import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image, ImageFile
from torchvision import transforms

ImageFile.LOAD_TRUNCATED_IMAGES = True

class ParametersDataset(Dataset):
    def __init__(
        self,
        data,                      # Pass balanced data as a DataFrame
        root_dir,
        image_dim=(320, 320),
        pre_crop_transform=None,
        post_crop_transform=None,
        layer_height=False,
        extrusion=False,
        per_img_normalisation=False,
    ):
        self.dataframe = data  # Use directly provided DataFrame
        self.root_dir = root_dir
        self.pre_crop_transform = pre_crop_transform
        self.post_crop_transform = post_crop_transform
        self.image_dim = image_dim
        self.use_layer_height = layer_height
        self.use_extrusion = extrusion
        self.per_img_normalisation = per_img_normalisation
        self.targets = []

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        self.targets = []
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Load the image path and coordinates
        img_name = os.path.join(self.root_dir, self.dataframe.img_path.iloc[idx])

        # Calculate crop box around the nozzle tip
        dim = self.image_dim[0] / 2
        left = self.dataframe.nozzle_tip_x.iloc[idx] - dim
        top = self.dataframe.nozzle_tip_y.iloc[idx] - dim
        right = self.dataframe.nozzle_tip_x.iloc[idx] + dim
        bottom = self.dataframe.nozzle_tip_y.iloc[idx] + dim

        # Open and preprocess the image
        image = Image.open(img_name)
        if self.pre_crop_transform:
            image = self.pre_crop_transform(image)
        image = image.crop((left, top, right, bottom))

        # Apply normalization (either per-image or using preset transforms)
        if self.per_img_normalisation:
            tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor()])
            image = tfms(image)
            mean = torch.mean(image, dim=[1, 2])
            std = torch.std(image, dim=[1, 2])
            image = transforms.Normalize(mean, std)(image)
        else:
            if self.post_crop_transform:
                image = self.post_crop_transform(image)

        # Retrieve targets for layer height and extrusion if specified
        if self.use_layer_height:
            layer_height_class = int(self.dataframe.layer_height_class.iloc[idx])
            self.targets.append(layer_height_class)
        if self.use_extrusion:
            extrusion_class = int(self.dataframe.extrusion_class.iloc[idx])
            self.targets.append(extrusion_class)

        y = torch.tensor(self.targets, dtype=torch.long)
        return image, y
