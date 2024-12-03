# !pip install ultralytics
# ! unzip /content/converted_png1.zip
from ultralytics import YOLO
# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch
# Use the model
model.train(data="/content/config.yaml", epochs=50)  # train the model
metrics = model.val()  # evaluate model performance on the validation set
results = model("/content/converted_png3/images/test/3.png")  # predict on an image