import os
import re
import requests
from html.parser import HTMLParser

GDRIVE_URL = os.environ.get('GDRIVE_URL')

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_folder_contents(folder_id):
    """Scrape folder contents using embeddedfolderview (no API key needed)"""
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    items = []
    # Parse file entries
    file_pattern = r'<div class="flip-entry" id="entry-([^"]+)"[^>]*data-target="([^"]*)"[^>]*>.*?<div class="flip-entry-title">([^<]+)</div>'
    for match in re.finditer(file_pattern, response.text, re.DOTALL):
        item_id, target, name = match.groups()
        is_folder = 'drive.google.com/drive/folders' in target
        items.append({
            'id': item_id,
            'name': name.strip(),
            'is_folder': is_folder
        })

    # Alternative pattern
    if not items:
        alt_pattern = r'\["([a-zA-Z0-9_-]{20,})","([^"]+)",(\d+|null),"([^"]*)"'
        for match in re.finditer(alt_pattern, response.text):
            item_id, name, size, mime = match.groups()
            is_folder = mime == 'application/vnd.google-apps.folder' or size == 'null'
            items.append({
                'id': item_id,
                'name': name,
                'is_folder': is_folder
            })

    return items

def list_files_recursive(folder_id, folder_name, results):
    """Recursively list all files"""
    items = get_folder_contents(folder_id)

    for item in items:
        if item['is_folder']:
            list_files_recursive(item['id'], item['name'], results)
        else:
            download_link = f"https://drive.google.com/uc?export=download&id={item['id']}"
            results.append(f"{folder_name} {download_link}")

def main():
    folder_id = extract_folder_id(GDRIVE_URL)
    if not folder_id:
        print("Invalid Google Drive URL")
        return

    # Get root folder name
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    name_match = re.search(r'<title>([^<]+) - Google Drive</title>', response.text)
    root_name = name_match.group(1) if name_match else "root"

    results = []
    list_files_recursive(folder_id, root_name, results)

    with open('list.txt', 'w') as f:
        for line in results:
            f.write(line + '\n')

    print(f"Found {len(results)} files")
    for line in results:
        print(line)

if __name__ == '__main__':
    main()
