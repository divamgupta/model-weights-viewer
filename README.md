# Model Weights Visualizer

A desktop application for visualizing model weights in SafeTensor format.

## Building the Application

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Building on macOS

1. **Prepare the Icon** (Optional)
   - Place a 1024x1024 PNG image named `icon_1024.png` in the project directory
   - Run the icon creation script:
     ```
     chmod +x create_icns.sh
     ./create_icns.sh
     ```

2. **Build the Application**
   - Make the build script executable:
     ```
     chmod +x build.sh
     ```
   - Run the build script:
     ```
     ./build.sh
     ```

3. **After Building**
   - The finished application will be in the `dist` folder as `Model Weights Visualizer.app`
   - You can move this .app file to your Applications folder or distribute it

## Usage

1. Open the application
2. Use the "Open File" button or drag and drop SafeTensor files
3. View the visualization of model weights

## Supported File Types

- `.safetensors` - SafeTensor model weight files
