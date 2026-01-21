import requests
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.config import SUPABASE_URL, SUPABASE_KEY, BUCKET_NAME, MAX_LISTING_WORKERS

def list_items_in_path(path: str) -> List[dict]:
    """Fetch all items (files and folders) from a specific path in Supabase Storage with pagination support."""
    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    all_items = []
    offset = 0
    limit = 100
    
    while True:
        payload = {
            "prefix": path,
            "limit": limit,
            "offset": offset,
            "sortBy": {"column": "name", "order": "asc"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                items = response.json()
                if not items:
                    break
                
                all_items.extend(items)
                
                # If we got fewer items than the limit, we've reached the end
                if len(items) < limit:
                    break
                
                offset += limit
            else:
                print(f"Error listing items in '{path}': Status {response.status_code} - {response.text}")
                break
        except Exception as e:
            print(f"Error listing items in '{path}': {e}")
            break
            
    if path:
        print(f"  > Scanned '{path}' - found {len(all_items)} items")
    return all_items

def list_files_recursively_parallel(base_path: str) -> List[str]:
    """Explores folders in parallel to find all files."""
    all_files = []
    folders_to_scan = [base_path]
    
    with ThreadPoolExecutor(max_workers=MAX_LISTING_WORKERS) as executor:
        while folders_to_scan:
            future_to_folder = {executor.submit(list_items_in_path, folder): folder for folder in folders_to_scan}
            folders_to_scan = []
            
            for future in as_completed(future_to_folder):
                items = future.result()
                current_folder = future_to_folder[future]
                
                for item in items:
                    name = item['name']
                    full_path = f"{current_folder}/{name}" if current_folder else name
                    
                    if item.get('id') is None:  # Folder
                        folders_to_scan.append(full_path)
                    else:  # File
                        all_files.append(full_path)
    return all_files
