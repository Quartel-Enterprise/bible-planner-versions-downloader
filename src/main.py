from typing import List
from concurrent.futures import ThreadPoolExecutor

from src.core.config import SUPABASE_URL, SUPABASE_KEY, BUCKET_NAME, MAX_LISTING_WORKERS, MAX_DOWNLOAD_WORKERS
from src.core.downloader import download_file
from src.core.storage import list_files_recursively_parallel


def main() -> None:
    """Main execution point for the Bible Versions Downloader."""
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("Error: Environment variables not correctly loaded. Check your .env file.")
        return

    print(f"Exploring bucket '{BUCKET_NAME}' in parallel with {MAX_LISTING_WORKERS} workers...")
    
    # Discovery phase
    files_to_download = list_files_recursively_parallel("bible")
    
    if not files_to_download:
        print("\n[WARNING] No files found via API listing.")
        print("Check your RLS policies or if the folder 'bible' exists.")
    else:
        total = len(files_to_download)
        print(f"Found {total} files. Starting parallel download with {MAX_DOWNLOAD_WORKERS} workers...")
        
        # Download phase
        with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
            executor.map(download_file, files_to_download)

    print("\nProcess completed.")

if __name__ == "__main__":
    main()
