import os

import requests

from src.core.config import SUPABASE_URL, SUPABASE_KEY, BUCKET_NAME, PROJECT_ROOT


def download_file(file_path: str) -> None:
    """Downloads a file from Supabase Storage only if it doesn't exist locally."""
    # Ensure the file is saved relative to the project root
    local_path = os.path.join(PROJECT_ROOT, file_path)
    
    if os.path.exists(local_path):
        return

    from urllib.parse import quote
    quoted_path = quote(file_path)
    url = f"{SUPABASE_URL}/storage/v1/object/authenticated/{BUCKET_NAME}/{quoted_path}"
    headers = {
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
