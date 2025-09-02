import streamlit as st
from PIL import Image
import os
import sqlite3
import bcrypt
import pandas as pd
import numpy as np
import json
import requests
import time
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import plotly.express as px
import plotly.graph_objects as go
import random
import logging

# Import your custom modules
from utils.disease_detector import predict_disease
from utils.yield_predictor import predict_yield, crop_map, season_map, state_map

# Configuration
class Config:
    DB_NAME = "agroai.db"
    MAX_UPLOAD_SIZE_MB = 5
    DEFAULT_FARM_SIZE = 5.0
    ASSET_DIR = "assets"
    TEST_IMAGES_DIR = "test_images"

os.makedirs(Config.ASSET_DIR, exist_ok=True)
os.makedirs(Config.TEST_IMAGES_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Translation dictionary
translations = {
    "en": {
        "login": "Login",
        "logout": "Logout",
        "username": "Username",
        "password": "Password",
        "submit": "Submit",
        "welcome": "Welcome",
        "invalid_credentials": "Invalid username or password",
        "register": "Register",
        "full_name": "Full Name",
        "email": "Email",
        "confirm_password": "Confirm Password",
        "registration_success": "Registration successful! Please login",
        "password_mismatch": "Passwords do not match",
        "invalid_email": "Invalid email address",
        "crop_yield": "Crop Yield Prediction",
        "predict": "Predict",
        "disease_detection": "Plant Disease Detection",
        "upload_image": "Upload Leaf Image",
        "analyze": "Analyze",
        "weather_forecast": "Weather Forecast",
        "enter_location": "Enter Location",
        "fetch_weather": "Fetch Weather",
        "language": "Language",
        "english": "English",
        "hindi": "Hindi",
        "marathi": "Marathi",
        "model_status": "Model Status Check",
        "model_working": "Model is working correctly",
        "model_not_working": "Model is not working",
        "test_images": "Test with sample images",
        "run_diagnostic": "Run Diagnostic",
        "diagnostic_results": "Diagnostic Results",
        "model_file_exists": "Model file exists",
        "model_file_missing": "Model file not found",
        "model_loaded": "Model loaded successfully",
        "model_load_failed": "Model failed to load",
        "prediction_made": "Prediction completed",
        "prediction_failed": "Prediction failed",
        "healthy_sample": "Test with healthy leaf",
        "diseased_sample": "Test with diseased leaf",
        "diagnostic_page": "Model Diagnostics",
        "check_status": "Check Model Status",
        "select_crop": "Select Crop",
        "select_season": "Select Season",
        "select_state": "Select State",
        "area": "Area (hectares)",
        "rainfall": "Annual Rainfall (mm)",
        "fertilizer": "Fertilizer (kg/hectare)",
        "pesticide": "Pesticide (kg/hectare)",
        "predicted_yield": "Predicted Yield (tons/hectare)",
        "crop_type": "Crop Type",
        "season": "Season",
        "state": "State",
    },
    "hi": {
        "login": "लॉगिन",
        "logout": "लॉगआउट",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "submit": "जमा करें",
        "welcome": "स्वागत हे",
        "invalid_credentials": "अमान्य उपयोगकर्ता नाम या पासवर्ड",
        "register": "पंजीकरण करें",
        "full_name": "पूरा नाम",
        "email": "ईमेल",
        "confirm_password": "पासवर्ड की पुष्टि कीजिये",
        "registration_success": "पंजीकरण सफल! कृपया लॉगिन करें",
        "password_mismatch": "पासवर्ड मेल नहीं खा रहे हैं",
        "invalid_email": "अमान्य ईमेल पता",
        "crop_yield": "फसल उपज पूर्वानुमान",
        "predict": "भविष्यवाणी करें",
        "disease_detection": "पौधे की बीमारी का पता लगाना",
        "upload_image": "पत्ती की छवि अपलोड करें",
        "analyze": "विश्लेषण",
        "weather_forecast": "मौसम का पूर्वानुमान",
        "enter_location": "स्थान दर्ज करें",
        "fetch_weather": "मौसम प्राप्त करें",
        "language": "भाषा",
        "english": "अंग्रेज़ी",
        "hindi": "हिंदी",
        "marathi": "मराठी",
        "select_crop": "फसल चुनें",
        "select_season": "मौसम चुनें",
        "select_state": "राज्य चुनें",
        "area": "क्षेत्र (हेक्टेयर)",
        "rainfall": "वार्षिक वर्षा (मिमी)",
        "fertilizer": "उर्वरक (किग्रा/हेक्टेयर)",
        "pesticide": "कीटनाशक (किग्रा/हेक्टेयर)",
        "predicted_yield": "अनुमानित उपज (टन/हेक्टेयर)",
        "crop_type": "फसल का प्रकार",
        "season": "मौसम",
        "state": "राज्य",
    },
    "mr": {
        "login": "लॉगिन",
        "logout": "लॉगआउट",
        "username": "वापरकर्तानाव",
        "password": "पासवर्ड",
        "submit": "प्रस्तुत",
        "welcome": "स्वागत आहे",
        "invalid_credentials": "अवैध वापरकर्तानाव किंवा पासवर्ड",
        "register": "नोंदणी करा",
        "full_name": "पूर्ण नाव",
        "email": "ईमेल",
        "confirm_password": "पासवर्डची पुष्टी करा",
        "registration_success": "नोंदणी यशस्वी! कृपया लॉगिन करा",
        "password_mismatch": "पासवर्ड जुळत नाहीत",
        "invalid_email": "अवैध ईमेल पत्ता",
        "crop_yield": "पीक उत्पन्न अंदाज",
        "predict": "अंदाज लावा",
        "disease_detection": "वनस्पती रोग ओळख",
        "upload_image": "पानाची प्रतिमा अपलोड करा",
        "analyze": "विश्लेषण",
        "weather_forecast": "हवामान अंदाज",
        "enter_location": "स्थान प्रविष्ट करा",
        "fetch_weather": "हवामान मिळवा",
        "language": "भाषा",
        "english": "इंग्रजी",
        "hindi": "हिंदी",
        "marathi": "मराठी",
        "select_crop": "पीक निवडा",
        "select_season": "हंगाम निवडा",
        "select_state": "राज्य निवडा",
        "area": "क्षेत्रफळ (हेक्टर)",
        "rainfall": "वार्षिक पाऊस (मिमी)",
        "fertilizer": "खत (किलो/हेक्टर)",
        "pesticide": "कीटकनाशक (किलो/हेक्टर)",
        "predicted_yield": "अंदाजित उत्पन्न (टन/हेक्टर)",
        "crop_type": "पिकाचा प्रकार",
        "season": "हंगाम",
        "state": "राज्य",
    }
}

def t(key):
    lang = st.session_state.get("language", "en")
    return translations.get(lang, translations["en"]).get(key, key)

# Database helpers
def init_db():
    conn = sqlite3.connect(Config.DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        name TEXT,
        email TEXT UNIQUE,
        farm_size REAL DEFAULT ?,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """, (Config.DEFAULT_FARM_SIZE,))
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(hashed, password):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validate_email_address(email):
    try:
        return validate_email(email)["email"]
    except EmailNotValidError:
        return None

# Weather API call with caching
@st.cache_data(ttl=3600)
def get_weather(location):
    # Mock weather data for demo
    return {
        "temp": round(random.uniform(15, 35), 1),
        "humidity": random.randint(40, 90),
        "wind_speed": round(random.uniform(1.0, 10.0), 1),
        "description": random.choice(["Clear Sky", "Partly Cloudy", "Cloudy", "Light Rain"]),
        "city": location,
        "country": "IN"
    }

# Create some test images for diagnostics
def create_test_images():
    # Create a healthy leaf image (mostly green)
    healthy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    healthy_img[:, :, 1] = 200  # Green channel
    healthy_img[:, :, 0] = 100  # Red channel
    healthy_img[:, :, 2] = 100  # Blue channel
    
    # Add some texture
    for i in range(10):
        x, y = random.randint(0, 99), random.randint(0, 99)
        healthy_img[x:x+20, y:y+20, 1] = 230  # Brighter green patches
    
    healthy_pil = Image.fromarray(healthy_img)
    healthy_path = os.path.join(Config.TEST_IMAGES_DIR, "healthy_leaf.jpg")
    healthy_pil.save(healthy_path)
    
    # Create a diseased leaf image (more color variation)
    diseased_img = np.zeros((100, 100, 3), dtype=np.uint8)
    diseased_img[:, :, 1] = 150  # Less green
    
    # Add disease spots (brown/yellow patches)
    for i in range(15):
        x, y = random.randint(0, 99), random.randint(0, 99)
        size = random.randint(5, 15)
        
        # Brown/yellow spots
        diseased_img[x:x+size, y:y+size, 0] = 180  # Red
        diseased_img[x:x+size, y:y+size, 1] = 150  # Green
        diseased_img[x:x+size, y:y+size, 2] = 100  # Blue
    
    diseased_pil = Image.fromarray(diseased_img)
    diseased_path = os.path.join(Config.TEST_IMAGES_DIR, "diseased_leaf.jpg")
    diseased_pil.save(diseased_path)
    
    return healthy_path, diseased_path

# Diagnostic page to check if model is working
def render_model_diagnostic():
    st.header("Model Status Check")
    
    # Create test images if they don't exist
    if not os.path.exists(Config.TEST_IMAGES_DIR):
        os.makedirs(Config.TEST_IMAGES_DIR)
    
    healthy_path, diseased_path = create_test_images()
    
    st.subheader("Disease Detection Model Test")
    
    # Test with sample images
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(healthy_path, caption="Healthy leaf sample", use_column_width=True)
        if st.button("Test with healthy leaf"):
            with st.spinner("Analyzing..."):
                img = Image.open(healthy_path)
                label, confidence = predict_disease(img)
                st.success(f"Prediction: {label} ({confidence:.2f}% confidence)")
                if "healthy" in label.lower():
                    st.success("✅ Correctly identified healthy leaf!")
                else:
                    st.warning("⚠️ Misclassified healthy leaf as diseased")
    
    with col2:
        st.image(diseased_path, caption="Diseased leaf sample", use_column_width=True)
        if st.button("Test with diseased leaf"):
            with st.spinner("Analyzing..."):
                img = Image.open(diseased_path)
                label, confidence = predict_disease(img)
                st.success(f"Prediction: {label} ({confidence:.2f}% confidence)")
                if "healthy" not in label.lower():
                    st.success("✅ Correctly identified diseased leaf!")
                else:
                    st.warning("⚠️ Misclassified diseased leaf as healthy")
    
    st.divider()
    st.subheader("Troubleshooting Tips")
    
    st.info("""
    If your model isn't working properly, check these things:
    
    1. **Model Files**: Ensure the model files are downloaded correctly
    2. **Dependencies**: Make sure all required libraries are installed
    3. **File Paths**: Check that the model paths are correct
    4. **Image Format**: Use JPG or PNG images for best results
    """)

def render_login():
    with st.form("login_form"):
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")
        submit = st.form_submit_button(t("login"))
        if submit:
            conn = sqlite3.connect(Config.DB_NAME)
            c = conn.cursor()
            c.execute("SELECT password, name FROM users WHERE username=?", (username,))
            row = c.fetchone()
            if row and check_password(row[0], password):
                st.success(f"{t('welcome')} {row[1]}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['name'] = row[1]
                st.rerun()
            else:
                st.error(t("invalid_credentials"))
            conn.close()

def render_register():
    with st.form("register_form"):
        username = st.text_input(t("username"))
        name = st.text_input(t("full_name"))
        email = st.text_input(t("email"))
        password = st.text_input(t("password"), type="password")
        confirm_password = st.text_input(t("confirm_password"), type="password")
        farm_size = st.number_input("Farm Size (acres)", min_value=0.1, value=Config.DEFAULT_FARM_SIZE, step=0.1)
        submit = st.form_submit_button(t("register"))
        if submit:
            if password != confirm_password:
                st.error(t("password_mismatch"))
            elif not validate_email_address(email):
                st.error(t("invalid_email"))
            else:
                hashed_pw = hash_password(password)
                conn = sqlite3.connect(Config.DB_NAME)
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO users (username, password, name, email, farm_size) VALUES (?, ?, ?, ?, ?)",
                              (username, hashed_pw, name, email, farm_size))
                    conn.commit()
                    st.success(t("registration_success"))
                    time.sleep(1)
                    st.session_state['current_page'] = 'Login'
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Username or email already exists.")
                finally:
                    conn.close()

def render_crop_yield():
    st.header(t("crop_yield"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        crop_options = list(crop_map.keys())
        crop = st.selectbox(t("select_crop"), options=crop_options)
        
        season_options = list(season_map.keys())
        season = st.selectbox(t("select_season"), options=season_options)
        
        state_options = list(state_map.keys())
        state = st.selectbox(t("select_state"), options=state_options)
    
    with col2:
        area = st.number_input(t("area"), min_value=0.1, value=1.0, step=0.1)
        rainfall = st.number_input(t("rainfall"), min_value=0, value=1000, step=10)
        fertilizer = st.number_input(t("fertilizer"), min_value=0.0, value=50.0, step=1.0)
        pesticide = st.number_input(t("pesticide"), min_value=0.0, value=5.0, step=0.5)
    
    if st.button(t("predict")):
        with st.spinner("Predicting yield..."):
            prediction = predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide)
            
            if isinstance(prediction, str):
                st.error(prediction)
            else:
                st.success(f"{t('predicted_yield')}: {prediction:.2f} tons/hectare")
                
                # Show additional information
                st.info(f"""
                **Prediction Details:**
                - {t('crop_type')}: {crop}
                - {t('season')}: {season}
                - {t('state')}: {state}
                - {t('area')}: {area} hectares
                """)

def render_disease_detection():
    st.header(t("disease_detection"))
    uploaded_file = st.file_uploader(t("upload_image"), type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        if uploaded_file.size > Config.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            st.error(f"File size exceeds {Config.MAX_UPLOAD_SIZE_MB}MB limit.")
        else:
            img = Image.open(uploaded_file)
            st.image(img, caption=t("uploaded_image"), use_column_width=True)
            
            if st.button(t("analyze")):
                with st.spinner("Analyzing image..."):
                    label, confidence = predict_disease(img)
                    
                    if "error" in label.lower():
                        st.error(f"Analysis failed: {label}")
                    else:
                        if "healthy" in label.lower():
                            st.success(f"✅ {label} ({confidence:.2f}% confidence)")
                        else:
                            st.error(f"⚠️ {label} detected ({confidence:.2f}% confidence)")
                            st.info("**Recommendation**: Consider using appropriate treatment and removing affected leaves.")

def render_weather():
    st.header(t("weather_forecast"))
    location = st.text_input(t("enter_location"), value="Pune")
    
    if st.button(t("fetch_weather")):
        with st.spinner("Fetching weather data..."):
            weather_data = get_weather(location)
            if weather_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temperature", f"{weather_data['temp']} °C")
                with col2:
                    st.metric("Humidity", f"{weather_data['humidity']} %")
                with col3:
                    st.metric("Wind Speed", f"{weather_data['wind_speed']} m/s")
                
                st.write(f"**Conditions**: {weather_data['description']}")
                st.write(f"**Location**: {weather_data['city']}, {weather_data['country']}")
                
                # Weather advice based on conditions
                if "rain" in weather_data['description'].lower():
                    st.warning("Rain expected. Consider delaying irrigation and protecting crops from excessive moisture.")
                elif weather_data['temp'] > 30:
                    st.warning("High temperature. Ensure adequate irrigation to prevent heat stress.")
            else:
                st.error("Could not fetch weather data. Please check the location name.")

def render_home():
    st.header("AgroAI - Smart Farming Assistant")
    
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.write(f"Hello {st.session_state.get('name', 'User')}! Welcome to your farming dashboard.")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Farm Size", f"{st.session_state.get('farm_size', Config.DEFAULT_FARM_SIZE)} acres")
        with col2:
            st.metric("Recommended Crops", "3")
        with col3:
            st.metric("Weather", "Sunny")
        
        # Recent activities
        st.subheader("Recent Activities")
        st.info("No recent activities. Start by exploring the features in the sidebar.")
    else:
        st.write("""
        AgroAI helps farmers make data-driven decisions for better crop management.
        
        **Features include:**
        - Crop yield prediction
        - Plant disease detection
        - Weather forecasting
        - Crop recommendations
        
        Please login or register to access all features.
        """)

def render_sidebar():
    with st.sidebar:
        st.title("AgroAI")
        
        # Language selector
        lang = st.selectbox(
            t("language"), 
            options=["en", "hi", "mr"],
            format_func=lambda x: {"en": t("english"), "hi": t("hindi"), "mr": t("marathi")}[x],
            key="language_selector"
        )
        st.session_state.language = lang
        
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.write(f"**{t('welcome')}, {st.session_state.get('name', 'User')}**")
            
            # Navigation for logged-in users
            page_options = ["Home", "Crop Yield", "Disease Detection", "Weather", "Model Diagnostics"]
            page = st.radio("Navigate", page_options, index=0)
            
            # Logout button
            if st.button(t("logout")):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            # Navigation for guests
            page_options = ["Home", "Login", "Register"]
            page = st.radio("Navigate", page_options, index=0)
        
        st.session_state.current_page = page

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'language' not in st.session_state:
        st.session_state.language = "en"
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Initialize database
    init_db()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content based on selected page
    current_page = st.session_state.current_page
    
    if current_page == "Home":
        render_home()
    elif current_page == "Login":
        render_login()
    elif current_page == "Register":
        render_register()
    elif current_page == "Crop Yield":
        render_crop_yield()
    elif current_page == "Disease Detection":
        render_disease_detection()
    elif current_page == "Weather":
        render_weather()
    elif current_page == "Model Diagnostics":
        render_model_diagnostic()
    
    # Footer
    st.markdown("---")
    st.markdown("AgroAI © 2023 | Making farming smarter and more efficient")

if __name__ == "__main__":
    main()
