import os
import shutil
import random
import pandas as pd
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

# -----------------------------
# CONFIG
# -----------------------------
RAW_DATASET_DIRS = [
    "/Users/sriram/Downloads/archive/HAM10000_images_part_1",
    "/Users/sriram/Downloads/archive/HAM10000_images_part_2"
]
METADATA_FILE = "/Users/sriram/Downloads/archive/HAM10000_metadata.csv"
SUBSET_DIR = "/Users/sriram/Medi/skin_classifier/subset_images"
SUBSET_META_FILE = "/Users/sriram/Medi/skin_classifier/subset_metadata.csv"
BALANCED_DIR = "/Users/sriram/Medi/skin_classifier/balanced_skin_data"
BEST_MODEL_PATH = "/Users/sriram/Medi/skin_classifier/best_skin_model.pth"

CATEGORIES = [
    "Actinic Keratoses",
    "Basal Cell Carcinoma",
    "Benign Keratosis",
    "Dermatofibroma",
    "Melanocytic Nevi",
    "Vascular Lesions",
    "Melanoma"
]

DX_MAPPING = {
    "akiec": "Actinic Keratoses",
    "bcc": "Basal Cell Carcinoma",
    "bkl": "Benign Keratosis",
    "df": "Dermatofibroma",
    "nv": "Melanocytic Nevi",
    "vasc": "Vascular Lesions",
    "mel": "Melanoma"
}

IMAGES_PER_CLASS = 1000
NUM_CLASSES = 7
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.7, 0.2, 0.1
BATCH_SIZE = 16
EPOCHS = 10
LR = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# STEP 1: CREATE SUBSET
# -----------------------------
def create_subset(raw_dirs, metadata_file, subset_dir, subset_meta_file, categories, images_per_class):
    os.makedirs(subset_dir, exist_ok=True)
    subset_records = []
    df = pd.read_csv(metadata_file)
    df['label'] = df['dx'].map(DX_MAPPING)
    
    image_paths = {}
    for raw_dir in raw_dirs:
        for filename in os.listdir(raw_dir):
            if filename.endswith(".jpg"):
                image_id = filename.split('.')[0]
                image_paths[image_id] = os.path.join(raw_dir, filename)

    for category in categories:
        cls_df = df[df['label'] == category]
        if len(cls_df) < images_per_class:
            print(f"⚠️ Warning: {category} has only {len(cls_df)} images. Taking all.")
            selected_df = cls_df
        else:
            selected_df = cls_df.sample(n=images_per_class, random_state=42)
            
        for _, row in selected_df.iterrows():
            img_id = row['image_id']
            src = image_paths.get(img_id)
            dst = os.path.join(subset_dir, f"{img_id}.jpg")
            
            if src and os.path.exists(src):
                shutil.copy(src, dst)
                subset_records.append({
                    "image_id": img_id,
                    "symptoms": "",
                    "label": category
                })
            else:
                print(f"⚠️ Image not found: {img_id}")
    
    subset_df = pd.DataFrame(subset_records)
    subset_df.to_csv(subset_meta_file, index=False)
    print(f"✅ Subset created: {len(subset_df)} images saved to {subset_dir}")
    return subset_dir

# -----------------------------
# STEP 2: CREATE BALANCED DATASET
# -----------------------------
def create_balanced_dataset(subset_dir, balanced_dir, categories, images_per_class):
    if os.path.exists(balanced_dir):
        print(f"[INFO] Using existing balanced dataset at {balanced_dir}")
        return balanced_dir
    
    os.makedirs(balanced_dir, exist_ok=True)
    metadata = pd.read_csv(SUBSET_META_FILE)
    
    for category in categories:
        cat_imgs = metadata[metadata['label'] == category]['image_id'].tolist()
        if len(cat_imgs) < images_per_class:
            selected_imgs = cat_imgs
        else:
            selected_imgs = random.sample(cat_imgs, images_per_class)
        
        dest_cls_dir = os.path.join(balanced_dir, category)
        os.makedirs(dest_cls_dir, exist_ok=True)
        for img_name in selected_imgs:
            src = os.path.join(subset_dir, f"{img_name}.jpg")
            dst = os.path.join(dest_cls_dir, f"{img_name}.jpg")
            if os.path.exists(src):
                shutil.copy(src, dst)
    
    print(f"✅ Balanced dataset created at {balanced_dir}")
    return balanced_dir

