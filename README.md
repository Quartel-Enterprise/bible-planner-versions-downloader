# Bible Planner - Bible Versions Downloader

A specialized utility to download and synchronize Bible versions from Supabase Storage for the Bible Planner project.

## Features

- **Parallel Discovery**: Recursively explores the Supabase Storage bucket using parallel workers for lightning-fast directory scanning.
- **High Performance Downloads**: Utilizes a separate thread pool for downloading files, maximizing your network bandwidth.
- **Automated Discovery**: Automatically finds all available translations and chapters without needing manual lists.
- **Smart Synchronization**: Only downloads new or missing files, skipping what you already have locally.
- **Original Structure**: Maintains the exact directory structure from Supabase (`bible/VERSION/BOOK/CHAPTER.json`).
- **Fully Typed**: Codebase uses Python Type Hints for better maintainability and dev experience.

## Requirements

- Python 3.9+
- `requests`
- `python-dotenv`

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install requests python-dotenv
   ```

## Configuration

Create a `.env` file in the root directory with your Supabase credentials. Note that `BUCKET_NAME` is now hardcoded to `"content"` as per project requirements.

```env
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_publishable_anon_key
```

## Performance Tuning

You can adjust the speed of the script by modifying these constants in `download_bibles.py`:

- `MAX_LISTING_WORKERS`: Number of threads for scanning directories (default: 10).
- `MAX_DOWNLOAD_WORKERS`: Number of threads for downloading files (default: 20).

## Usage

Run the downloader script:

```bash
python3 download_bibles.py
```

## Troubleshooting

### No files found (RLS Issues)
If the script fails to find files, ensure your Supabase Storage has a policy allowing public read access:

```sql
CREATE POLICY "Allow public read access" 
ON storage.objects FOR SELECT 
TO anon 
USING (bucket_id = 'content');
```

## Contributing

Always use **Type Hints** for any modifications to Python files as per the `AGENTS.md` guidelines.
