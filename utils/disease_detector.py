import numpy as np
from keras.models import load_model
from PIL import Image
import json
import os
import gdown

# Paths
MODEL_PATH = "plant_disease_model.h5"
CLASS_PATH = "disease_classes.json"

def download_if_missing():
    if not os.path.exists(MODEL_PATH):
        gdown.download("https://drive.google.com/uc?id=1S6f-gU6mMo9htxzJhNZmxwV__2SqxATp", MODEL_PATH, quiet=False)
    if not os.path.exists(CLASS_PATH):
        gdown.download("https://drive.google.com/uc?id=1J-onrbrJKyOfzd13wKHhMk92E5gBS80h", CLASS_PATH, quiet=False)

download_if_missing()

# Load class labels
with open(CLASS_PATH, "r") as f:
    class_dict = json.load(f)

def is_plant_image(image):
    """Basic check if image might be a plant leaf"""
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Check if image has 3 channels
        if len(img_array.shape) != 3 or img_array.shape[2] != 3:
            img_array = np.array(image.convert('RGB'))
            
        # Check if image is mostly green (crude plant detection)
        green_channel = img_array[:, :, 1]
        red_channel = img_array[:, :, 0]
        blue_channel = img_array[:, :, 2]
        
        # Calculate green dominance
        green_ratio = np.mean(green_channel) / (np.mean(red_channel) + np.mean(blue_channel) + 1e-6)
        return green_ratio > 1.0  # Empirical threshold
    except Exception as e:
        print(f"Image validation error: {str(e)}")
        return False

def preprocess_image(image):
    try:
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        print(f"Preprocessing error: {str(e)}")
        return None

def predict_disease(image):
    try:
        # Basic check if image might be a plant
        if not is_plant_image(image):
            return "Not a valid plant image", 0.0
            
        # Load model (do this once and cache it for production)
        model = load_model(MODEL_PATH)
        
        processed = preprocess_image(image)
        if processed is None:
            return "Image processing failed", 0.0
            
        predictions = model.predict(processed)[0]
        label_index = np.argmax(predictions)
        confidence = float(predictions[label_index])
        
        # Only return prediction if confidence is above threshold
        if confidence > 0.5:  # 50% confidence threshold
            label = class_dict[str(label_index)]
            return label, confidence * 100
        else:
            return "Uncertain - may not be a plant disease", confidence * 100
            
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return "Prediction error", 0.0
