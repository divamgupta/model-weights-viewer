#!/bin/bash

# Exit on error
set -e


eval "$(conda shell.bash hook)"


if [ ! -d "./env/backend_env" ]; then
    mkdir -p ./env
    conda create -y --prefix ./env/backend_env python=3.11
fi

conda activate ./env/backend_env


# Install required packages if not already installed
pip install pyinstaller PyQt5 PyQtWebEngine Pillow
pip install torch
pip install safetensors

# Create the .spec file if it doesn't exist
if [ ! -f app.spec ]; then
    echo "Creating app.spec file"
    pyinstaller --name="Model Weights Visualizer" \
                --windowed \
                --icon=app_icon.png \
                --add-data="app_icon.png:." \
                --hidden-import=PyQt5.QtWebEngineWidgets \
                app.py
fi

# Build the app using the spec file
pyinstaller --noconfirm --clean "app.spec"

echo "Build complete!"
echo "Your app is located at: dist/Model Weights Visualizer.app"


# Create a temporary directory
DMG_TMP_DIR="$(mktemp -d)"
DMG_NAME="Model Weights Visualizer"
DMG_PATH="dist/${DMG_NAME}.dmg"

# Copy app to temporary directory
cp -R "dist/${DMG_NAME}.app" "${DMG_TMP_DIR}/"

# Create link to /Applications folder
ln -s /Applications "${DMG_TMP_DIR}"

# Create the DMG
hdiutil create -volname "${DMG_NAME}" -srcfolder "${DMG_TMP_DIR}" -ov -format UDZO "${DMG_PATH}"

# Clean up
rm -rf "${DMG_TMP_DIR}"

echo "DMG creation complete! Your DMG file is at: ${DMG_PATH}"
