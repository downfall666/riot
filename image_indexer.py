import os
import json
from PIL import Image


INDEX_FILE = 'image_index.json'
IMAGE_DIR = 'images'
CANONICAL_SIZE = (64, 64) 

RGB_TOLERANCE = 15 



def get_feature_vector(file_path):
   
    try:
        img = Image.open(file_path).convert("RGB")
       
        img_resized = img.resize(CANONICAL_SIZE, Image.Resampling.LANCZOS)
        
      
        feature_vector = list(sum(img_resized.getdata(), ())) 
        return feature_vector
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return None

def compare_vectors(vector_a, vector_b, tolerance):
    """
    Compares two feature vectors (lists of RGB integers) using Max Channel Difference.
    Returns the match percentage.
    """
    if len(vector_a) != len(vector_b):
        return 0.0 

    total_channels = len(vector_a)
    mismatched_channels = 0
    
 
    for i in range(0, total_channels, 3):
        diff_r = abs(vector_a[i] - vector_b[i])
        diff_g = abs(vector_a[i+1] - vector_b[i+1])
        diff_b = abs(vector_a[i+2] - vector_b[i+2])
        
       
        max_diff = max(diff_r, diff_g, diff_b)
        
        if max_diff > tolerance:
            mismatched_channels += 1

    total_pixels = total_channels / 3
    
    match_percentage = 100 - (mismatched_channels / total_pixels) * 100
    return match_percentage

def load_index():
    """Loads the index file if it exists, otherwise returns an empty dictionary."""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Index file corrupted. Starting fresh.")
                return {}
    return {}

def save_index(index_data):
    """Saves the current index dictionary to the file."""
    with open(INDEX_FILE, 'w') as f:
        json.dump(index_data, f, indent=4)
    print(f"\nSuccessfully saved {len(index_data)} entries to {INDEX_FILE}.")

def index_all_images(index_data):
    """Scans the image directory and updates/adds all files to the index."""
    if not os.path.isdir(IMAGE_DIR):
        print(f"Error: Image directory '{IMAGE_DIR}' not found. Please create it and add your PNG files.")
        return 0
        
    print(f"\nStarting indexing of files in '{IMAGE_DIR}'...")
    new_count = 0
    
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(IMAGE_DIR, filename)
            display_name = os.path.splitext(filename)[0] 
            
            if display_name in index_data:
                pass 
                
            vector = get_feature_vector(file_path)
            if vector:
                index_data[display_name] = vector
                new_count += 1
                
    return new_count

if __name__ == '__main__':
    print("Testing Feature Extraction Utility...")
    print("This file contains utility functions. Run 'app.py' to manage the index.")
