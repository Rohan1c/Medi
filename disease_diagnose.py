import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import os
import pandas as pd
import gradio as gr

# Define the classes
classes = [
    "Actinic Keratoses",
    "Basal Cell Carcinoma",
    "Benign Keratosis",
    "Dermatofibroma",
    "Melanocytic Nevi",
    "Vascular Lesions",
    "Melanoma"
]

# Set up the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 1. Dataset and Data Loading (Conceptual) ---
class SkinDiseaseDataset(Dataset):
    def __init__(self, df, img_dir, tokenizer, img_transforms):
        self.df = df
        self.img_dir = img_dir
        self.tokenizer = tokenizer
        self.img_transforms = img_transforms
        self.classes = sorted(df['label'].unique())
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = os.path.join(self.img_dir, row['image_id'] + '.jpg')
        image = Image.open(img_path).convert("RGB")
        text = row['symptoms']
        label = self.class_to_idx[row['label']]

        image_tensor = self.img_transforms(image)
        text_tokens = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        
        # Remove batch dimension from tokenizer output
        text_tokens = {k: v.squeeze(0) for k, v in text_tokens.items()}
        
        return image_tensor, text_tokens, torch.tensor(label)

# --- 2. Set up Models and a custom collate function ---
# Image preprocessing
img_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Custom collate function to handle variable-length text tensors
def custom_collate_fn(batch):
    # Separate the data
    images = [item[0] for item in batch]
    texts = [item[1] for item in batch]
    labels = [item[2] for item in batch]

    # Stack images and labels as tensors
    images = torch.stack(images)
    labels = torch.stack(labels)

    # Use the tokenizer's padding method for text inputs
    # This pads all text inputs in the batch to the same length.
    padded_texts = tokenizer.pad(
        texts,
        padding=True,
        return_tensors="pt"
    )
    
    return images, padded_texts, labels

# Image model
resnet = models.resnet50(pretrained=True)
resnet.fc = nn.Identity()

# Text model
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
bert_model = AutoModel.from_pretrained("bert-base-uncased")

# Multimodal classifier
class MultimodalClassifier(nn.Module):
    def __init__(self, text_dim=768, image_dim=2048, num_classes=7):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(text_dim + image_dim, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes)
        )
    def forward(self, text_emb, image_emb):
        x = torch.cat([text_emb, image_emb], dim=1)
        return self.fc(x)

classifier = MultimodalClassifier(image_dim=2048)
classifier = classifier.to(device)
resnet = resnet.to(device)
bert_model = bert_model.to(device)

# --- 3. Training Loop ---
def train_model(epochs=10):
    print("Starting model training with dummy data...")
    df = pd.DataFrame({
        'image_id': [f'img_{i}' for i in range(100)],
        'symptoms': ['red, itchy rash', 'dark spot that is growing', 'benign lesion, no symptoms', 'symptom 4'] * 25,
        'label': ['Actinic Keratoses', 'Melanoma', 'Benign Keratosis', 'Vascular Lesions'] * 25
    })
    dummy_img_dir = 'dummy_images'
    os.makedirs(dummy_img_dir, exist_ok=True)
    for img_id in df['image_id']:
        Image.new('RGB', (224, 224), 'white').save(os.path.join(dummy_img_dir, f'{img_id}.jpg'))
    
    dataset = SkinDiseaseDataset(df, dummy_img_dir, tokenizer, img_transforms)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=custom_collate_fn)

    optimizer = torch.optim.Adam(list(resnet.parameters()) + list(classifier.parameters()) + list(bert_model.parameters()), lr=1e-4)
    criterion = nn.CrossEntropyLoss()

    resnet.train()
    bert_model.train()
    classifier.train()

    for epoch in range(epochs):
        for images, texts, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)
            texts = {k: v.to(device) for k, v in texts.items()}
            
            optimizer.zero_grad()
            
            image_features = resnet(images)
            text_outputs = bert_model(**texts)
            text_features = text_outputs.last_hidden_state.mean(dim=1)
            
            combined_logits = classifier(text_features, image_features)
            
            loss = criterion(combined_logits, labels)
            loss.backward()
            optimizer.step()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

    torch.save(resnet.state_dict(), 'trained_resnet_model.pth')
    torch.save(classifier.state_dict(), 'trained_classifier.pth')
    print("Training complete. Models saved.")

# --- 4. Inference Function for Gradio ---
def diagnose(image, text_symptoms):
    if not os.path.exists('trained_resnet_model.pth') or not os.path.exists('trained_classifier.pth'):
        return "Model not trained. Please run the training code first."

    resnet.load_state_dict(torch.load('trained_resnet_model.pth'))
    classifier.load_state_dict(torch.load('trained_classifier.pth'))
    
    resnet.eval()
    bert_model.eval()
    classifier.eval()

    image_emb = torch.zeros(1, 2048).to(device)
    if image is not None:
        img_t = img_transforms(image.convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            image_emb = resnet(img_t)

    text_emb = torch.zeros(1, 768).to(device)
    if text_symptoms:
        inputs = tokenizer(text_symptoms, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = bert_model(**inputs)
            text_emb = outputs.last_hidden_state.mean(dim=1)

    with torch.no_grad():
        combined_logits = classifier(text_emb, image_emb)

    probs = torch.softmax(combined_logits, dim=1)[0]
    top_idx = torch.argmax(probs).item()
    confidence = probs[top_idx].item()
    
    return f"Predicted condition: {classes[top_idx]}, Confidence: {confidence:.2f}"

# --- 5. Gradio Interface ---
iface = gr.Interface(
    fn=diagnose,
    inputs=[
        gr.Image(type="pil", label="Upload Skin Image"),
        gr.Textbox(lines=3, placeholder="Describe your symptoms...", label="Describe symptoms")
    ],
    outputs="text",
    title="Skin Disease Diagnostic Chatbot",
    description="Upload an image of your skin condition and describe any symptoms. This bot gives probable skin disease predictions. ⚠️ Not a medical diagnosis."
)

if __name__ == "__main__":
    train_model(epochs=5)
    iface.launch()
