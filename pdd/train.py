import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
import pandas as pd
from PIL import Image
import os
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import json

# Enable CUDA optimizations
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled = True

class PlantDiseaseDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, label

class PlantDiseaseTrainer:
    def __init__(self, data_dir, batch_size=32, num_epochs=20, learning_rate=0.001):
        # Check for GPU and set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device.type == 'cuda':
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            torch.cuda.empty_cache()  # Clear GPU memory
        else:
            print("Using CPU - Training will be slower")
        
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate
        self.data_dir = data_dir
        
        # Load labels
        self.labels_df = pd.read_csv('pdd/disease_labels.csv')
        
        # Use smaller image size and simpler augmentations
        self.train_transform = transforms.Compose([
            transforms.Resize((160, 160)),  # Reduced from 224x224
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        self.val_transform = transforms.Compose([
            transforms.Resize((160, 160)),  # Reduced from 224x224
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        # Load treatment data
        self.treatments = {}
        for _, row in self.labels_df.iterrows():
            self.treatments[row['disease_name']] = {
                'description': row['description'],
                'chemical': [p.strip() for p in row['recommended_products'].split(',')],
                'cultural': [p.strip() for p in row['prevention_measures'].split(',')]
            }
        
        # Save treatments to JSON file for later use
        with open('pdd/treatments.json', 'w') as f:
            json.dump(self.treatments, f, indent=4)

        # Modify data loader settings
        self.num_workers = 0 if os.name == 'nt' else 4  # Set to 0 for Windows
        self.pin_memory = True if torch.cuda.is_available() else False

    def prepare_data(self):
        # Get all image paths and labels
        image_paths = []
        labels = []
        
        print("\nScanning dataset directory:", self.data_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created directory: {self.data_dir}")
        
        # Print available classes
        print("\nAvailable disease classes in labels file:")
        for label_id, row in self.labels_df.iterrows():
            print(f"[{label_id}] {row['disease_name']}")
        
        # Dictionary to store image counts per class
        class_counts = {}
        
        # First pass: count images per class
        for label_id in range(len(self.labels_df)):
            disease_name = self.labels_df.loc[label_id, 'disease_name']
            disease_dir = os.path.join(self.data_dir, disease_name)
            
            if os.path.exists(disease_dir):
                image_files = [f for f in os.listdir(disease_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                class_counts[label_id] = len(image_files)
                if image_files:
                    print(f"\nFound {len(image_files)} images for {disease_name}")
                else:
                    print(f"\nNo images found in {disease_dir}")
            else:
                print(f"\nDirectory not found: {disease_dir}")
                class_counts[label_id] = 0
        
        # Filter out classes with less than 10 images
        MIN_SAMPLES = 10
        valid_classes = {label_id: count for label_id, count in class_counts.items() if count >= MIN_SAMPLES}
        
        if not valid_classes:
            raise ValueError(f"No classes found with at least {MIN_SAMPLES} images!")
        
        print(f"\nUsing {len(valid_classes)} classes with at least {MIN_SAMPLES} images each:")
        
        # Second pass: collect images only from valid classes
        for label_id in valid_classes.keys():
            disease_name = self.labels_df.loc[label_id, 'disease_name']
            disease_dir = os.path.join(self.data_dir, disease_name)
            
            image_files = [f for f in os.listdir(disease_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
            for img_file in image_files:
                image_paths.append(os.path.join(disease_dir, img_file))
                labels.append(label_id)
            print(f"{disease_name}: {len(image_files)} images")
        
        if not image_paths:
            raise ValueError(
                f"\nNo valid images found in {self.data_dir}!\n"
                "Please ensure your dataset is organized correctly."
            )
        
        print(f"\nTotal valid images found: {len(image_paths)}")
        
        # Split data into train and validation sets
        train_paths, val_paths, train_labels, val_labels = train_test_split(
            image_paths, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print(f"Training samples: {len(train_paths)}")
        print(f"Validation samples: {len(val_paths)}")
        
        # Create datasets
        self.train_dataset = PlantDiseaseDataset(train_paths, train_labels, self.train_transform)
        self.val_dataset = PlantDiseaseDataset(val_paths, val_labels, self.val_transform)
        
        # Create data loaders with optimized settings
        self.train_loader = DataLoader(
            self.train_dataset, 
            batch_size=self.batch_size, 
            shuffle=True, 
            num_workers=self.num_workers,
            pin_memory=self.pin_memory
        )
        self.val_loader = DataLoader(
            self.val_dataset, 
            batch_size=self.batch_size, 
            shuffle=False, 
            num_workers=self.num_workers,
            pin_memory=self.pin_memory
        )

    def setup_model(self):
        # Use ResNet18 instead of ResNet50 (smaller model)
        self.model = models.resnet18(weights='IMAGENET1K_V1')
        
        # Freeze early layers to reduce memory usage and training time
        for param in self.model.parameters():
            param.requires_grad = False
            
        # Only train the final layers
        for param in self.model.layer4.parameters():
            param.requires_grad = True
        
        # Modify final layer for our number of classes
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, len(self.labels_df))
        
        # Move model to GPU/CPU
        self.model = self.model.to(self.device)
        
        # Use mixed precision training if GPU available
        if self.device.type == 'cuda':
            self.scaler = torch.cuda.amp.GradScaler()
        
        # Optimized training setup
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.learning_rate,
            weight_decay=0.01
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=2, factor=0.1, min_lr=1e-6
        )

    def train_epoch(self):
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        progress_bar = tqdm(self.train_loader, desc='Training')
        for inputs, labels in progress_bar:
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            # Use mixed precision training if GPU available
            if self.device.type == 'cuda':
                with torch.cuda.amp.autocast():
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, labels)
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
            
            self.optimizer.zero_grad()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f'{running_loss/total:.3f}',
                'acc': f'{100.*correct/total:.2f}%'
            })
            
            # Clean up GPU memory
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
        
        return running_loss/len(self.train_loader), correct/total

    def validate(self):
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in tqdm(self.val_loader, desc='Validating'):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
        return running_loss/len(self.val_loader), correct/total

    def train(self):
        print(f"Training on {self.device}")
        self.prepare_data()
        self.setup_model()
        
        best_val_acc = 0
        train_losses = []
        val_losses = []
        train_accs = []
        val_accs = []
        
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch+1}/{self.num_epochs}")
            
            # Train
            train_loss, train_acc = self.train_epoch()
            train_losses.append(train_loss)
            train_accs.append(train_acc)
            
            # Validate
            val_loss, val_acc = self.validate()
            val_losses.append(val_loss)
            val_accs.append(val_acc)
            
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                }, 'pdd/best_model.pth')
        
        # Plot training history
        self.plot_training_history(train_losses, val_losses, train_accs, val_accs)

    def plot_training_history(self, train_losses, val_losses, train_accs, val_accs):
        plt.figure(figsize=(12, 4))
        
        # Plot losses
        plt.subplot(1, 2, 1)
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Val Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Plot accuracies
        plt.subplot(1, 2, 2)
        plt.plot(train_accs, label='Train Acc')
        plt.plot(val_accs, label='Val Acc')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('pdd/training_history.png')
        plt.close()

if __name__ == "__main__":
    try:
        # Set random seeds
        torch.manual_seed(42)
        np.random.seed(42)
        
        # Initialize trainer with optimized parameters
        trainer = PlantDiseaseTrainer(
            data_dir='pdd/organized_dataset',
            batch_size=64,  # Increased batch size
            num_epochs=20,
            learning_rate=0.001
        )
        
        # Start training
        trainer.train()
        
    except Exception as e:
        print(f"\nTraining failed: {str(e)}")
        import traceback
        traceback.print_exc()