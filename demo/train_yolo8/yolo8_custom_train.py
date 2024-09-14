# !pip install ultralytics
# ! unzip /content/converted_png1.zip
from ultralytics import YOLO
# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch
# Use the model
model.train(data="/content/config.yaml", epochs=20)  # train the model
metrics = model.val()  # evaluate model performance on the validation set
results = model("/content/converted_png/images/test/d4c52577df97e69f39917c7f1dda8adc512dbf17_2000x2000.png")  # predict on an image