import os
import re
import requests

API_KEY = os.environ.get('API_KEY')
GDRIVE_URL = os.environ.get('GDRIVE_URL')

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def list_files(folder_id, parent_name=None):
    results = []
    url = f"https://www.googleapis.com/drive/v3/files"
    params = {
        'q': f"'{folder_id}' in parents",
        'key': API_KEY,
        'fields': 'files(id,name,mimeType)',
        'pageSize': 1000
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'files' not in data:
        print(f"Error: {data}")
        return results

    for item in data['files']:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # Recursively process subfolder
            results.extend(list_files(item['id'], item['name']))
        else:
            # File found - save with parent folder name
            folder_name = parent_name or "root"
            download_link = f"https://drive.google.com/uc?export=download&id={item['id']}"
            results.append(f"{folder_name} {download_link}")

    return results

def main():
    folder_id = extract_folder_id(GDRIVE_URL)
    if not folder_id:
        print("Invalid Google Drive URL")
        return

    # Get root folder name first
    url = f"https://www.googleapis.com/drive/v3/files/{folder_id}"
    params = {'key': API_KEY, 'fields': 'name'}
    response = requests.get(url, params=params)
    root_name = response.json().get('name', 'root')

    # List all files recursively
    files = list_files(folder_id, root_name)

    with open('list.txt', 'w') as f:
        for line in files:
            f.write(line + '\n')

    print(f"Found {len(files)} files")
    print("Contents of list.txt:")
    for line in files:
        print(line)

if __name__ == '__main__':
    main()
