import numpy as np
from keras.models import load_model
from PIL import Image
import json
import os
import gdown

# Paths
MODEL_PATH = "notebooks/plant_disease_model.h5"
CLASS_PATH = "notebooks/disease_classes.json"

def download_if_missing():
    if not os.path.exists(MODEL_PATH):
        gdown.download("https://drive.google.com/uc?id=1S6f-gU6mMo9htxzJhNZmxwV__2SqxATp", MODEL_PATH, quiet=False)
    if not os.path.exists(CLASS_PATH):
        gdown.download("https://drive.google.com/uc?id=1J-onrbrJKyOfzd13wKHhMk92E5gBS80h", CLASS_PATH, quiet=False)

download_if_missing()

# Load class labels
with open(CLASS_PATH, "r") as f:
    class_dict = json.load(f)

def preprocess_image(image):
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    return np.expand_dims(img_array, axis=0)

def predict_disease(image):
    try:
        model = load_model(MODEL_PATH)
        processed = preprocess_image(image)
        predictions = model.predict(processed)[0]
        label_index = np.argmax(predictions)
        label = class_dict[str(label_index)]
        confidence = float(predictions[label_index]) * 100
        return label, confidence
    except Exception as e:
        return "Model Load Error", 0.0
