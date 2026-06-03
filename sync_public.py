import os
import shutil
import sys
import subprocess
from pathlib import Path

# Config
DEFAULT_TARGET_NAME = "SCIML_QF_Public"

def sync():
    # Source is directory of this script
    source_dir = Path(__file__).resolve().parent
    
    # Target is default sibling directory
    target_dir = source_dir.parent / DEFAULT_TARGET_NAME
    
    print(f"=== SCIML QF Public Repo Sync ===")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    
    # 1. Ensure target directory exists and is initialized with git
    if not target_dir.exists():
        print(f"\nTarget directory '{target_dir}' does not exist.")
        choice = input("Do you want to create it? [y/N]: ").strip().lower()
        if choice == 'y':
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            print("Sync cancelled.")
            return
            
    git_dir = target_dir / ".git"
    if not git_dir.exists():
        print(f"\nInitializing git repository in '{target_dir}'...")
        subprocess.run(["git", "init"], cwd=str(target_dir), check=True)
        # Create a basic .gitignore for the public repo to ignore OS files, etc.
        gitignore_path = target_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("__pycache__/\n*.pyc\n.DS_Store\nThumbs.db\n.venv/\nenv/\n")
            print("Created a default .gitignore in the target repository.")

    # 2. Identify modules to copy (folders starting with 00, 01, etc.)
    modules = sorted([
        d for d in source_dir.iterdir()
        if d.is_dir() and d.name[0:2].isdigit()
    ])
    
    print(f"\nFound {len(modules)} module folders in source.")
    
    # 3. Clean and Copy code directories
    for module in modules:
        source_code_dir = module / "code"
        target_module_dir = target_dir / module.name
        target_code_dir = target_module_dir / "code"
        
        # Clean existing code folder in target to prevent stale files
        if target_code_dir.exists():
            shutil.rmtree(target_code_dir)
            
        if source_code_dir.exists() and source_code_dir.is_dir():
            print(f"  -> Copying {module.name}/code ...")
            target_code_dir.mkdir(parents=True, exist_ok=True)
            # Copy all files from source code to target code
            for item in source_code_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target_code_dir / item.name)
                else:
                    shutil.copy2(item, target_code_dir / item.name)
        else:
            # If no code dir, make sure we clean up target module dir if empty
            if target_module_dir.exists() and not any(target_module_dir.iterdir()):
                target_module_dir.rmdir()
                
    # 4. Copy shared root files
    root_files_to_copy = ["requirements.txt", "readme.md", "README.md", "LICENSE"]
    for filename in root_files_to_copy:
        src_file = source_dir / filename
        if src_file.exists():
            print(f"  -> Copying {filename} ...")
            shutil.copy2(src_file, target_dir / filename)
            
    # 5. Git Status & Commit in target
    print("\nChecking git status in public repository...")
    status_proc = subprocess.run(["git", "status", "--short"], cwd=str(target_dir), capture_output=True, text=True)
    if not status_proc.stdout.strip():
        print("No changes detected. Public repository is already up to date!")
        return
        
    print("\nChanges detected in target repository:")
    print(status_proc.stdout)
    
    commit_choice = input("Do you want to stage and commit these changes? [y/N]: ").strip().lower()
    if commit_choice == 'y':
        commit_msg = input("Enter commit message (press Enter for default: 'Sync code from private repo'): ").strip()
        if not commit_msg:
            commit_msg = "Sync code from private repo"
            
        subprocess.run(["git", "add", "."], cwd=str(target_dir), check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(target_dir), check=True)
        print("Changes committed successfully.")
        
        push_choice = input("Do you want to push to remote? [y/N]: ").strip().lower()
        if push_choice == 'y':
            # Check if remote exists
            remotes_proc = subprocess.run(["git", "remote"], cwd=str(target_dir), capture_output=True, text=True)
            if not remotes_proc.stdout.strip():
                print("No remote configured for the public repository yet.")
                remote_url = input("Enter remote repository URL (or press Enter to skip): ").strip()
                if remote_url:
                    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=str(target_dir), check=True)
                    print(f"Remote 'origin' added: {remote_url}")
                    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=str(target_dir), capture_output=True, text=True)
                    current_branch = branch_proc.stdout.strip() or "main"
                    if current_branch == "master":
                        subprocess.run(["git", "branch", "-M", "main"], cwd=str(target_dir), check=True)
                        current_branch = "main"
                    subprocess.run(["git", "push", "-u", "origin", current_branch], cwd=str(target_dir), check=True)
            else:
                branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=str(target_dir), capture_output=True, text=True)
                current_branch = branch_proc.stdout.strip() or "main"
                subprocess.run(["git", "push", "origin", current_branch], cwd=str(target_dir), check=True)
    else:
        print("Changes not committed.")

if __name__ == "__main__":
    try:
        sync()
    except Exception as e:
        print(f"\nError occurred: {e}", file=sys.stderr)
        sys.exit(1)
