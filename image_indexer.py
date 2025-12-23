import os
import json
from PIL import Image

# --- Configuration ---
INDEX_FILE = 'image_index.json'
IMAGE_DIR = 'images'
CANONICAL_SIZE = (64, 64)  # All images are resized to 64x64 for fast, consistent comparison
# Tolerance for comparison (Max Diff for RGB channels)
# We will use 15, as confirmed in your previous analysis, but applied to the downscaled image.
RGB_TOLERANCE = 15 
# --- End Configuration ---


def get_feature_vector(file_path):
    """
    Normalizes an image to a canonical size and extracts a flat tuple of all RGB values.
    This tuple serves as the unique content 'fingerprint' or feature vector.
    """
    try:
        img = Image.open(file_path).convert("RGB")
        # Step 1: Canonical Resize (Neutralizes the size trick)
        img_resized = img.resize(CANONICAL_SIZE, Image.Resampling.LANCZOS)
        
        # Step 2: Extract Feature Vector (Flattened list of R, G, B values)
        # Example: (R1, G1, B1, R2, G2, B2, ...)
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
        return 0.0 # Vectors must be the same length (same canonical size)

    total_channels = len(vector_a) # Total number of R, G, B values
    mismatched_channels = 0
    
    # We step through the list 3 elements at a time (R, G, B)
    for i in range(0, total_channels, 3):
        diff_r = abs(vector_a[i] - vector_b[i])
        diff_g = abs(vector_a[i+1] - vector_b[i+1])
        diff_b = abs(vector_a[i+2] - vector_b[i+2])
        
        # Max Diff (L-infinity norm)
        max_diff = max(diff_r, diff_g, diff_b)
        
        if max_diff > tolerance:
            mismatched_channels += 1

    # Mismatched_channels is the count of PIXELS that mismatched (since we incremented by 3)
    total_pixels = total_channels / 3
    
    match_percentage = 100 - (mismatched_channels / total_pixels) * 100
    return match_percentage

def load_index():
    """Loads the index file if it exists, otherwise returns an empty dictionary."""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            try:
                # The stored vectors are lists of integers, which is JSON-safe.
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
            # Use filename without extension as the display name (key)
            display_name = os.path.splitext(filename)[0] 
            
            # Skip if already indexed and file hasn't changed (simplified)
            if display_name in index_data:
                # For simplicity, we re-index to handle file updates. 
                # A more complex system would check file modification time.
                pass 
                
            vector = get_feature_vector(file_path)
            if vector:
                index_data[display_name] = vector
                new_count += 1
                
    return new_count

if __name__ == '__main__':
    # Simple test for feature extraction
    print("Testing Feature Extraction Utility...")
    # This assumes you have 'maybe.png' in the current directory for testing
    # test_vector = get_feature_vector('maybe.png') 
    # if test_vector:
    #     print(f"Test vector length: {len(test_vector)} (should be 12288 for 64x64)")
    #     print(f"First 10 values: {test_vector[:10]}")
    print("This file contains utility functions. Run 'app.py' to manage the index.")
