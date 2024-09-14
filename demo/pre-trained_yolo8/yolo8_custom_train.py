from ultralytics import YOLO

model = YOLO("best.pt")  # load a pretrained model (recommended for training)
# Use the model
results = model(r"C:\Users\uie65064\Documents\GitHub\Yolo8-Annotation-Tool\demo\annotation_dataset\converted_png\images\test\download (1).png")  # predict on an image
