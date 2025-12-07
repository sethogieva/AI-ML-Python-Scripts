import os
import json
import argparse
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models


def train(data_dir, output_dir, epochs=5, batch_size=32, lr=1e-4, device=None):
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ImageNet normalization
    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    val_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dir = data_dir / 'train'
    val_dir = data_dir / 'val'
    assert train_dir.exists(), f"Train folder not found: {train_dir}"

    train_dataset = datasets.ImageFolder(str(train_dir), transform=train_transforms)
    val_dataset = datasets.ImageFolder(str(val_dir), transform=val_transforms) if val_dir.exists() else None

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4) if val_dataset else None

    num_classes = len(train_dataset.classes)
    print(f'Classes: {train_dataset.classes}')

    model = models.resnet18(pretrained=True)
    # Replace final layer
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=lr)

    best_acc = 0.0
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total = 0
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            running_corrects += (preds == labels).sum().item()
            total += images.size(0)

        epoch_loss = running_loss / total
        epoch_acc = running_corrects / total
        print(f'Epoch {epoch+1}/{epochs} - loss: {epoch_loss:.4f} acc: {epoch_acc:.4f}')

        if val_loader:
            model.eval()
            val_corrects = 0
            val_total = 0
            with torch.no_grad():
                for images, labels in val_loader:
                    images = images.to(device)
                    labels = labels.to(device)
                    outputs = model(images)
                    preds = outputs.argmax(dim=1)
                    val_corrects += (preds == labels).sum().item()
                    val_total += images.size(0)
            val_acc = val_corrects / val_total
            print(f' Validation acc: {val_acc:.4f}')
            if val_acc > best_acc:
                best_acc = val_acc
                torch.save(model.state_dict(), output_dir / 'image_model.pth')
                print(' Saved best model')

    # Always save final model and classes mapping
    torch.save(model.state_dict(), output_dir / 'image_model_final.pth')
    with open(output_dir / 'classes.json', 'w') as f:
        json.dump(train_dataset.classes, f)
    print('Training complete. Models saved to', output_dir)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', default='flower_images', help='Path with train/val subfolders')
    p.add_argument('--output-dir', default='Flower Recognition Model', help='Where to save model')
    p.add_argument('--epochs', type=int, default=5)
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--lr', type=float, default=1e-4)
    args = p.parse_args()
    train(args.data_dir, args.output_dir, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