# -----------------------------
# STEP 3: DATALOADERS
# -----------------------------
def get_dataloaders(data_dir, batch_size):
    # Training transforms with aggressive augmentation
    train_tfms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.RandomAffine(
            degrees=15,
            scale=(0.9, 1.1),
            translate=(0.1, 0.1)
        ),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.1
        ),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
        transforms.RandomErasing(p=0.3, scale=(0.02, 0.1), ratio=(0.3, 3.3))
    ])
    
    # Standard transforms for validation and testing (no augmentation)
    test_val_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    ])
    
    train_dataset = datasets.ImageFolder(data_dir, transform=train_tfms)
    test_val_dataset = datasets.ImageFolder(data_dir, transform=test_val_tfms)
    
    targets = np.array(train_dataset.targets)
    indices = np.arange(len(train_dataset))
    
    class_indices = defaultdict(list)
    for i, target in enumerate(targets):
        class_indices[target].append(indices[i])
        
    train_indices, val_indices, test_indices = [], [], []
    
    for cls in class_indices:
        random.shuffle(class_indices[cls])
        total_cls = len(class_indices[cls])
        train_count = int(total_cls * TRAIN_RATIO)
        val_count = int(total_cls * VAL_RATIO)
        
        train_indices.extend(class_indices[cls][:train_count])
        val_indices.extend(class_indices[cls][train_count:train_count + val_count])
        test_indices.extend(class_indices[cls][train_count + val_count:])
    
    train_subset = Subset(train_dataset, train_indices)
    val_subset = Subset(test_val_dataset, val_indices)
    test_subset = Subset(test_val_dataset, test_indices)

    train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_subset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, test_loader, train_dataset.classes

# -----------------------------
# STEP 4: MODEL
# -----------------------------
def get_model(num_classes):
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model.to(DEVICE)

# -----------------------------
# STEP 5: TRAIN
# -----------------------------
def train_model(model, train_loader, val_loader, epochs, lr, best_model_path):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
        
        train_acc = correct / total
        avg_loss = running_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs = model(imgs)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
        val_acc = val_correct / val_total
        
        print(f"Epoch [{epoch+1}/{epochs}] | Loss: {avg_loss:.4f} | Train Acc: {train_acc:.3f} | Val Acc: {val_acc:.3f}")
        
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), best_model_path)
            print("[INFO] Saved new best model!")
    
    print(f"[INFO] Training complete. Best Val Acc: {best_acc:.3f}")

# -----------------------------
# STEP 6: TEST & METRICS
# -----------------------------
def test_model(model, test_loader, class_names, best_model_path):
    try:
        model.load_state_dict(torch.load(best_model_path, map_location=DEVICE))
    except FileNotFoundError:
        print("[ERROR] Model weights not found! Train first.")
        return
        
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    rec = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    print("\n[INFO] Classification Report:\n")
    print(classification_report(all_labels, all_preds, target_names=class_names))
    print(f"Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1-score: {f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.show()

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    subset_dir = create_subset(RAW_DATASET_DIRS, METADATA_FILE, SUBSET_DIR, SUBSET_META_FILE, CATEGORIES, IMAGES_PER_CLASS)
    balanced_dir = create_balanced_dataset(subset_dir, BALANCED_DIR, CATEGORIES, IMAGES_PER_CLASS)
    
    train_loader, val_loader, test_loader, classes = get_dataloaders(balanced_dir, BATCH_SIZE)
    
    model = get_model(NUM_CLASSES)
    train_model(model, train_loader, val_loader, EPOCHS, LR, BEST_MODEL_PATH)
    test_model(model, test_loader, classes, BEST_MODEL_PATH)