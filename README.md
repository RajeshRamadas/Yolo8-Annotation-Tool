# Yolo8 Annotation Tool

## Project Synopsis

The **Yolo8 Annotation Tool** is a comprehensive application designed for annotating images with bounding boxes. It is built using Python and leverages the PyQt6 library for the graphical user interface. The tool is intended to facilitate the creation of annotated datasets for machine learning models, particularly for object detection tasks.
Additionally, there is an option to generate data in VOC XML and COCO json format.

## Key Features

### Image Loading and Display

- **Load Images**: Load images from a folder or a specific image file.
- **Image Settings**: Apply various settings such as width, height, rotation, flip, color jitter, random crop,  brightness, and contrast to the images.

### Drawing and Managing Bounding Boxes

- **Bounding Box Creation**: Draw bounding boxes using mouse events.
- **Undo/Redo**: Undo and redo actions for bounding box modifications.

### Annotation Management

- **Save/Load Annotations**: Save and load annotations in formats (e.g., txt).
- **Delete Annotations**: Delete existing annotations.
- **Validate Annotations**: Ensure the correctness of annotations and all files are annotated
- **Validate Overlapping Annotations**: Check if bounding box are Overlapping 

### Dataset Management

- **Organize Files**: Organize files and create necessary folders for YOLOv8.
- **Dataset Splitting**: Split datasets for training and validation purposes.

### Annotation Format
- **YOLO Annotation Format**
- **VOC XML**
- **COCO JSON**

### Addition feature
- **PNG CONVERTER**: Any image format will be converted to png image with height and width given in GUI.(Tool supports only .png image format)
- **TRAINING DATASET**: images are split for training dataset(Test, Training, Validation)

## Limitation

- **Single Category Annotation**: This tool currently supports annotating images with only one category or class per project.
- **Single image format support**: This tool currently supports only one images format(.png)(consider using PNG CONVERTER)

## Annotation format
The YOLOv8 model annotation format typically consists of text files with the same name as the corresponding image file. Each line in the text file represents one object in the image and follows this structure:

![img.png](02-Implementation/image/doc/img.png)

**Explanation of the Components:**

  **class_id:** An integer representing the category of the object.

  **x_center:** The x-coordinate of the bounding box center, normalized to the image width (value between 0 and 1).

  **y_center:** The y-coordinate of the bounding box center, normalized to the image height (value between 0 and 1).

  **width:** The width of the bounding box, normalized to the image width (value between 0 and 1).

  **height:** The height of the bounding box, normalized to the image height (value between 0 and 1).
  
**Example:**
For an image named image1.jpg, the corresponding annotation file would be image1.txt and might contain:

- **0 0.5 0.5 0.2 0.3**
- **1 0.75 0.25 0.1 0.2**

**In this example:**

The first line represents an object of class 0 with a bounding box centered at (50%, 50%) of the image, with a width of 20% and height of 30%.

The second line represents an object of class 1 with a bounding box centered at (75%, 25%).

This format is essential for training YOLOv8 models effectively.
  
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
   cd 02-Implementation

2. **Install the Required Dependencies:**
    ```bash
    cd install_script
    pip install -r requirements.txt

3. **Run the Application:**
    ```bash
    # This will launch the Yolo8 Annotation Tool interface.
    python main.py
    
    or
    
    # This will launch the Yolo8 Annotation Tool interface using exe for windows machine .
    ./02-Implementation/exe/yolo8_annotation.exe

   
## Application 

![img.png](02-Implementation/image/doc/app.png)

## Conclusion
The Yolo8 Annotation Tool is designed to be user-friendly and efficient, providing a robust set of features for creating annotated datasets for machine learning training. It simplifies the process of image annotation, making it accessible for both novice and experienced users in the field of computer vision.
