# https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt
import os
import pandas as pd
from torchvision.io import read_image


class CustomImageDataset(Dataset):
    def __init__(self, img_dir, transform=None, target_transform=None):
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

        # Scan all subfolders to get class names
        self.classes = sorted(entry.name for entry in os.scandir(img_dir) if entry.is_dir())
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}
        
        # Build list of (image_path, label)
        self.samples = []
        for cls_name in self.classes:
            cls_folder = os.path.join(img_dir, cls_name) # variable with path to the classes
            
            for fname in os.listdir(cls_folder):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    path = os.path.join(cls_folder, fname) # path for each image
                    label = self.class_to_idx[cls_name] # id that belong to the image
                    self.samples.append((path, label)) # image path with the class id

    def __len__(self): # returns the number of samples in the dataset
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = read_image(img_path) # convert image into a tensor

        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label, img_path


class InferenceImageDataset(Dataset):
    def __init__(self, img_dir, transform=None):
        self.img_dir = img_dir
        self.transform = transform

        self.samples = []
        for fname in os.listdir(img_dir):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(img_dir, fname)
                self.samples.append(path)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path = self.samples[idx]
        image = read_image(img_path)

        if self.transform:
            image = self.transform(image)

        return image, img_path