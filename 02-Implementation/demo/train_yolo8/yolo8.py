import os
from pathlib import Path

# Install YOLOv8 if not already installed
try:
    import ultralytics
except ImportError:
    os.system('pip install ultralytics')

# Define training function
def train_yolov8(data_yaml_path, model_cfg='yolov8n.yaml', weights='yolov8n.pt', epochs=100, img_size=640, batch_size=16):
    """
    Function to train YOLOv8 model.

    :param data_yaml_path: Path to the dataset YAML file.
    :param model_cfg: Model configuration (e.g., 'yolov8n.yaml', 'yolov8s.yaml', etc.).
    :param weights: Path to the pre-trained weights or 'yolov8n.pt' for a starting point.
    :param epochs: Number of training epochs.
    :param img_size: Input image size.
    :param batch_size: Batch size for training.
    """
    # Ensure that the data YAML file exists
    if not Path(data_yaml_path).exists():
        print(f"Error: The dataset YAML file does not exist at {data_yaml_path}")
        return

    # YOLOv8 training command with the updated syntax
    os.system(f"yolo train data={data_yaml_path} model={weights} epochs={epochs} imgsz={img_size} batch={batch_size}")

# Path to the dataset YAML file
data_yaml_path = r'C:\Users\uie65064\Desktop\sample_images\converted_png\test_dataset\dataset.yaml'

# Train YOLOv8
train_yolov8(
    data_yaml_path=data_yaml_path,
    model_cfg='yolov8n.yaml',  # Choose the model (yolov8n, yolov8s, etc.)
    weights='yolov8n.pt',      # Start from the YOLOv8 nano weights
    epochs=100,                # Train for 100 epochs
    img_size=640,              # Resize images to 640x640
    batch_size=16              # Use batch size of 16
)
