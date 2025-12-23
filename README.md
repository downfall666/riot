Image Comparator & Indexer
A lightweight, local-first Python tool for indexing image feature vectors and performing high-confidence cross-referencing between local files or web URLs.


Prerequisites
Python 3.x

Dependencies: Install requirements via pip:

Bash

pip install pyperclip pillow
(Note: pyperclip is required for automatic clipboard functionality.)

Installation & Setup
Clone the repository to your desired directory.

Initialize Data: Create a folder named images in the root directory:

Bash
touch image_index.json (this file is too large to include here, but will not exceed 30 MB on your device)
mkdir images
Configuration: Place your reference .png images inside the /images folder.

Launch: Run the primary interface:

Bash

python main.py
Component Overview
main.py
The primary entry point for the application. It handles the user interface and coordinates data between the index and the comparison logic.

Capabilities: Cross-reference local files, analyze direct image URLs (supports drag-and-drop links), and manage the database.

image_indexer.py
The core engine of the application. It processes raw images from the /images directory, extracts feature vectors, and compiles them into the JSON database.

Note: This module is managed by main.py; it should not be executed directly.

/images Directory
Stores the source images for indexing. The system preserves filenames and capitalization—if a match is found, the filename (minus the extension) is what will be copied to your clipboard.

image_index.json
The "memory" of the application. This file stores the processed data for all indexed images. Do not delete this file, as main.py requires it for all referencing operations.

Important Usage Notes
Data Integrity: DO NOT run the "Mass Update" option if your /images folder is empty. Doing so will overwrite and reset your existing image_index.json file.

Single Additions: If you wish to add an image without a full download of the entire library, use Option 3 (Add Data) to update the index individually.

File Format: The current version specifically supports .png files for indexing.

 License & Terms
This project is open-source. You are granted explicit permission to use, modify, and distribute this software, provided the following conditions are met:

Liability: The author (downfall_6666) is not responsible for any misuse, abuse, or legal consequences resulting from the use of this software. The user assumes all responsibility for their actions.

Support Limitation: In the event of account bans, service restrictions, or legal issues arising from the use of this tool on third-party platforms, the author will not provide assistance or mediation.

Community Contributions: Customization and sharing are highly encouraged. If you develop an improved version or a unique fork, feel free to share it with the community!
