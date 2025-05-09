# ML Model Weights Viewer

A desktop application for visualizing model weights of ML models.


![image](https://github.com/user-attachments/assets/17aa23a9-c33e-4762-a95d-9f562e6511d5)


## Introduction
Model Weights Viewer is a tool that lets you easily view and explore the weights of machine learning models. It helps you see and understand the layers inside the model.

## Features

- Interactive visualization of weight tensors

## Installation

```bash
# Clone the repository
git clone https://github.com/divamgupta/model-weights-viewer.git
cd model-weights-visualizer

# Install dependencies
pip install -r requirements.txt

# Alternatively, install packages directly
pip install PyQt5 PyQtWebEngine Pillow torch safetensors

# Launch the application
python app.py

# Building the application 

bash build.sh

```

## Usage

1. Launch the application.
2. Choose a SafeTensors file using **File > Open** or drag and drop the file into the application window.
3. Explore and visualize the model weights using the provided interface.

## Supported Formats (TODO)

- [x] SafeTensors (.safetensors)
- [ ] PyTorch models (.pt, .pth)
- [ ] TensorFlow checkpoints (.ckpt)
- [ ] ONNX models (.onnx)



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



