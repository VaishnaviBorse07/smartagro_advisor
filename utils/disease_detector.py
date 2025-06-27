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

def is_plant_image(image_array):
    """Check if the image contains plant-like features based on color distribution"""
    # Convert to HSV color space for better color analysis
    hsv_image = np.array(image.convert('HSV'))
    
    # Calculate green pixel percentage (plants are typically green)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_pixels = np.sum((hsv_image[:,:,0] >= lower_green[0]) & 
                         (hsv_image[:,:,0] <= upper_green[0]) &
                         (hsv_image[:,:,1] >= lower_green[1]) &
                         (hsv_image[:,:,2] >= lower_green[2]))
    green_percentage = green_pixels / (image.size[0] * image.size[1])
    
    return green_percentage > 0.2  # At least 20% green pixels

def preprocess_image(image):
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    return np.expand_dims(img_array, axis=0)

def predict_disease(image):
    try:
        # First check if the image contains plant-like features
        if not is_plant_image(image):
            return "Not a plant image", 0.0, False
        
        model = load_model(MODEL_PATH)
        processed = preprocess_image(image)
        predictions = model.predict(processed)[0]
        label_index = np.argmax(predictions)
        label = class_dict[str(label_index)]
        confidence = float(predictions[label_index]) * 100
        
        # Add confidence threshold
        if confidence < 60.0:  # Only accept predictions with >60% confidence
            return "Uncertain prediction - may not be a plant disease", confidence, False
            
        return label, confidence, True
    except Exception as e:
        return f"Error: {str(e)}", 0.0, False

# Example usage:
if __name__ == "__main__":
    test_image = Image.open("test_plant.jpg")
    disease, confidence, is_valid = predict_disease(test_image)
    
    if is_valid:
        print(f"Detected: {disease} with {confidence:.2f}% confidence")
    else:
        print(f"Not a valid plant disease image: {disease}")
