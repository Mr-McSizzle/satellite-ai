# GAIA Reproducibility Package

This directory contains the manifests and build scripts required to generate a fully air-gapped reproducibility package for the GAIA system, allowing organizers to rerun the entire pipeline entirely offline.

## Why a Script?

Due to GitHub's strict 100 MB file size limit, it is not possible to directly commit the ~600 MB `RemoteCLIP-ViT-B-32.pt` model weights or the ~2 GB of PyTorch/FastAPI compiled wheels directly to the repository without Git LFS. 

To solve this, we provide a **manifest** and an automated **staging script**.

## How to Build the Offline Package

Run the provided Python script to download and structure the offline artifacts:

```bash
python reproducibility/stage_package.py
```

### What this script does:
1. **Reads `manifest.json`**: Resolves the required model checkpoints and dataset seed lists.
2. **Stages the Wheelhouse**: Executes `pip download -r backend/requirements.txt` to pull all compiled Python wheels (`.whl`) into a local `wheelhouse/` directory.
3. **Stages the Weights**: Copies or downloads the `RemoteCLIP` weights into a local `weights/` directory.
4. **Generates Installers**: Creates `install_offline.sh` and `install_offline.bat`.

Once the script finishes, the resulting `reproducibility/offline_package/` directory will contain everything needed to run GAIA. You can zip this folder and move it to the offline target machine via a USB drive.

## How to Install on the Air-Gapped Machine

Transfer the generated `offline_package` folder to the target machine, open a terminal inside it, and run the offline installer:

**On Windows:**
```cmd
install_offline.bat
```

**On Linux/Mac:**
```bash
bash install_offline.sh
```

This will force `pip` to resolve dependencies strictly from the local `wheelhouse/` folder (bypassing PyPI) and will copy the model weights into the correct `models/weights/` location. You can then run the backend and frontend servers as described in the main `README.md`.
