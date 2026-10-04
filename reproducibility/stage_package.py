import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "reproducibility" / "manifest.json"
PACKAGE_DIR = ROOT_DIR / "reproducibility" / "offline_package"
WHEELHOUSE_DIR = PACKAGE_DIR / "wheelhouse"
WEIGHTS_DIR = PACKAGE_DIR / "weights"

def load_manifest():
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Downloaded successfully.")

def stage_wheelhouse(manifest):
    print("Staging backend wheelhouse for offline installation...")
    WHEELHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    req_path = ROOT_DIR / manifest["dependencies"]["backend"]
    
    # Download Python wheels for offline installation
    subprocess.run([
        "pip", "download", "-r", str(req_path), "-d", str(WHEELHOUSE_DIR)
    ], check=True)
    
    # Copy requirements file to package
    shutil.copy(req_path, PACKAGE_DIR / "requirements.txt")
    print("Wheelhouse staged successfully.")

def stage_weights(manifest):
    print("Staging model weights...")
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for model in manifest["models"]:
        dest = WEIGHTS_DIR / model["filename"]
        # If the model is already in the main repo models/weights, just copy it to save time
        existing_path = ROOT_DIR / "models" / "weights" / model["filename"]
        if existing_path.exists():
            print(f"Found existing weights at {existing_path}. Copying to reproducibility package...")
            shutil.copy(existing_path, dest)
        else:
            download_file(model["url"], dest)
    print("Weights staged successfully.")

def build_static_frontend():
    print("Building static frontend bundle for offline deployment...")
    FRONTEND_DIR = ROOT_DIR / "frontend-code"
    
    # We compile the frontend on the connected machine so the offline machine doesn't need Node.js/npm.
    # Check if npm is installed
    if shutil.which("npm"):
        subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)
        
        # Move the built dist folder into the reproducibility package
        dest_dist = PACKAGE_DIR / "frontend_dist"
        if dest_dist.exists():
            shutil.rmtree(dest_dist)
        shutil.copytree(FRONTEND_DIR / "dist", dest_dist)
        print("Frontend bundled successfully.")
    else:
        print("WARNING: npm not found. Skipping static frontend build.")

def create_install_scripts():
    print("Creating offline install scripts...")
    sh_script = """#!/bin/bash
echo "Installing GAIA offline..."
pip install --no-index --find-links=wheelhouse -r requirements.txt
echo "Copying weights..."
mkdir -p ../models/weights
cp weights/* ../models/weights/
echo "Deploying frontend static bundle..."
rm -rf ../frontend-code/dist
cp -r frontend_dist ../frontend-code/dist
echo "Offline setup complete."
"""
    bat_script = """@echo off
echo Installing GAIA offline...
pip install --no-index --find-links=wheelhouse -r requirements.txt
echo Copying weights...
mkdir ..\\models\\weights 2>nul
copy weights\\* ..\\models\\weights\\
echo Deploying frontend static bundle...
rmdir /s /q ..\\frontend-code\\dist 2>nul
xcopy /E /I frontend_dist ..\\frontend-code\\dist
echo Offline setup complete.
"""
    with open(PACKAGE_DIR / "install_offline.sh", "w") as f:
        f.write(sh_script)
    with open(PACKAGE_DIR / "install_offline.bat", "w") as f:
        f.write(bat_script)
        
    if os.name == "posix":
        os.chmod(PACKAGE_DIR / "install_offline.sh", 0o755)

def main():
    print("Building GAIA Reproducibility Package...")
    manifest = load_manifest()
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    stage_weights(manifest)
    stage_wheelhouse(manifest)
    build_static_frontend()
    create_install_scripts()
    
    print(f"\n✅ Reproducibility package staged at: {PACKAGE_DIR}")
    print("Zip this directory and provide it to evaluators for air-gapped installation.")

if __name__ == "__main__":
    main()
