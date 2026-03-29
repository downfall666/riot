import os
import tempfile
import urllib.request
import urllib.error
from image_indexer import get_feature_vector, compare_vectors, load_index, save_index, index_all_images, RGB_TOLERANCE

try:
    import pyperclip
    CLIPBOARD_ENABLED = True
except ImportError:
    CLIPBOARD_ENABLED = False
    print("WARNING: 'pyperclip' not found. Automatic clipboard functions are disabled. Install with: pip install pyperclip")

STRONG_MATCH_THRESHOLD = 60.0 

def copy_to_clipboard(text):
    if CLIPBOARD_ENABLED:
        try:
            pyperclip.copy(text)
            print(f" (Copied '{text}' to clipboard.)")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

def run_comparison_logic(input_path, index_data):
    
    new_vector = get_feature_vector(input_path)
    if not new_vector:
        print("Comparison failed: Could not process the input image.")
        return

    print(f"\n--- Comparing Input Image against {len(index_data)} Indexed Entries (Tolerance: {RGB_TOLERANCE}) ---")
    
    match_results = []

    for name, indexed_vector in index_data.items():
        confidence = compare_vectors(new_vector, indexed_vector, RGB_TOLERANCE)
        
        match_results.append({"name": name, "confidence": confidence})
        
        if confidence > 99.0:
            print(f"  --> NEAR PERFECT MATCH FOUND: '{name}' with {confidence:.2f}% confidence!")

    match_results.sort(key=lambda x: x['confidence'], reverse=True)
    
    best_match = match_results[0] if match_results else {"name": "None", "confidence": 0.0}

    print("\n--- TOP MATCHES ---")
    
    for i, result in enumerate(match_results[:5]):
        print(f"  #{i+1}: '{result['name']}' ({result['confidence']:.2f}%)")

    print("\n--- FINAL CONCLUSION ---")
    if best_match["confidence"] >= STRONG_MATCH_THRESHOLD:
        print(f"The best match is '{best_match['name']}' with a STRONG CONFIDENCE of {best_match['confidence']:.2f}%.")
        print("This confirms the images are the same content despite size changes and compression noise.")
        copy_to_clipboard(best_match['name']) # <--- New Feature: Copy the result
    else:
        print(f"No strong match found. Best result: '{best_match['name']}' ({best_match['confidence']:.2f}%).")


def compare_local_file(index_data):
    if not index_data:
        print("\nIndex is empty. Please run 'Mass Update' first.")
        return

    input_path = input("\nEnter the path to the local image file to compare: ")
    
    if not os.path.exists(input_path):
        print("Error: File not found at that path.")
        return
        
    run_comparison_logic(input_path, index_data)


def analyze_image_url(index_data, pre_pasted_url=None):
    if not index_data:
        print("\nIndex is empty. Please run 'Mass Update' first.")
        return

    image_url = pre_pasted_url

    if not image_url:
        if CLIPBOARD_ENABLED:
            image_url = pyperclip.paste()
            if not image_url:
                print("Clipboard is empty.")
            else:
                print(f"\nClipboard URL detected: {image_url}")
                
        if not image_url:
            image_url = input("\nEnter the DIRECT image URL to analyze (must end in .png, .jpg, etc.): ")
    else:
        print(f"\nAnalyzing URL: {image_url}")
    
    temp_file_path = os.path.join(tempfile.gettempdir(), 'temp_image_for_analysis.png')

    print(f"Attempting to download image from URL...")
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(image_url, temp_file_path)
        print("Download complete. Analyzing...")
        
        run_comparison_logic(temp_file_path, index_data)

    except urllib.error.URLError as e:
        print(f"Error downloading image: Invalid URL or network issue. ({e})")
    except Exception as e:
        print(f"An unexpected error occurred during download/analysis: {e}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def manage_index():
    index_data = load_index()
    
    while True:
        print("\n--- Image Index Manager ---")
        print(f"Current Index Size: {len(index_data)} entries")
        print("1. Cross-Reference Local File")
        print("2. Mass Update (Re-index all files in 'images/')")
        print("3. Add Data (Index a specific single file)")
        print("4. Remove Data (Remove a specific entry)")
        
        clipboard_status = " (Auto-Read Clipboard)" if CLIPBOARD_ENABLED else ""
        print(f"5. Analyze Image URL{clipboard_status}")
        
        print("6. Exit")
        
        try:
            choice = input("Choose an option (1-6) OR Paste a URL directly: ")
        except KeyboardInterrupt:
            print("\nExiting Image Comparator. Goodbye!")
            return

        if choice.strip().lower().startswith("http"):
             analyze_image_url(index_data, pre_pasted_url=choice.strip())
             continue

        if choice == '1':
            compare_local_file(index_data)
        
        elif choice == '2':
            count = index_all_images(index_data)
            print(f"Indexed/Updated {count} files.")
            save_index(index_data)
        
        elif choice == '3':
            file_path = input("Enter the path to the single image file to add: ")
            display_name = input("Enter a display name for this entry (e.g., 'My_New_Image'): ")
            
            vector = get_feature_vector(file_path)
            if vector:
                index_data[display_name] = vector
                print(f"Successfully added '{display_name}'.")
                save_index(index_data)
        
        elif choice == '4':
            if not index_data:
                print("Index is empty.")
                continue
                
            name_to_remove = input("Enter the display name of the entry to remove: ")
            if name_to_remove in index_data:
                del index_data[name_to_remove]
                print(f"Successfully removed '{name_to_remove}'.")
                save_index(index_data)
            else:
                print(f"Error: Entry '{name_to_remove}' not found in the index.")
        
        elif choice == '5':
            analyze_image_url(index_data)

        elif choice == '6':
            print("Exiting Image Comparator. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6 or paste a URL.")

if __name__ == '__main__':
    if not os.path.isdir("images"):
        os.makedirs("images", exist_ok=True)
        print("Note: Created 'images/' directory. Please place your PNG files. Other filetypes will be rejected by the indexer.")
        
    manage_index()
