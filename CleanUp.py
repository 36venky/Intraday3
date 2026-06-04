import os
import glob

def cleanup_project(folder_path):
    # Delete txt and log files (top-level only)
    for pattern in ("*.txt", "*.log","*.csv","*.json"):
        for file in glob.glob(os.path.join(folder_path, pattern)):
            try:
                os.remove(file)
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"Failed to delete file {file}: {e}")


cleanup_project("C:\\Users\\91702\\OneDrive\\Desktop\\Intraday\\Signals")
cleanup_project("C:\\Users\\91702\\OneDrive\\Desktop\\Intraday")
cleanup_project("C:\\Users\\91702\\OneDrive\\Desktop\\Intraday\\Modules\\logs")