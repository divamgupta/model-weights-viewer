#!/bin/bash

# Exit on error
set -e


eval "$(conda shell.bash hook)"


if [ ! -d "./env/backend_env" ]; then
    mkdir -p ./env
    conda create -y --prefix ./env/backend_env python=3.11
    conda activate ./env/backend_env
fi



# Install required packages if not already installed
pip install pyinstaller PyQt5 PyQtWebEngine Pillow
pip install torch

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
