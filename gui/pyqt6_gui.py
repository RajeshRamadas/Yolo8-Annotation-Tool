import sys
import os
import shutil
import numpy as np
import subprocess
import importlib.util
import json
from PIL import Image
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QFileDialog,
    QStatusBar,
    QTextEdit,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSlider,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QAction, QIcon, QImage, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint, QRect
from PIL import Image, ImageEnhance, ImageQt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox


#custom import


class CategoryInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Category ID, Name, and Path")
        self.layout = QVBoxLayout()

        self.id_label = QLabel("Category ID:")
        self.id_input = QLineEdit()
        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.id_input)

        self.name_label = QLabel("Category Name:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.path_label = QLabel("Path to .txt File:")
        self.path_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.path_label)
        self.layout.addWidget(self.path_input)
        self.layout.addWidget(self.browse_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.accept)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .txt File", "", "Text Files (*.txt)")
        if file_path:
            self.path_input.setText(file_path)

    def get_inputs(self):
        return self.id_input.text(), self.name_input.text(), self.path_input.text()

class Yolo8AnnotationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.annotation_x_label = None
        self.setWindowTitle("Yolo8 Annotation Tool")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize image list and index
        self.image_list = []
        self.current_index = 0
        self.current_image = None  # Store the current image as a PIL image
        self.bounding_boxes = []  # List to store bounding boxes
        self.undo_stack = []  # Stack to store undo actions
        self.redo_stack = []  # Stack to store redo actions
        self.image_path = None  # Path of image selected in the display window
        self.load_images = None  # Path of image selected in the display window
        self.directory_path = None # save dir for annotation files

        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create horizontal splitter for three sections
        horizontal_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout.addWidget(horizontal_splitter)

        # Create File List Bay
        self.file_list_bay = QWidget(self)
        file_list_layout = QVBoxLayout(self.file_list_bay)
        self.file_list_label = QLabel("<b>IMAGE FILES</b>", self.file_list_bay)
        file_list_layout.addWidget(self.file_list_label)
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.currentItemChanged.connect(self.on_file_selected)
        file_list_layout.addWidget(self.file_list_widget)

        # Add navigation buttons
        nav_buttons_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.show_previous_image)
        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.show_next_image)
        nav_buttons_layout.addWidget(self.prev_button)
        nav_buttons_layout.addWidget(self.next_button)
        file_list_layout.addLayout(nav_buttons_layout)

        file_list_layout.addLayout(file_list_layout)
        self.file_list_bay.setLayout(file_list_layout)

        # Create Setting Bay (10%)
        self.setting_bay = QWidget(self)
        setting_layout = QVBoxLayout(self.setting_bay)

        # Add image settings controls directly to the Setting Bay
        setting_layout.addWidget(self.create_image_settings_controls())

        self.setting_bay.setLayout(setting_layout)

        # Create Display Bay (80%)
        self.display_bay = QWidget(self)
        display_layout = QVBoxLayout(self.display_bay)

        # Create and add the image label to the display layout
        self.image_label = QLabel("Load an image to start", self.display_bay)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(QPixmap())
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.start_drawing
        self.image_label.mouseMoveEvent = self.update_drawing
        self.image_label.mouseReleaseEvent = self.finish_drawing
        display_layout.addWidget(self.image_label)

        self.display_bay.setLayout(display_layout)

        # Create Annotation Bay (10%)
        self.annotation_bay = QWidget(self)
        annotation_layout = QVBoxLayout(self.annotation_bay)

        # Add annotation controls directly to the Annotation Bay
        annotation_layout.addWidget(self.create_annotation_controls())

        self.annotation_bay.setLayout(annotation_layout)

        # Add bays to the splitter
        horizontal_splitter.addWidget(self.setting_bay)
        horizontal_splitter.addWidget(self.display_bay)
        horizontal_splitter.addWidget(self.file_list_bay)
        horizontal_splitter.addWidget(self.annotation_bay)

        # Set initial sizes for the bays
        horizontal_splitter.setSizes([100, 800, 100, 100])  # Approximate sizes based on 10:80:10 ratio

        # Create log window at the bottom
        self.log_window = QTextEdit(self)
        self.log_window.setReadOnly(True)
        self.log_window.setMinimumHeight(100)  # Minimum height for the log window
        self.log_window.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # Horizontal policy: Expanding
            QSizePolicy.Policy.Fixed,  # Vertical policy: Fixed
        )
        main_layout.addWidget(self.log_window)

        # Create toolbar and status bar
        self.create_toolbar()
        self.setStatusBar(QStatusBar(self))

        # Log initial message
        self.log("Application started.")

        # Variables for drawing
        self.drawing = False
        self.start_point = QPoint()
        self.current_rect = QRect()
        self.image_size = (0, 0)  # Track image size
        self.offset = QPoint(100, 100)  # Example offset value

        # Update bounding box details on annotation bay
        self.update_bounding_box_details()

    def show_next_image(self):
        """Show the next image in the list."""
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.file_list_widget.setCurrentRow(self.current_index)
            self.load_image(self.image_list[self.current_index])
        else:
            self.log("No more images to show.")

    def show_previous_image(self):
        """Show the previous image in the list."""
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.file_list_widget.setCurrentRow(self.current_index)
            self.load_image(self.image_list[self.current_index])
        else:
            self.log("No more images to show.")

    def on_file_selected(self, current, previous):
        """Load the selected image from the file list."""
        if current:
            file_path = current.toolTip()  # Get the full file path from tooltip
            self.load_image(file_path)

    def create_image_settings_controls(self):
        """Create controls for adjusting image settings."""
        controls_group = QGroupBox("", self.setting_bay)  # Remove the title
        layout = QFormLayout()

        # Width Control
        self.width_spinbox = QSpinBox(self)
        self.width_spinbox.setRange(1, 10000)  # Define the range as needed
        self.width_spinbox.setValue(640)  # Default width
        self.width_spinbox.valueChanged.connect(self.update_image_settings)
        layout.addRow(QLabel("Width", self), self.width_spinbox)

        # Height Control
        self.height_spinbox = QSpinBox(self)
        self.height_spinbox.setRange(1, 10000)  # Define the range as needed
        self.height_spinbox.setValue(640)  # Default height
        self.height_spinbox.valueChanged.connect(self.update_image_settings)
        layout.addRow(QLabel("Height", self), self.height_spinbox)

        # Rotation Control
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.update_image_settings)
        layout.addRow(QLabel("Rotation (degrees)", self), self.rotation_slider)

        # Brightness Control
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_image_settings)
        layout.addRow(QLabel("Brightness", self), self.brightness_slider)

        # Contrast Control
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.update_image_settings)
        layout.addRow(QLabel("Contrast", self), self.contrast_slider)

        controls_group.setLayout(layout)
        return controls_group

    def create_annotation_controls(self):
        """Create controls for managing annotations."""
        controls_group = QGroupBox("", self.annotation_bay)  # Remove the title
        layout = QFormLayout()

        # Annotation Width
        self.annotation_width_label = QLabel("Width: N/A", self)
        layout.addWidget(self.annotation_width_label)

        # Annotation Height
        self.annotation_height_label = QLabel("Height: N/A", self)
        layout.addWidget(self.annotation_height_label)

        # Annotation X Coordinate
        self.annotation_x_label = QLabel("X: N/A", self)
        layout.addWidget(self.annotation_x_label)

        # Annotation Y Coordinate
        self.annotation_y_label = QLabel("Y: N/A", self)
        layout.addWidget(self.annotation_y_label)

        # Annotation Text Input
        self.annotation_input = QLineEdit(self)
        self.annotation_input.setPlaceholderText("Enter annotation class...")
        self.annotation_text = QLabel("Annotation class:", self)
        layout.addWidget(self.annotation_text)
        layout.addRow(QLabel("", self), self.annotation_input)

        # Undo Button
        self.undo_button = QPushButton("Undo", self)
        self.undo_button.clicked.connect(self.undo_bounding_box)
        layout.addWidget(self.undo_button)

        # Redo Button
        self.redo_button = QPushButton("Redo", self)
        self.redo_button.clicked.connect(self.redo_bounding_box)
        layout.addWidget(self.redo_button)

        # Save Annotations Button
        self.save_annotations_button = QPushButton("Save Annotations", self)
        self.save_annotations_button.clicked.connect(self.save_annotations)
        layout.addWidget(self.save_annotations_button)

        # Load Annotations Button
        self.load_annotations_button = QPushButton("Load Annotations", self)
        self.load_annotations_button.clicked.connect(self.load_annotations)
        layout.addWidget(self.load_annotations_button)

        # Delete Annotations Button
        self.delete_annotations_button = QPushButton("Delete Annotations", self)
        self.delete_annotations_button.clicked.connect(self.delete_annotations)
        layout.addWidget(self.delete_annotations_button)

        # Validate Annotations Button
        self.validate_annotations_button = QPushButton("Validate Annotations", self)
        self.validate_annotations_button.clicked.connect(self.validate_annotations)
        layout.addWidget(self.validate_annotations_button)

        # Mouse Position Label
        self.mouse_position_label = QLabel("Mouse Position: N/A", self)
        layout.addWidget(self.mouse_position_label)

        controls_group.setLayout(layout)
        return controls_group

    def update_annotation_settings(self):
        """Update annotation settings."""
        self.log(
            f"Annotation settings updated: Width={self.annotation_width_spinbox.value()}, Height={self.annotation_height_spinbox.value()}"
        )

    def add_annotation(self):
        """Add an annotation to the bounding box."""
        annotation_text = self.annotation_input.text()
        if annotation_text:
            if self.bounding_boxes:
                last_box = self.bounding_boxes[-1]
                self.log(
                    f"Annotation added to box (x={last_box.left()}, y={last_box.top()}): {annotation_text}"
                )
            else:
                self.log("No bounding box to annotate.")
            self.annotation_input.clear()
            self.update_bounding_box_details()
        else:
            QMessageBox.warning(self, "Warning", "Annotation text cannot be empty!")

    def reset_image_settings(self):
        """Reset image settings to default values."""
        self.width_spinbox.setValue(640)  # Reset width to default
        self.height_spinbox.setValue(640)  # Reset height to default
        self.rotation_slider.setValue(0)  # Reset rotation to default
        self.brightness_slider.setValue(0)  # Reset brightness to default
        self.contrast_slider.setValue(0)  # Reset contrast to default

    def update_image_settings(self):
        """Update image settings based on user input."""
        try:
            if not self.image_list:
                self.log("No image loaded.")
                return

            image_path = self.image_list[self.current_index]
            image = Image.open(image_path)
            width = self.width_spinbox.value()
            height = self.height_spinbox.value()
            image = image.resize((width, height))

            rotation_angle = self.rotation_slider.value()
            brightness = self.brightness_slider.value() / 100.0 + 1.0
            contrast = self.contrast_slider.value() / 100.0 + 1.0

            image = image.rotate(rotation_angle)
            image = ImageEnhance.Brightness(image).enhance(brightness)
            image = ImageEnhance.Contrast(image).enhance(contrast)

            self.current_image = image
            self.image_size = (int(width), int(height))
            qt_image = ImageQt.ImageQt(image)
            final_pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(
                final_pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )
        except Exception as e:
            self.log(f"Error updating image settings: {e}")

    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)

        # Add Folder Path Button
        load_images_action = QAction("Load Images", self)
        load_images_action.triggered.connect(self.load_images_annotation)
        toolbar.addAction(load_images_action)

        # Save Image Action
        save_image_action = QAction(QIcon("icons/save.png"), "Save Image", self)
        save_image_action.triggered.connect(self.save_image)
        toolbar.addAction(save_image_action)

        # Reset Image Action
        reset_image_action = QAction("Reset Image", self)
        reset_image_action.triggered.connect(self.reset_image_settings)
        toolbar.addAction(reset_image_action)

        # Dataset Spliter Action
        dataset_spliter_action = QAction("Dataset Splitter", self)
        dataset_spliter_action.triggered.connect(self.create_yolo8_folders)
        toolbar.addAction(dataset_spliter_action)

        # Image png converter
        png_converter_action = QAction("PNG Converter", self)
        png_converter_action.triggered.connect(self.png_converter)
        toolbar.addAction(png_converter_action)

        # New action for converting annotations
        convert_annotations_action = QAction("VOC/COCO Format", self)
        convert_annotations_action.triggered.connect(self.show_category_input_dialog)
        toolbar.addAction(convert_annotations_action)

        # Image Reload
        images_reload_action = QAction("Images Reload", self)
        images_reload_action.triggered.connect(self.image_reload)
        toolbar.addAction(images_reload_action)

    def image_reload(self):
        """reload images"""
        if not hasattr(self, 'image_path') or not self.load_images:
            self.log("Error: Image path is not set.")
            return
        self.load_images_from_folder(self.load_images)
    def png_converter(self):
        """png converter images."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.convert_all_images_in_directory(folder_path)


    def load_images_annotation(self):
        """Add a folder containing images."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.load_images_from_folder(folder_path)

    def load_images_from_folder(self, folder_path):
        """Load images from the selected folder."""
        self.load_images = folder_path
        self.file_list_widget.clear()
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".png"):
                    file_path = os.path.join(root, file)
                    self.image_list.append(file_path)
                    item = QListWidgetItem(file)
                    item.setToolTip(file_path)  # Set tooltip with file path
                    self.file_list_widget.addItem(item)
        if self.image_list:
            self.current_index = 0
            self.load_image(self.image_list[self.current_index])
        else:
            self.log("No images found in the selected folder.")

    def show_category_input_dialog(self):
        dialog = CategoryInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_id, category_name, txt_file_path = dialog.get_inputs()
            if not category_id or not category_name or not txt_file_path:
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return
            self.convert_txt_to_coco(category_id, category_name, txt_file_path)
            self.coco_to_voc()

    def coco_to_voc(self):
        # Load COCO JSON file
        coco_json_path = os.path.join(self.directory_path, 'annotations_coco.json')
        with open(coco_json_path, 'r') as f:
            coco_data = json.load(f)

        # Create a mapping from category_id to category name
        self.category_mapping = {category['id']: category['name'] for category in coco_data['categories']}

        # Process each image in the COCO dataset
        for image in coco_data['images']:
            image_id = image['id']
            file_name = image['file_name']
            width = image['width']
            height = image['height']

            # Create the XML structure for Pascal VOC
            annotation = ET.Element("annotation")
            ET.SubElement(annotation, "filename").text = file_name

            # Add size information
            size = ET.SubElement(annotation, "size")
            ET.SubElement(size, "width").text = str(width)
            ET.SubElement(size, "height").text = str(height)
            ET.SubElement(size, "depth").text = "3"  # Assuming RGB images

            # Find annotations for the current image
            annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]

            for ann in annotations:
                category_id = ann['category_id']
                bbox = ann['bbox']  # COCO format [x_min, y_min, width, height]

                # Convert to VOC format (xmin, ymin, xmax, ymax)
                x_min = int(bbox[0])
                y_min = int(bbox[1])
                x_max = int(bbox[0] + bbox[2])
                y_max = int(bbox[1] + bbox[3])

                # Ensure bounding box coordinates are within the image dimensions
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(width, x_max)
                y_max = min(height, y_max)

                # Create object element in XML
                obj = ET.SubElement(annotation, "object")
                if category_id in self.category_mapping:
                    ET.SubElement(obj, "name").text = self.category_mapping[category_id]
                else:
                    print(f"Warning: Category ID {category_id} not found in mapping. Skipping annotation.")
                    continue

                ET.SubElement(obj, "pose").text = "Unspecified"
                ET.SubElement(obj, "truncated").text = "0"
                ET.SubElement(obj, "difficult").text = "0"

                # Create bounding box element
                bndbox = ET.SubElement(obj, "bndbox")
                ET.SubElement(bndbox, "xmin").text = str(x_min)
                ET.SubElement(bndbox, "ymin").text = str(y_min)
                ET.SubElement(bndbox, "xmax").text = str(x_max)
                ET.SubElement(bndbox, "ymax").text = str(y_max)

            # Save the XML file for each image
            xml_file_path = os.path.join(self.directory_path, f"{os.path.splitext(file_name)[0]}.xml")
            tree = ET.ElementTree(annotation)
            tree.write(xml_file_path)

            print(f"Converted {file_name} to {xml_file_path} in VOC format.")

    def convert_txt_to_coco(self, category_id, category_name, txt_file_path):

        self.directory_path = os.path.dirname(txt_file_path)

        # Initialize COCO structure
        coco = {
            "images": [],
            "annotations": [],
            "categories": [{"id": int(category_id), "name": category_name}]
        }

        annotation_id = 1
        for txt_file in os.listdir(self.directory_path):
            if txt_file.endswith('.txt'):
                txt_file_path = os.path.join(self.directory_path, txt_file)
                image_id = os.path.splitext(os.path.basename(txt_file_path))[0]

                # Read the corresponding image to get its dimensions
                image_file_path = os.path.join(self.directory_path, f"{image_id}.png")
                if not os.path.exists(image_file_path):
                    self.log(f"Image file {image_file_path} does not exist.")
                    return

                with Image.open(image_file_path) as img:
                    width, height = img.size

                # Add image info to COCO
                coco["images"].append({
                    "id": image_id,
                    "file_name": f"{image_id}.png",
                    "width": width,
                    "height": height
                })

                # Read and parse the .txt file
                with open(txt_file_path, 'r') as file:
                    for line in file:
                        parts = line.strip().split()
                        # category_id = int(parts[0]) + 1  # Assuming category IDs start from 0 in YOLO format
                        category_id = int(parts[0])
                        x_center = float(parts[1]) * width
                        y_center = float(parts[2]) * height
                        bbox_width = float(parts[3]) * width
                        bbox_height = float(parts[4]) * height
                        x_min = x_center - bbox_width / 2
                        y_min = y_center - bbox_height / 2

                        # Add annotation info to COCO
                        coco["annotations"].append({
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": category_id,
                            "bbox": [x_min, y_min, bbox_width, bbox_height],
                            "area": bbox_width * bbox_height,
                            "iscrowd": 0
                        })
                        annotation_id += 1

        # Save COCO JSON file
        coco_output_path = os.path.join(self.directory_path, 'annotations_coco.json')
        with open(coco_output_path, 'w') as coco_file:
            json.dump(coco, coco_file, indent=4)

        self.log(f"Converted annotations to COCO format at {coco_output_path}")

    def next_image(self):
        """Show the next image in the list."""
        if self.image_list and self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.load_image(self.image_list[self.current_index])

    def previous_image(self):
        """Show the previous image in the list."""
        if self.image_list and self.current_index > 0:
            self.current_index -= 1
            self.load_image(self.image_list[self.current_index])

    def rotate_left(self):
        """Rotate the image 90 degrees to the left."""
        current_angle = self.rotation_slider.value()
        self.rotation_slider.setValue((current_angle - 90) % 360)  # Rotate left by 90 degrees

    def rotate_right(self):
        """Rotate the image 90 degrees to the right."""
        current_angle = self.rotation_slider.value()
        self.rotation_slider.setValue((current_angle + 90) % 360)  # Rotate right by 90 degrees

    def load_image(self, file_path):
        """Load an image from the specified file path."""
        try:
            self.image_path = file_path
            self.current_index = self.file_list_widget.row(self.file_list_widget.currentItem())
            image = Image.open(file_path)
            self.current_image = QImage(
                image.tobytes(), image.width, image.height, image.width * 3, QImage.Format.Format_RGB888
            )
            self.update_image_settings()
            self.log(f"Loaded image: {file_path}")
            self.bounding_boxes = []
            self.undo_stack = []
            self.redo_stack = []

            self.reset_image_settings()

        except Exception as e:
            self.log(f"Failed to load image: {e}")

    def save_image(self):
        """Save the current image."""
        if not self.current_image:
            self.log("No image to save.")
            return

        # Get the base name of the image file without extension
        image_name = os.path.basename(self.image_path)
        file_name, _ = os.path.splitext(image_name)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", self.image_path, "Images (*.png)")
        if file_path:
            self.current_image.save(file_path)
            self.log(f"Image saved to {file_path}.")

    def start_drawing(self, event):
        """Start drawing a bounding box."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_image:
                self.drawing = True
                self.start_point = event.position().toPoint() - self.offset
                self.current_rect = QRect(self.start_point, self.start_point).normalized()

    def update_drawing(self, event):
        """Update the bounding box while drawing."""
        if self.drawing:
            current_pos = event.position().toPoint() - self.offset
            self.current_rect = QRect(self.start_point, current_pos).normalized()

            # Boundary checking
            if self.current_image:
                image_width, image_height = self.image_size
                if self.current_rect.left() < 0:
                    self.current_rect.setLeft(0)
                if self.current_rect.top() < 0:
                    self.current_rect.setTop(0)
                if self.current_rect.right() > image_width:
                    self.current_rect.setRight(image_width)
                if self.current_rect.bottom() > image_height:
                    self.current_rect.setBottom(image_height)

            self.update_display()
            self.update_mouse_position(event.position().toPoint())

    def update_mouse_position(self, pos):
        # Convert to relative coordinates based on image size
        x = (pos.x() - self.offset.x())
        y = (pos.y() - self.offset.y())

        if self.current_image:
            x = min(max(x, 0), self.image_size[0])
            y = min(max(y, 0), self.image_size[1])

        self.mouse_position_label.setText(f"Mouse Position: X={x}, Y={y}")

    def finish_drawing(self, event):
        if self.drawing:
            self.drawing = False
            if not self.current_rect.isNull() and self.current_rect.width() > 0 and self.current_rect.height() > 0:
                self.bounding_boxes.append(self.current_rect)
                self.undo_stack.append(('add', self.current_rect))
                self.redo_stack.clear()  # Clear redo stack when a new action is performed
            self.update_display()

    def undo_bounding_box(self):
        if self.undo_stack:
            action, box = self.undo_stack.pop()
            if action == 'add':
                self.bounding_boxes.remove(box)
                self.redo_stack.append(('add', box))
            elif action == 'remove':
                self.bounding_boxes.append(box)
                self.redo_stack.append(('remove', box))
            self.update_display()

    def redo_bounding_box(self):
        if self.redo_stack:
            action, box = self.redo_stack.pop()
            if action == 'add':
                self.bounding_boxes.append(box)
                self.undo_stack.append(('add', box))
            elif action == 'remove':
                self.bounding_boxes.remove(box)
                self.undo_stack.append(('remove', box))
            self.update_display()

    def save_annotations(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            self.log("Error: Image path is not set.")
            return

        if self.annotation_input.text().strip() == "":
            QMessageBox.warning(self, "Warning!", "Update Annotation Class")
            return

        # Get the base name of the image file without extension
        image_name = os.path.basename(self.image_path)
        file_name, _ = os.path.splitext(image_name)
        # Get the directory path
        directory_path = os.path.dirname(self.image_path)
        # Create text file name using the image file name
        annotation_file_name = f"{file_name}.txt"

        annotation_file_path = os.path.join(directory_path, annotation_file_name)
        # Get image dimensions
        image_width, image_height = self.image_size

        # Prepare annotations in YOLO format (or another format)
        annotations = []
        for box in self.bounding_boxes:

            width = box.width()
            height = box.height()
            x_min = box.left()
            y_min = box.top()
            x_max = box.width() + x_min
            y_max = box.height() + y_min

            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min

            x_norm = center_x / image_width
            y_norm = center_y / image_width
            width_norm = width / image_width
            height_norm = height / image_width

            object_class_id = self.annotation_input.text()  # Assuming this returns object class ID

            # Append the YOLO formatted data (class, x_center, y_center, width, height)
            annotations.append(f"{object_class_id} {x_norm:.2f} {y_norm:.2f} {width_norm:.2f} {height_norm:.2f}")

        # Save to a text file
        with open(annotation_file_path, 'w') as f:
            for annotation in annotations:
                f.write(annotation + "\n")

        if not annotations:
            self.log(f"Annotations is missing, try to draw bounding box.")
        else:
            self.log(f"Annotations saved in {annotation_file_path}.")

        # save image with updated DIM
        self.save_image()

    def delete_annotations(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            self.log("Error: Image path is not set.")
            return
        # Get the base name of the image file without extension
        image_name = os.path.basename(self.image_path)
        file_name, _ = os.path.splitext(image_name)
        # Get the directory path
        directory_path = os.path.dirname(self.image_path)
        # Create text file name using the image file name
        annotation_file_name = f"{file_name}.txt"

        # Combine directory path and file name
        annotation_file_path = os.path.join(directory_path, annotation_file_name)

        if os.path.exists(annotation_file_path):
            reply = QMessageBox.question(self, 'Confirmation',
                                         f"Are you sure you want to delete {annotation_file_path}?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(annotation_file_path)
                    QMessageBox.information(self, 'Success', f'File {annotation_file_path} deleted successfully.')
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to delete file: {e}')
            else:
                QMessageBox.information(self, 'Cancelled', 'File deletion cancelled.')
        else:
            QMessageBox.warning(self, 'File Not Found', f'File {annotation_file_path} does not exist.')

    def load_annotations(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            self.log("Error: Image path is not set.")
            return
        try:
            image_width, image_height = self.image_size
            # Get the base name of the image file without extension
            image_name = os.path.basename(self.image_path)
            file_name, _ = os.path.splitext(image_name)
            # Get the directory path
            directory_path = os.path.dirname(self.image_path)
            # Create text file name using the image file name
            annotation_file_name = f"{file_name}.txt"

            annotation_file_path = os.path.join(directory_path, annotation_file_name)

            annotations = []
            with open(annotation_file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    # Each line is in the format: class_id center_x center_y width height
                    class_id, x_norm, y_norm, width_norm, height_norm = map(float, line.strip().split())

                    # Scale the normalized values to the actual image size
                    x = float(x_norm) * image_width
                    y = float(y_norm) * image_height
                    width = float(width_norm) * image_width
                    height = float(height_norm) * image_height

                    x = int(x - (width / 2))
                    y = int(y - (height / 2))
                    # width = int(x + (width / 2))
                    # height = int(y + (height / 2))
                    annotations.append((x, y, width, height))

            # Iterate over each bounding box in annotations
            for box in annotations:
                # Extract the x, y, width, and height from the box
                x = float(box[0])
                y = float(box[1])
                width = float(box[2])
                height = float(box[3])

                # Create a QRect object using the extracted values
                self.bounding_boxes.append(QRect(x, y, width, height))

            self.log("Annotations loaded.")
            self.update_display()
        except FileNotFoundError:
            self.log("No annotation file found.")

    def update_display(self):
        if self.current_image:
            qt_image = ImageQt.ImageQt(self.current_image)
            pixmap = QPixmap.fromImage(qt_image)

            # Draw bounding boxes
            painter = QPainter(pixmap)
            pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            for box in self.bounding_boxes:
                painter.drawRect(box)
            if self.drawing:
                painter.drawRect(self.current_rect)
            painter.end()

            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

            # Update bounding box details
            self.update_bounding_box_details()

    def update_bounding_box_details(self):
        if self.bounding_boxes:
            last_box = self.bounding_boxes[-1]  # Show details for the last box added

            # Calculate normalized values
            image_width, image_height = self.image_size
            width = last_box.width()
            height = last_box.height()
            x_min = last_box.left()
            y_min = last_box.top()
            x_max = last_box.width() + x_min
            y_max = last_box.height() + y_min

            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min

            x_norm = center_x / image_width
            y_norm = center_y / image_width
            width_norm = width / image_width
            height_norm = height / image_width

            # Display the normalized values in the annotation bay
            self.annotation_width_label.setText(f"Width: {width_norm:.4f}")
            self.annotation_height_label.setText(f"Height: {height_norm:.4f}")
            self.annotation_x_label.setText(f"X : {x_norm:.4f}")
            self.annotation_y_label.setText(f"Y : {y_norm:.4f}")

        else:
            self.annotation_width_label.setText("Width: N/A")
            self.annotation_height_label.setText("Height: N/A")
            self.annotation_x_label.setText("X : N/A")
            self.annotation_y_label.setText("Y : N/A")

    def log(self, message):
        self.log_window.append(message)

    def create_yolo8_folders(self):
        """
        Create the necessary folder structure for YOLOv8 training data.

        Parameters:
        base_path (str): The root directory where the YOLOv8 dataset folders will be created.
        """
        # Define the base path where the dataset folders will be created
        base_folder = 'yolo8_dataset'
        folder_path = QFileDialog.getExistingDirectory(self, "Dataset Spliter location")
        dataset_path = os.path.join(folder_path, base_folder)

        # Check for valid path
        if not folder_path:
            self.log(f"Invalid Directory : {folder_path}")
            return

        # Check is 'yolo8_dataset' folder already exist
        if not os.path.exists(dataset_path):
            # Define the folder structure
            self.organize_files(folder_path)
            self.split_dataset(folder_path)
            QMessageBox.information(self, "Success", f"Training dataset generated. {folder_path}")
        else:
            QMessageBox.information(self, "Warning", f"Directory already exist: {folder_path}/{base_folder}")
            self.log(f"Directory already exist: {folder_path}/{base_folder}")
            self.log(f"==> Delete: {folder_path}/{base_folder}")

    def organize_files(self, source_dir):
        """
        Organize files into separate 'images' and 'labels' folders.

        Parameters:
        source_dir (str): The directory containing mixed image and label files.
        target_images_dir (str): The directory to move image files to.
        target_labels_dir (str): The directory to move label files to.
        """
        # Create folder path for Images and labels
        target_images_dir = os.path.join(source_dir, f"images")
        target_labels_dir = os.path.join(source_dir, f"labels")

        # Ensure the target directories exist
        os.makedirs(target_images_dir, exist_ok=True)
        os.makedirs(target_labels_dir, exist_ok=True)

        # List all files in the source directory
        files = os.listdir(source_dir)

        for file in files:
            # Construct full file path
            file_path = os.path.join(source_dir, file)

            if os.path.isfile(file_path):
                # Determine file extension
                _, ext = os.path.splitext(file)

                # Check if file is an image or a label
                if ext.lower() in ['.png']:  # Add or remove extensions as needed
                    # Move image files
                    shutil.move(file_path, os.path.join(target_images_dir, file))
                    self.log(f"Moved image png file: {file}")
                elif ext.lower() == '.txt':
                    # Move label files
                    shutil.move(file_path, os.path.join(target_labels_dir, file))
                    self.log(f"Moved label xml file: {file}")
                elif ext.lower() == '.xml':
                    # Move label files
                    shutil.move(file_path, os.path.join(target_labels_dir, file))
                    self.log(f"Moved label xml file: {file}")
                elif ext.lower() == '.json':
                    # Move label files
                    shutil.move(file_path, os.path.join(target_labels_dir, file))
                    self.log(f"Moved label json file: {file}")

    def split_dataset(self, base_path, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2):
        """
        Split dataset into training, validation, and test sets.

        Parameters:
        base_path (str): The root directory of the dataset.
        train_ratio (float): Ratio of data used for training.
        val_ratio (float): Ratio of data used for validation.
        test_ratio (float): Ratio of data used for testing.
        """

        # Paths for images and labels
        images_path = os.path.join(base_path, "images")
        labels_path = os.path.join(base_path, "labels")

        # Ensure these directories exist
        assert os.path.exists(images_path), f"Images path {images_path} does not exist."
        assert os.path.exists(labels_path), f"Labels path {labels_path} does not exist."

        # Get list of all images
        # all_ann_txt = [f for f in os.listdir(labels_path) if os.path.isfile(os.path.join(labels_path, f))]
        all_ann_txt = [f for f in os.listdir(labels_path) if
                       os.path.isfile(os.path.join(labels_path, f)) and f.endswith('.txt')]
        # Shuffle and split
        np.random.shuffle(all_ann_txt)

        total_ann_txt = len(all_ann_txt)
        train_end = int(train_ratio * total_ann_txt)
        val_end = int((train_ratio + val_ratio) * total_ann_txt)

        train_ann_txt = all_ann_txt[:train_end]
        val_ann_txt = all_ann_txt[train_end:val_end]
        test_ann_txt = all_ann_txt[val_end:]

        train_xml = []
        train_images = []
        for file in train_ann_txt:
            # Get the base name without extension and add .png
            base_name = os.path.splitext(file)[0]
            png_file = base_name + '.png'
            train_images.append(png_file)
            xml_file = base_name + '.xml'
            train_xml.append(xml_file)

        val_xml = []
        val_images = []
        for file in val_ann_txt:
            # Get the base name without extension and add .png
            base_name = os.path.splitext(file)[0]
            png_file = base_name + '.png'
            val_images.append(png_file)
            xml_file = base_name + '.xml'
            val_xml.append(xml_file)

        test_xml = []
        test_images = []
        for file in test_ann_txt:
            # Get the base name without extension and add .png
            base_name = os.path.splitext(file)[0]
            png_file = base_name + '.png'
            test_images.append(png_file)
            xml_file = base_name + '.xml'
            test_xml.append(xml_file)

        # Helper function to move files
        def move_files(file_list, src_folder, dst_folder):
            for file in file_list:
                shutil.move(os.path.join(src_folder, file), os.path.join(dst_folder, file))
                label_file = file.replace('.png', '.txt')  # Assuming image files are .jpg and label files are .txt
                xml_file = file.replace('.png', '.xml')  # Assuming image files are .jpg and label files are .txt
                if os.path.exists(os.path.join(src_folder, label_file)):
                    shutil.move(os.path.join(src_folder, label_file), os.path.join(dst_folder, label_file))
                if os.path.exists(os.path.join(src_folder, label_file)):
                    shutil.move(os.path.join(src_folder, xml_file), os.path.join(dst_folder, xml_file))

        # Create destination folders
        for folder in ['train', 'val', 'test']:
            os.makedirs(os.path.join(images_path, folder), exist_ok=True)
            os.makedirs(os.path.join(labels_path, folder), exist_ok=True)

        # Move txt files to respective folders
        move_files(train_ann_txt, labels_path, os.path.join(labels_path, 'train'))
        move_files(test_ann_txt, labels_path, os.path.join(labels_path, 'val'))
        move_files(val_ann_txt, labels_path, os.path.join(labels_path, 'test'))

        # Move xml files to respective folders
        move_files(train_xml, labels_path, os.path.join(labels_path, 'train'))
        move_files(val_xml, labels_path, os.path.join(labels_path, 'val'))
        move_files(test_xml, labels_path, os.path.join(labels_path, 'test'))

        # Move JPG files to respective folders
        move_files(train_images, images_path, os.path.join(images_path, 'train'))
        move_files(val_images, images_path, os.path.join(images_path, 'val'))
        move_files(test_images, images_path, os.path.join(images_path, 'test'))

    def validate_annotations(self):
        if not hasattr(self, 'image_path') or not self.image_path:
            self.log("Error: Image path is not set.")
            return
        # Get the directory path
        directory_path = os.path.dirname(self.image_path)
        if directory_path:
            # Get the base names of all .txt and .png files
            txt_files = {os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.txt')}
            png_files = {os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.png')}

            if not txt_files:
                QMessageBox.warning(self, "Validation Result", f"Missing Annotation .txt files")
                return

            # Find .txt files without corresponding .png files
            missing_files = [f"{png_file}.txt" for png_file in png_files if png_file not in txt_files]

            if missing_files:
                missing_files_str = "\n".join(missing_files)
                QMessageBox.warning(self, "Validation Result",
                                    f"The following .png files do not have corresponding annotation .txt files: "
                                    f"\nDir : {directory_path}\n{missing_files_str}")
            else:
                QMessageBox.information(self, "Validation Result", "All annotation .txt files exist for "
                                                                   "corresponding .png files.")

    def convert_image_to_png(self, input_path, output_path):
        try:
            with Image.open(input_path) as img:
                img.save(output_path, 'PNG')
                self.log(f"Converted {input_path} to {output_path}")
        except Exception as e:
            self.log(f"Error converting {input_path}: {e}")

    def convert_all_images_in_directory(self, directory_path):
        # Ensure the output directory exists
        output_directory = os.path.join(directory_path, 'converted_png')
        os.makedirs(output_directory, exist_ok=True)

        # Loop through all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    # Open the image to determine if it's a valid image file
                    with Image.open(file_path) as img:
                        # Construct output file path
                        base_name, _ = os.path.splitext(filename)
                        output_file_path = os.path.join(output_directory, f"{base_name}.png")
                        # Convert and save the image
                        self.convert_image_to_png(file_path, output_file_path)
                except IOError:
                    # Not an image file or can't open it
                    self.log(f"Skipping non-image file or unreadable file: {file_path}")
        self.log(f"==> PNG image files : {output_directory}")



