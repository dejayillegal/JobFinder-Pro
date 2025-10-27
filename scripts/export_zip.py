#!/usr/bin/env python3
"""Export JobFinder Pro project as a ZIP file for distribution."""

import os
import zipfile
from pathlib import Path
from datetime import datetime

# Files and directories to exclude
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '.git',
    '.venv',
    'venv',
    'node_modules',
    '.next',
    'dist',
    'build',
    '*.egg-info',
    '.pytest_cache',
    '.coverage',
    'htmlcov',
    '.env',
    '*.log',
    '.DS_Store',
    'uploads/*',
    '*.db',
    '*.sqlite'
]

def should_exclude(path: str) -> bool:
    """Check if path should be excluded from ZIP."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # Pattern like *.pyc
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern.endswith('/*'):
            # Pattern like uploads/*
            if pattern[:-2] in path_str:
                return True
        else:
            # Exact match or directory name
            if pattern in path_str.split(os.sep):
                return True
    return False

def create_export_zip():
    """Create ZIP file with project contents."""
    project_root = Path.cwd()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'jobfinder-pro-{timestamp}.zip'
    
    print(f"🗜️  Creating export ZIP: {zip_filename}")
    print("=" * 50)
    
    file_count = 0
    total_size = 0
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip if excluded
                if should_exclude(file_path):
                    continue
                
                # Get relative path
                rel_path = file_path.relative_to(project_root)
                
                # Add to ZIP
                zipf.write(file_path, rel_path)
                file_count += 1
                total_size += file_path.stat().st_size
                
                # Print progress
                if file_count % 10 == 0:
                    print(f"  Added {file_count} files...", end='\r')
    
    zip_size = Path(zip_filename).stat().st_size
    
    print(f"\n✅ Export complete!")
    print("=" * 50)
    print(f"Files:          {file_count}")
    print(f"Original size:  {total_size / 1024 / 1024:.2f} MB")
    print(f"ZIP size:       {zip_size / 1024 / 1024:.2f} MB")
    print(f"Compression:    {(1 - zip_size / total_size) * 100:.1f}%")
    print(f"Output:         {zip_filename}")
    print("=" * 50)

if __name__ == "__main__":
    create_export_zip()
