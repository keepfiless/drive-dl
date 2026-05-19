import os
import re
import requests

GDRIVE_URL = os.environ.get('GDRIVE_URL')

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_folder_contents(folder_id):
    """Parse folder using embeddedfolderview endpoint"""
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    html = response.text

    items = []

    # Pattern for parsing the JavaScript data in embeddedfolderview
    # Format: ["id","name","","mimeType",...] or similar structures
    pattern = r'\["([\w-]{20,})","([^"]+)","[^"]*","(application/vnd\.google-apps\.folder|[^"]+)"'

    for match in re.finditer(pattern, html):
        file_id, name, mime = match.groups()
        is_folder = 'folder' in mime
        items.append({
            'id': file_id,
            'name': name,
            'is_folder': is_folder
        })

    # Alternative: parse flip-entry divs
    if not items:
        entry_pattern = r'data-id="([^"]+)"[^>]*>.*?<div class="flip-entry-title">([^<]+)</div>'
        for match in re.finditer(entry_pattern, html, re.DOTALL):
            file_id, name = match.groups()
            # Check if it's a folder by looking for folder icon
            is_folder = f'data-id="{file_id}"' in html and 'vnd.google-apps.folder' in html
            items.append({
                'id': file_id,
                'name': name.strip(),
                'is_folder': is_folder
            })

    return items

def list_files_recursive(folder_id, folder_name, results, visited=None):
    """Recursively list all files"""
    if visited is None:
        visited = set()

    if folder_id in visited:
        return
    visited.add(folder_id)

    print(f"Scanning folder: {folder_name} ({folder_id})")
    items = get_folder_contents(folder_id)
    print(f"  Found {len(items)} items")

    for item in items:
        if item['is_folder']:
            list_files_recursive(item['id'], item['name'], results, visited)
        else:
            download_link = f"https://drive.google.com/uc?export=download&id={item['id']}"
            results.append(f"{folder_name} {download_link}")
            print(f"  File: {item['name']}")

def main():
    folder_id = extract_folder_id(GDRIVE_URL)
    if not folder_id:
        print("Invalid Google Drive URL")
        return

    print(f"Starting with folder ID: {folder_id}")

    results = []
    list_files_recursive(folder_id, "root", results)

    with open('list.txt', 'w') as f:
        for line in results:
            f.write(line + '\n')

    print(f"\n=== RESULTS ===")
    print(f"Total files found: {len(results)}")
    for line in results:
        print(line)

if __name__ == '__main__':
    main()
