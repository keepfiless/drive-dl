import os
import re
import tempfile
import shutil
from gdown.download_folder import _get_folder_list

GDRIVE_URL = os.environ.get('GDRIVE_URL')

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def list_files_recursive(folder_id, folder_name, results):
    """Recursively list all files using gdown's internal function"""
    try:
        folder_list = _get_folder_list(folder_id)
    except Exception as e:
        print(f"Error getting folder {folder_id}: {e}")
        return

    for item in folder_list:
        if item[2] == 'folder':
            # Recursively process subfolder
            list_files_recursive(item[0], item[1], results)
        else:
            # File found
            download_link = f"https://drive.google.com/uc?export=download&id={item[0]}"
            results.append(f"{folder_name} {download_link}")

def main():
    folder_id = extract_folder_id(GDRIVE_URL)
    if not folder_id:
        print("Invalid Google Drive URL")
        return

    print(f"Processing folder: {folder_id}")

    # Get root folder files
    results = []
    try:
        root_list = _get_folder_list(folder_id)
        root_name = "root"

        for item in root_list:
            if item[2] == 'folder':
                list_files_recursive(item[0], item[1], results)
            else:
                download_link = f"https://drive.google.com/uc?export=download&id={item[0]}"
                results.append(f"{root_name} {download_link}")
    except Exception as e:
        print(f"Error: {e}")
        return

    with open('list.txt', 'w') as f:
        for line in results:
            f.write(line + '\n')

    print(f"Found {len(results)} files")
    for line in results:
        print(line)

if __name__ == '__main__':
    main()
