import os
import shutil
from PIL import Image
import pandas as pd

def organize_dataset():
    # Read the labels file
    labels_df = pd.read_csv('pdd/disease_labels.csv')
    
    # Source directory (where your original images are)
    source_dir = 'pdd/PlantDiseases100x100/PlantDiseases100x100'  # Update this path
    
    # Destination directory
    dest_dir = 'pdd/organized_dataset'
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    print("Creating directories for each disease class...")
    # Create directories for each disease
    for _, row in labels_df.iterrows():
        disease_dir = os.path.join(dest_dir, row['disease_name'])
        os.makedirs(disease_dir, exist_ok=True)
        print(f"Created directory: {disease_dir}")
    
    print("\nOrganizing images...")
    # Process training images
    train_dir = os.path.join(source_dir, 'train')
    test_dir = os.path.join(source_dir, 'test')
    
    for directory in [train_dir, test_dir]:
        print(f"\nProcessing images in {os.path.basename(directory)}...")
        image_files = [f for f in os.listdir(directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        for img_file in image_files:
            img_path = os.path.join(directory, img_file)
            txt_file = os.path.splitext(img_file)[0] + '.txt'
            txt_path = os.path.join(directory, txt_file)
            
            if os.path.exists(txt_path):
                # Read the label file
                with open(txt_path, 'r') as f:
                    lines = f.readlines()
                
                if lines:
                    # Get the first label (assuming main disease)
                    first_line = lines[0].strip().split()
                    label_id = int(first_line[0])
                    
                    # Get disease name from label_id
                    disease_name = labels_df.loc[label_id, 'disease_name']
                    
                    # Copy image to appropriate disease folder
                    dst_path = os.path.join(dest_dir, disease_name, img_file)
                    shutil.copy2(img_path, dst_path)
                    print(f"Copied: {img_file} -> {disease_name}/")

if __name__ == "__main__":
    organize_dataset() 