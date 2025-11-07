#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def rename_dash_prefix(root_path, dry_run=True):
    """
    Recursively rename files and directories that start with ' - ' to start with '_'
    
    Args:
        root_path: The directory to start searching from
        dry_run: If True, only print what would be renamed without actually renaming
    """
    root = Path(root_path).resolve()
    
    if not root.exists():
        print(f"Error: Path '{root_path}' does not exist")
        return
    
    # Collect all items to rename (process depth-first to handle nested directories)
    items_to_rename = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current_dir = Path(dirpath)
        
        # Check files
        for filename in filenames:
            if filename.startswith(' - '):
                items_to_rename.append(current_dir / filename)
        
        # Check directories
        for dirname in dirnames:
            if dirname.startswith(' - '):
                items_to_rename.append(current_dir / dirname)
    
    if not items_to_rename:
        print("No files or directories found starting with ' - '")
        return
    
    print(f"Found {len(items_to_rename)} item(s) to rename:\n")
    
    renamed_count = 0
    for item in items_to_rename:
        old_name = item.name
        new_name = '_' + old_name[3:]  # Remove ' - ' and add '_'
        new_path = item.parent / new_name
        
        if dry_run:
            print(f"[DRY RUN] Would rename: {item} -> {new_path}")
        else:
            try:
                item.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming {item}: {e}")
    
    if not dry_run:
        print(f"\nSuccessfully renamed {renamed_count} item(s)")
    else:
        print(f"\nDry run complete. Run with --execute to actually rename files.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_dash_files.py <directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    # Ask user if they want to do a dry run first
    response = input("\nDo you want to do a dry run first? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n=== DRY RUN ===")
        rename_dash_prefix(target_dir, dry_run=True)
        
        # Ask if they want to proceed with actual renaming
        proceed = input("\nProceed with actual renaming? (y/n): ").strip().lower()
        if proceed in ['y', 'yes']:
            print("\n=== EXECUTING RENAMES ===")
            rename_dash_prefix(target_dir, dry_run=False)
        else:
            print("Cancelled.")
    else:
        print("\n=== EXECUTING RENAMES ===")
        rename_dash_prefix(target_dir, dry_run=False)
