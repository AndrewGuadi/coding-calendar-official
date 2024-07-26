import zipfile
import os

# Define the path to the zip file and the extraction directory
zip_file_path = '/mnt/data/coding-calendar-official-main.zip'
extract_to_path = '/mnt/data/coding-calendar-official-main/'

# Create the extraction directory if it doesn't exist
os.makedirs(extract_to_path, exist_ok=True)

# Extract the contents of the zip file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

# List the extracted files and directories to understand the structure
extracted_files = []
for root, dirs, files in os.walk(extract_to_path):
    for name in files:
        extracted_files.append(os.path.join(root, name))
    for name in dirs:
        extracted_files.append(os.path.join(root, name))

extracted_files
