import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
BUCKET_NAME: str = "content"

# Download Configuration
MAX_LISTING_WORKERS: int = 10
MAX_DOWNLOAD_WORKERS: int = 20

def list_items_in_path(path: str) -> List[dict]:
    """Fetch items (files and folders) from a specific path in Supabase Storage."""
    url: str = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"
    headers: dict = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload: dict = {
        "prefix": path,
        "limit": 100,
        "offset": 0,
        "sortBy": {"column": "name", "order": "asc"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            items = response.json()
            if path:
                print(f"  > Scanned '{path}' - found {len(items)} items")
            return items
    except Exception as e:
        print(f"Error listing items in '{path}': {e}")
    return []

def list_files_recursively_parallel(base_path: str) -> List[str]:
    """Explores folders in parallel to find all files."""
    all_files: List[str] = []
    folders_to_scan: List[str] = [base_path]
    
    with ThreadPoolExecutor(max_workers=MAX_LISTING_WORKERS) as executor:
        while folders_to_scan:
            # Submit scan tasks for all current folders
            future_to_folder = {executor.submit(list_items_in_path, folder): folder for folder in folders_to_scan}
            folders_to_scan = [] # Reset for next level
            
            for future in as_completed(future_to_folder):
                items = future.result()
                current_folder = future_to_folder[future]
                
                for item in items:
                    name: str = item['name']
                    full_path: str = f"{current_folder}/{name}" if current_folder else name
                    
                    if item.get('id') is None:  # It's a folder
                        folders_to_scan.append(full_path)
                    else:  # It's a file
                        all_files.append(full_path)
    
    return all_files

def download_file(file_path: str) -> None:
    """Downloads a file from Supabase Storage only if it doesn't exist locally."""
    local_path: str = file_path
    
    if os.path.exists(local_path):
        return

    from urllib.parse import quote
    quoted_path: str = quote(file_path)
    url: str = f"{SUPABASE_URL}/storage/v1/object/authenticated/{BUCKET_NAME}/{quoted_path}"
    headers: dict = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {local_path}")
        else:
            if response.status_code != 404:
                print(f"Error downloading '{file_path}': {response.status_code}")
    except Exception as e:
        print(f"Exception downloading '{file_path}': {e}")

if __name__ == "__main__":
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("Error: Environment variables not correctly loaded. Check your .env file.")
        exit(1)

    print(f"Exploring bucket '{BUCKET_NAME}' in parallel with {MAX_LISTING_WORKERS} workers...")
    
    # Start searching from the 'bible' folder in parallel
    files_to_download: List[str] = list_files_recursively_parallel("bible")
    
    if not files_to_download:
        print("\n[WARNING] No files found via API listing.")
        print("Check your RLS policies or if the folder 'bible' exists.")
    else:
        total: int = len(files_to_download)
        print(f"Found {total} files. Starting parallel download with {MAX_DOWNLOAD_WORKERS} workers...")
        
        # Parallel download using its own worker count
        with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
            executor.map(download_file, files_to_download)

    print("\nProcess completed.")
