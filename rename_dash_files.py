#!/usr/bin/env python3
import os
import sys
import select
from pathlib import Path

def get_input_with_timeout(prompt, timeout=60):
    """
    Get user input with a timeout. Returns None if timeout expires.
    
    Args:
        prompt: The prompt to display to the user
        timeout: Timeout in seconds (default 60)
    
    Returns:
        User input string or None if timeout
    """
    print(prompt, end='', flush=True)
    
    # Use select to wait for input with timeout
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    
    if ready:
        return sys.stdin.readline().strip()
    else:
        print("\n[Timeout - skipping]")
        return None

def find_available_name(base_path, original_name):
    """
    Find an available filename by appending a number.
    
    Args:
        base_path: The parent directory path
        original_name: The original filename
    
    Returns:
        An available Path object with a number appended
    """
    path_obj = Path(original_name)
    stem = path_obj.stem
    suffix = path_obj.suffix
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = base_path / new_name
        if not new_path.exists():
            return new_path
        counter += 1

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
    skipped_items = []
    
    for item in items_to_rename:
        old_name = item.name
        new_name = '_' + old_name[3:]  # Remove ' - ' and add '_'
        new_path = item.parent / new_name
        
        if dry_run:
            if new_path.exists():
                print(f"[DRY RUN] Conflict: {item} -> {new_path} (target exists)")
            else:
                print(f"[DRY RUN] Would rename: {item} -> {new_path}")
        else:
            try:
                # Check if target already exists
                if new_path.exists():
                    print(f"\nConflict: Target already exists: {new_path}")
                    response = get_input_with_timeout(
                        "Choose action - (s)kip or (r)ename with number [s/r]: ",
                        timeout=60
                    )
                    
                    if response and response.lower() in ['r', 'rename']:
                        # Find available name with number
                        new_path = find_available_name(item.parent, new_name)
                        item.rename(new_path)
                        print(f"Renamed: {old_name} -> {new_path.name}")
                        renamed_count += 1
                    else:
                        # Skip (either user chose skip or timeout occurred)
                        print(f"Skipped: {old_name}")
                        skipped_items.append(str(item))
                else:
                    # No conflict, rename normally
                    item.rename(new_path)
                    print(f"Renamed: {old_name} -> {new_name}")
                    renamed_count += 1
            except Exception as e:
                print(f"Error renaming {item}: {e}")
                skipped_items.append(str(item))
    
    if not dry_run:
        print(f"\nSuccessfully renamed {renamed_count} item(s)")
        if skipped_items:
            print(f"\nSkipped {len(skipped_items)} item(s):")
            for skipped in skipped_items:
                print(f"  - {skipped}")
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
