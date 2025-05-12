import importlib.util
import subprocess
import sys
import os

REQUIRED = [
    'PyQt6',
    'matplotlib',
    'numpy',
    'networkx',
]

def is_installed(pkg):
    return importlib.util.find_spec(pkg) is not None

def main():
    missing = [pkg for pkg in REQUIRED if not is_installed(pkg)]
    if not missing:
        print("All required packages are already installed.")
        return
    print(f"Missing packages: {', '.join(missing)}")
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        print("All dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.")

if __name__ == '__main__':
    main() 