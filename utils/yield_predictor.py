import pandas as pd
import joblib
import os
import gdown

MODEL_PATH = os.path.join("notebooks", "yield_model.pkl")

# Download model if not present
if not os.path.exists(MODEL_PATH):
    gdown.download("https://drive.google.com/uc?id=1OTkpN5Yhig9DwHRaX5Luyf1_khkeMGQU", MODEL_PATH, quiet=False)

model = joblib.load(MODEL_PATH)

crop_map = {
    "Arecanut": 0, "Arhar/Tur": 1, "Castor seed": 2,
    "Coconut": 3, "Cotton(lint)": 4, "Rice": 5, "Wheat": 6, "Maize": 7
}
season_map = {"Kharif": 0, "Rabi": 1, "Whole Year": 2}
state_map = {"Assam": 0, "Punjab": 1, "Tamil Nadu": 2, "Maharashtra": 3}

def predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide):
    if model is None:
        return "Model not loaded."

    features = pd.DataFrame([[ 
        crop_map.get(crop, -1),
        season_map.get(season, -1),
        state_map.get(state, -1),
        area,
        rainfall,
        fertilizer,
        pesticide
    ]], columns=["Crop", "Season", "State", "Area", "Annual_Rainfall", "Fertilizer", "Pesticide"])

    prediction = model.predict(features)[0]
    return float(prediction)
