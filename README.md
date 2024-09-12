
# Yolo8 Annotation Tool
# Overview
The Yolo8 Annotation Tool is a PyQt6-based application designed for annotating images with bounding boxes. It allows users to load images, draw, resize, rotate, and delete bounding boxes, and save annotations in various formats. The tool is useful for preparing datasets for yolo8 models, such as object detection.

# Key Components
Imports:
Standard libraries: sys, os, shutil, numpy.
PyQt6 modules for GUI components.
PIL (Pillow) for image processing.
Main Window (SimpleAnnotationTool):

# Inherits from QMainWindow.
Initializes the main window with a title, size, and layout.
Contains several sections: File List Bay, Setting Bay, Display Bay, and Annotation Bay.
File List Bay:

Displays a list of image files.
Allows navigation through images using "Previous" and "Next" buttons.
Setting Bay:

Contains controls for adjusting image settings (width, height, rotation, brightness, contrast).
Display Bay:

Displays the currently loaded image.
Allows drawing, resizing, rotating, and deleting bounding boxes on the image.
Annotation Bay:

Displays details of the bounding boxes.
Contains controls for managing annotations (undo, redo, save, load, delete, validate).
Toolbar:

Contains actions for loading images, saving images, resetting image settings, and creating dataset folders.
Image Handling:

Functions for loading, displaying, and updating images.
Functions for drawing, resizing, rotating, and managing bounding boxes.
# Annotation Handling:

Functions for saving, loading, deleting, and validating annotations.
# Dataset Management:

Functions for organizing files and splitting datasets for training.
Key Functions
# Image Loading and Display:

load_images_from_folder(): Loads images from a selected folder.
load_image(): Loads a specific image and updates the display.
update_image_settings(): Applies settings like width, height, rotation, brightness, and contrast to the image.
Drawing and Managing Bounding Boxes:

start_drawing(), update_drawing(), finish_drawing(): Handle mouse events for drawing bounding boxes.
resize_bounding_box(), rotate_bounding_box(): Handle mouse events for resizing and rotating bounding boxes.
undo_bounding_box(), redo_bounding_box(): Manage undo and redo actions for bounding boxes.
delete_bounding_box(): Delete the selected bounding box.
# Annotation Management:

save_annotations(), load_annotations(), delete_annotations(), validate_annotations(): Handle saving, loading, deleting, and validating annotations.
save_annotations_as_xml(), save_annotations_as_json(): Save annotations in XML or JSON format.
Dataset Management:

create_yolo8_folders(), organize_files(), split_dataset(): Handle organizing files and splitting datasets for training.
# Example Usage
To run the application, execute the main() function, which initializes the QApplication and shows the main window.

# Conclusion
The Simple Annotation Tool is a comprehensive application for annotating images with bounding boxes. It includes functionalities for loading images, drawing, resizing, rotating, deleting bounding boxes, managing annotations, and preparing datasets for machine learning training. The tool is designed to be user-friendly and efficient for creating annotated datasets.
