# Yolo8 Annotation Tool

## Project Synopsis

The **Yolo8 Annotation Tool** is a comprehensive application designed for annotating images with bounding boxes. It is built using Python and leverages the PyQt6 library for the graphical user interface. The tool is intended to facilitate the creation of annotated datasets for machine learning models, particularly for object detection tasks.

## Key Features

### Image Loading and Display

- **Load Images**: Load images from a folder or a specific image file.
- **Image Settings**: Apply various settings such as width, height, rotation, brightness, and contrast to the images.

### Drawing and Managing Bounding Boxes

- **Bounding Box Creation**: Draw bounding boxes using mouse events.
- **Undo/Redo**: Undo and redo actions for bounding box modifications.

### Annotation Management

- **Save/Load Annotations**: Save and load annotations in formats (e.g., txt).
- **Delete Annotations**: Delete existing annotations.
- **Validate Annotations**: Ensure the correctness of annotations and all files are annotated

### Dataset Management

- **Organize Files**: Organize files and create necessary folders for YOLOv8.
- **Dataset Splitting**: Split datasets for training and validation purposes.

## Limitation

- **Single Category Annotation**: This tool currently supports annotating images with only one category or class per project.

## Installation Instructions

### Prerequisites

Before installing the Yolo8 Annotation Tool, make sure you have the following installed on your system:

- **Python 3.7+**: Ensure Python is installed. You can download it from [python.org](https://www.python.org/downloads/).
- **pip**: Python package manager, usually installed with Python.

### Installation Steps & Execution

1. **Clone the Repository**:

   ```bash
   git clone hhttps://github.com/RajeshRamadas/Yolo8-Annotation-Tool.git
   cd yolo8-annotation-tool
2. **Create and Activate a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install the Required Dependencies:**
    ```bash
    cd install_script
    pip install -r requirements.txt

4. **Run the Application:**
    ```bash
    # This will launch the Yolo8 Annotation Tool interface.
    python main.py

## Conclusion
The Yolo8 Annotation Tool is designed to be user-friendly and efficient, providing a robust set of features for creating annotated datasets for machine learning training. It simplifies the process of image annotation, making it accessible for both novice and experienced users in the field of computer vision.