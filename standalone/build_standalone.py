import os
import subprocess
import sys

def build():
    print("Building standalone ERD Tool...")
    
    # Ensure we are in the standalone directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # PyInstaller command components
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "ERD_Tool",
        # Add frontend dist
        "--add-data", "frontend/dist;frontend/dist",
        # Add core logic (one level up)
        "--add-data", "../core;core",
        # Ensure xlrd is included
        "--hidden-import", "xlrd",
        # Main script
        "app.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"EXE file located at: {os.path.join(os.getcwd(), 'dist', 'ERD_Tool.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
