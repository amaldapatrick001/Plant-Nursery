import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import json

class DiseaseDetector:
    def __init__(self):
        # Load labels first to get correct number of classes
        self.labels_df = pd.read_csv('pdd/disease_labels.csv')
        
        # Load the pre-trained ResNet18 model
        self.model = models.resnet18(pretrained=False)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, len(self.labels_df))  # Use actual number of classes
        
        # Load the trained weights
        try:
            checkpoint = torch.load('pdd/best_model.pth', map_location=torch.device('cpu'))
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print("Model loaded successfully")
            print(f"Best validation accuracy: {checkpoint.get('val_acc', 'N/A')}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
            
        self.model.eval()
        
        # Load treatments
        with open('pdd/treatments.json', 'r') as f:
            self.treatments_dict = json.load(f)
        
        # Define image transformations (matching training exactly)
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_path):
        try:
            # Load and transform image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, 1)[0]
            
            # Get predictions with confidence threshold
            CONFIDENCE_THRESHOLD = 40.0
            HIGH_CONFIDENCE_THRESHOLD = 70.0
            
            # Get top prediction first
            top_confidence, top_idx = torch.max(probabilities, 0)
            top_confidence = top_confidence.item() * 100
            
            predictions = []
            
            # If top confidence is high enough, only show that prediction
            if top_confidence >= HIGH_CONFIDENCE_THRESHOLD:
                disease_info = self.labels_df[self.labels_df['label_id'] == top_idx.item()].iloc[0]
                predictions.append({
                    'disease': disease_info['disease_name'],
                    'confidence': f"{top_confidence:.2f}",
                    'description': disease_info['description'],
                    'chemical': [p.strip() for p in disease_info['recommended_products'].split(',')],
                    'cultural': [p.strip() for p in disease_info['prevention_measures'].split(',')],
                    'is_high_confidence': True
                })
            else:
                # Get top 3 predictions if no high confidence prediction
                top_3_conf, top_3_idx = torch.topk(probabilities, k=3)
                
                for conf, idx in zip(top_3_conf, top_3_idx):
                    confidence = conf.item() * 100
                    if confidence >= CONFIDENCE_THRESHOLD or len(predictions) == 0:
                        disease_info = self.labels_df[self.labels_df['label_id'] == idx.item()].iloc[0]
                        predictions.append({
                            'disease': disease_info['disease_name'],
                            'confidence': f"{confidence:.2f}",
                            'description': disease_info['description'],
                            'chemical': [p.strip() for p in disease_info['recommended_products'].split(',')],
                            'cultural': [p.strip() for p in disease_info['prevention_measures'].split(',')],
                            'is_high_confidence': confidence >= HIGH_CONFIDENCE_THRESHOLD
                        })
            
            # Debug information
            print(f"\nPrediction details:")
            for pred in predictions:
                print(f"Disease: {pred['disease']}, Confidence: {pred['confidence']}%")
            
            return predictions
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_treatments(self, disease_name):
        return self.treatments_dict.get(disease_name, {
            'chemical': ['Consult a plant pathologist for specific chemical treatments'],
            'biological': ['Consult a plant pathologist for specific biological controls'],
            'cultural': ['Maintain plant hygiene', 'Ensure proper spacing between plants']
        })

def detect_disease(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            
            # Validate file type
            if not image.content_type.startswith('image/'):
                return render(request, 'pdd/upload.html', {
                    'error': 'Please upload a valid image file (JPG, PNG).'
                })
            
            # Save the uploaded image
            fs = FileSystemStorage(location='media/uploads/')
            filename = fs.save(image.name, image)
            image_path = fs.path(filename)
            image_url = fs.url(f'uploads/{filename}')
            
            # Get prediction
            detector = DiseaseDetector()
            predictions = detector.predict(image_path)
            
            if predictions:
                context = {
                    'predictions': predictions,
                    'image_url': image_url,
                    'success': True
                }
            else:
                context = {
                    'error': 'Unable to process the image. Please try again.',
                    'success': False
                }
                
            return render(request, 'pdd/result.html', context)
            
        except Exception as e:
            print(f"Error in disease detection: {str(e)}")
            import traceback
            traceback.print_exc()
            return render(request, 'pdd/upload.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'pdd/upload.html')
