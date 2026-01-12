import os
import glob
import shutil

EXCLUDE_DIRS = {"intraday", "venv", ".venv", "Lib", "site-packages"}

def cleanup_project(folder_path):
    # Delete txt and log files (top-level only)
    for pattern in ("*.txt", "*.log"):
        for file in glob.glob(os.path.join(folder_path, pattern)):
            try:
                os.remove(file)
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"Failed to delete file {file}: {e}")

    # Delete __pycache__ safely
    for root, dirs, _ in os.walk(folder_path):
        if any(excl in root for excl in EXCLUDE_DIRS):
            continue

        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                try:
                    shutil.rmtree(path)
                    print(f"Deleted folder: {path}")
                except Exception as e:
                    print(f"Failed to delete folder {path}: {e}")

# Usage
cleanup_project(r"C:\Users\91702\OneDrive\Desktop\Intraday")
cleanup_project(r"C:\Users\91702\OneDrive\Desktop\Intraday\Modules")
cleanup_project(r"C:\Users\91702\OneDrive\Desktop\Intraday\Modules\logs")
cleanup_project(r"C:\Users\91702\OneDrive\Desktop\Intraday\Dependencies")
cleanup_project(r"C:\Users\91702\OneDrive\Desktop\Intraday\Indicators")

