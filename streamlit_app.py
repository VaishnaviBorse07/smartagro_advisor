import streamlit as st
from PIL import Image
import os
import bcrypt
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
from streamlit_lottie import st_lottie
import random
import sqlite3
from email_validator import validate_email, EmailNotValidError
import logging
from io import BytesIO
import base64

# =============================================
# Configuration and Constants
# =============================================

class Config:
    DB_NAME = "agroai.db"
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 1800  # 30 minutes in seconds
    DEFAULT_FARM_SIZE = 5.0
    ASSETS_DIR = "assets"
    MODEL_DIR = "models"
    MAX_UPLOAD_SIZE = 5  # MB

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs(Config.ASSETS_DIR, exist_ok=True)
os.makedirs(Config.MODEL_DIR, exist_ok=True)

# =============================================
# Translation System
# =============================================

translations = {
    "en": {
        "login": "🔐 Login", "logout": "🚪 Logout", "welcome": "✅ Welcome",
        "invalid": "❌ Invalid credentials", "username": "Username",
        "password": "Password", "login_button": "Login",
        "logged_as": "Logged in as", "crop_yield": "🌿 Crop Yield",
        "disease_detect": "🦠 Disease Detection", "home": "🌾 Home",
        "features": "📌 Features", "about": "📖 About", "contact": "📬 Contact",
        "team": "Our Team", "upload_leaf": "Upload Leaf Image",
        "analyze": "Analyze", "crop": "Crop", "season": "Season",
        "state": "State", "area": "Area (hectares)", "rainfall": "Rainfall (mm)",
        "fertilizer": "Fertilizer (kg)", "pesticide": "Pesticide (kg)",
        "predict": "Predict Yield", "hero_title": "AgroAI Advisor",
        "hero_subtitle": "Smart Agriculture Assistant",
        "register": "📝 Register", "name": "Full Name",
        "email": "Email", "confirm_password": "Confirm Password",
        "register_button": "Create Account", "have_account": "Already have an account? Login",
        "need_account": "Need an account? Register", "reg_success": "Registration successful! Please login",
        "password_mismatch": "Passwords do not match", "invalid_email": "Please enter a valid email",
        "yield_form_title": "Crop Yield Calculator",
        "disease_form_title": "Plant Disease Scanner",
        "camera_instructions": "Point your camera at a plant leaf and capture an image",
        "capture_button": "Capture Image",
        "analyze_button": "Analyze Capture",
        "treatment_title": "🌱 Treatment Recommendations",
        "treatment_advice": [
            "Remove and destroy infected plants to prevent spread",
            "Apply appropriate fungicide/insecticide as recommended",
            "Improve air circulation around plants by proper spacing",
            "Maintain proper watering schedule (avoid overwatering)"
        ],
        "yield_tips_title": "💡 Yield Optimization Tips",
        "yield_tips": [
            "Implement crop rotation to maintain soil health and reduce pests",
            "Monitor soil moisture levels regularly with smart sensors",
            "Use organic fertilizers to improve long-term soil fertility",
            "Adopt integrated pest management strategies for sustainable farming"
        ],
        "dashboard_title": "📊 Analytics Dashboard",
        "weather_title": "🌦️ Weather Forecast",
        "features_title": "🌟 Key Features",
        "about_title": "📖 About Us",
        "contact_title": "📬 Contact Us",
        "mission": "Our Mission",
        "vision": "Our Vision",
        "mission_text": "Empowering farmers with AI-driven insights for sustainable agriculture",
        "vision_text": "Transforming traditional farming through cutting-edge technology",
        "contact_info": [
            "📧 Email: smartagro@gmail.com",
            "📞 Phone: +91-xxxxxxxxx",
            "🌐 Website: www.smartagro.com",
            "📍 Address: Maharashtra,India"
        ],
        "profile": "👤 Profile",
        "farm_size": "Farm Size (hectares)",
        "location": "Farm Location",
        "save_profile": "Save Profile",
        "crop_history": "📅 Crop History",
        "add_crop": "➕ Add Crop Record",
        "crop_name": "Crop Name",
        "planting_date": "Planting Date",
        "harvest_date": "Harvest Date",
        "yield_amount": "Yield (tons)",
        "notes": "Notes",
        "add_record": "Add Record",
        "no_records": "No crop records found",
        "weather_alerts": "⚠️ Weather Alerts",
        "soil_health": "🌱 Soil Health",
        "market_prices": "💲 Market Prices",
        "language": "Language",
        "unknown": "Unknown",
        "yield_prediction_desc": "Predict harvest amounts based on environmental factors",
        "disease_detection_desc": "Identify plant diseases from leaf images",
        "analytics_desc": "View historical data and trends",
        "weather_desc": "Get localized weather forecasts",
        "soil_health_desc": "Get recommendations for soil improvement",
        "market_insights_desc": "View crop prices and market trends",
        "team_members": [
            {"name": "Vaishnavi Borse", "role": "Full Stack Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Pranjali Patil", "role": "Frontend Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Maithili Pawar", "role": "Frontend Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Yuvraj Rajure", "role": "ML Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Hardik Sonawane", "role": "ML Developer", "bio": "B.Tech in Computer Science"}
        ]
    },
    "hi": {
        "login": "🔐 लॉगिन", 
        "logout": "🚪 लॉगआउट", 
        "welcome": "✅ स्वागत है",
        "invalid": "❌ अमान्य प्रमाण", 
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड", 
        "login_button": "लॉगिन",
        "logged_as": "लॉगिन किया गया", 
        "crop_yield": "🌿 फसल उपज",
        "disease_detect": "🦠 रोग पहचान", 
        "home": "🌾 होम",
        "features": "📌 विशेषताएं", 
        "about": "📖 हमारे बारे में", 
        "contact": "📬 संपर्क करें",
        "team": "हमारी टीम", 
        "upload_leaf": "पत्ती की छवि अपलोड करें",
        "analyze": "विश्लेषण", 
        "crop": "फसल", 
        "season": "मौसम",
        "state": "राज्य", 
        "area": "क्षेत्र (हेक्टेयर)", 
        "rainfall": "वर्षा (मिमी)",
        "fertilizer": "उर्वरक (किलो)", 
        "pesticide": "कीटनाशक (किलो)",
        "predict": "उपज का अनुमान लगाएं", 
        "hero_title": "एग्रोएआई सलाहकार",
        "hero_subtitle": "स्मार्ट कृषि सहायक",
        "register": "📝 पंजीकरण", 
        "name": "पूरा नाम",
        "email": "ईमेल", 
        "confirm_password": "पासवर्ड की पुष्टि करें",
        "register_button": "खाता बनाएं", 
        "have_account": "पहले से खाता है? लॉगिन करें",
        "need_account": "खाता चाहिए? पंजीकरण करें", 
        "reg_success": "पंजीकरण सफल! कृपया लॉगिन करें",
        "password_mismatch": "पासवर्ड मेल नहीं खाते", 
        "invalid_email": "कृपया मान्य ईमेल दर्ज करें",
        "yield_form_title": "फसल उपज कैलकुलेटर",
        "disease_form_title": "पौधे की बीमारी स्कैनर",
        "camera_instructions": "पौधे की पत्ती पर अपना कैमरा लगाएं और छवि कैप्चर करें",
        "capture_button": "छवि कैप्चर करें",
        "analyze_button": "कैप्चर का विश्लेषण करें",
        "treatment_title": "🌱 उपचार सिफारिशें",
        "treatment_advice": [
            "संक्रमित पौधों को हटाकर नष्ट कर दें ताकि बीमारी न फैले",
            "सिफारिश के अनुसार उचित फफूंदनाशक/कीटनाशक लगाएं",
            "पौधों के आसपास उचित दूरी रखकर हवा का संचार बेहतर करें",
            "उचित पानी देने का समय बनाए रखें (अधिक पानी देने से बचें)"
        ],
        "yield_tips_title": "💡 उपज अनुकूलन सुझाव",
        "yield_tips": [
            "मिट्टी की सेहत बनाए रखने और कीटों को कम करने के लिए फसल चक्र अपनाएं",
            "स्मार्ट सेंसर से नियमित रूप से मिट्टी की नमी की जांच करें",
            "लंबे समय तक मिट्टी की उर्वरता बढ़ाने के लिए जैविक उर्वरकों का उपयोग करें",
            "टिकाऊ खेती के लिए एकीकृत कीट प्रबंधन रणनीतियों को अपनाएं"
        ],
        "dashboard_title": "📊 विश्लेषण डैशबोर्ड",
        "weather_title": "🌦️ मौसम पूर्वानुमान",
        "features_title": "🌟 प्रमुख विशेषताएं",
        "about_title": "📖 हमारे बारे में",
        "contact_title": "📬 संपर्क करें",
        "mission": "हमारा मिशन",
        "vision": "हमारी दृष्टि",
        "mission_text": "टिकाऊ कृषि के लिए एआई-संचालित अंतर्दृष्टि के साथ किसानों को सशक्त बनाना",
        "vision_text": "अत्याधुनिक तकनीक के माध्यम से पारंपारिक खेती को बदलना",
        "contact_info": [
            "📧 ईमेल: smartagro@gmail.com", 
            "📞 फ़ोन: +91-xxxxxxxxx",
            "🌐 वेबसाइट: www.smartagro.com", 
            "📍 पता: महाराष्ट्र, भारत"
        ],
        "profile": "👤 प्रोफाइल",
        "farm_size": "खेत का आकार (हेक्टेयर)",
        "location": "खेत का स्थान",
        "save_profile": "प्रोफाइल सहेजें",
        "crop_history": "📅 फसल इतिहास",
        "add_crop": "➕ फसल रिकॉर्ड जोड़ें",
        "crop_name": "फसल का नाम",
        "planting_date": "रोपण की तारीख",
        "harvest_date": "कटाई की तारीख",
        "yield_amount": "उपज (टन)",
        "notes": "टिप्पणियाँ",
        "add_record": "रिकॉर्ड जोड़ें",
        "no_records": "कोई फसल रिकॉर्ड नहीं मिला",
        "weather_alerts": "⚠️ मौसम चेतावनी",
        "soil_health": "🌱 मिट्टी की सेहत",
        "market_prices": "💲 बाजार कीमतें",
        "language": "भाषा",
        "unknown": "अज्ञात",
        "yield_prediction_desc": "पर्यावरणीय कारकों के आधार पर फसल उपज का अनुमान लगाएं",
        "disease_detection_desc": "पत्ती की छवियों से पौधों की बीमारियों की पहचान करें",
        "analytics_desc": "ऐतिहासिक डेटा और रुझान देखें",
        "weather_desc": "स्थानीय मौसम पूर्वानुमान प्राप्त करें",
        "soil_health_desc": "मिट्टी में सुधार के लिए सिफारिशें प्राप्त करें",
        "market_insights_desc": "फसल की कीमतें और बाजार के रुझान देखें",
        "team_members": [
            {"name": "वैष्णवी बोरसे", "role": "फुल स्टैक डेवलपर", "bio": "कंप्यूटर साइंस में बी.टेक"},  
            {"name": "प्रांजली पाटिल", "role": "फ्रंटएंड डेवलपर", "bio": "कंप्यूटर साइंस में बी.टेक"},  
            {"name": "मैथिली पवार", "role": "फ्रंटएंड डेवलपर", "bio": "कंप्यूटर साइंस में बी.टेक"},  
            {"name": "युवराज रजुरे", "role": "एमएल डेवलपर", "bio": "कंप्यूटर साइंस में बी.टेक"},  
            {"name": "हार्दिक सोनवणे", "role": "एमएल डेवलपर", "bio": "कंप्यूटर साइंस में बी.टेक"}  
        ]
    },
    "mr": {
        "login": "🔐 लॉगिन", 
        "logout": "🚪 लॉगआउट", 
        "welcome": "✅ स्वागत आहे",
        "invalid": "❌ अवैध प्रमाणपत्रे", 
        "username": "वापरकर्तानाव",
        "password": "पासवर्ड", 
        "login_button": "लॉगिन",
        "logged_as": "लॉगिन केले", 
        "crop_yield": "🌿 पीक उत्पन्न",
        "disease_detect": "🦠 रोग ओळख", 
        "home": "🌾 होम",
        "features": "📌 वैशिष्ट्ये", 
        "about": "📖 आमच्याबद्दल", 
        "contact": "📬 संपर्क",
        "team": "आमची संघ", 
        "upload_leaf": "पानाची प्रतिमा अपलोड करा",
        "analyze": "विश्लेषण", 
        "crop": "पीक", 
        "season": "हंगाम",
        "state": "राज्य", 
        "area": "क्षेत्र (हेक्टर)", 
        "rainfall": "पाऊस (मिमी)",
        "fertilizer": "खत (किलो)", 
        "pesticide": "कीटकनाशक (किलो)",
        "predict": "उत्पन्नाचा अंदाज लावा", 
        "hero_title": "अॅग्रोएआई सल्लागार",
        "hero_subtitle": "स्मार्ट शेती सहाय्यक",
        "register": "📝 नोंदणी", 
        "name": "पूर्ण नाव",
        "email": "ईमेल", 
        "confirm_password": "पासवर्डची पुष्टी करा",
        "register_button": "खाते तयार करा", 
        "have_account": "आधीपासून खाते आहे? लॉगिन करा",
        "need_account": "खाते हवे? नोंदणी करा", 
        "reg_success": "नोंदणी यशस्वी! कृपया लॉगिन करा",
        "password_mismatch": "पासवर्ड जुळत नाहीत", 
        "invalid_email": "कृपया वैध ईमेल टाका",
        "yield_form_title": "पीक उत्पन्न कॅल्क्युलेटर",
        "disease_form_title": "वनस्पती रोग स्कॅनर",
        "camera_instructions": "वनस्पतीच्या पानावर कॅमेरा लावा आणि प्रतिमा कॅप्चर करा",
        "capture_button": "प्रतिमा कॅप्चर करा",
        "analyze_button": "कॅप्चरचे विश्लेषण करा",
        "treatment_title": "🌱 उपचार शिफारसी",
        "treatment_advice": [
            "संसर्ग झालेल्या वनस्पती काढून टाका आणि नष्ट करा जेणेकरून रोग पसरू नये",
            "शिफारस केल्याप्रमाणे योग्य फंगिसाइड/कीटकनाशक वापरा",
            "योग्य अंतर ठेवून वनस्पतींच्या आजूबाजूला हवेची चांगली फेरफटका करा",
            "योग्य पाणी देण्याचे वेळापत्रक राखा (जास्त पाणी देणे टाळा)"
        ],
        "yield_tips_title": "💡 उत्पन्न वाढवण्याची टिप्स",
        "yield_tips": [
            "मातीचे आरोग्य राखण्यासाठी आणि कीटक कमी करण्यासाठी पिकांची फेरपालट करा",
            "स्मार्ट सेन्सरच्या मदतीने नियमितपणे मातीतील ओलावा तपासा",
            "दीर्घकाळापर्यंत मातीची सुपीकता वाढवण्यासाठी सेंद्रिय खते वापरा",
            "टिकाऊ शेतीसाठी एकात्मिक कीटक व्यवस्थापन धोरणे स्वीकारा"
        ],
        "dashboard_title": "📊 विश्लेषण डॅशबोर्ड",
        "weather_title": "🌦️ हवामान अंदाज",
        "features_title": "🌟 प्रमुख वैशिष्ट्ये",
        "about_title": "📖 आमच्याबद्दल",
        "contact_title": "📬 संपर्क",
        "mission": "आमचे मिशन",
        "vision": "आमचे दृष्टीकोन",
        "mission_text": "शाश्वत शेतीसाठी AI-चालित अंतर्दृष्टीसह शेतकऱ्यांना सक्षम करणे",
        "vision_text": "अत्याधुनिक तंत्रज्ञानाद्वारे पारंपारिक शेतीचे रूपांतर",
        "contact_info": [
            "📧 ईमेल: smartagro@gmail.com",
            "📞 फोन: +91-xxxxxxxxx",
            "🌐 वेबसाइट: www.smartagro.com",
            "📍 पत्ता: महाराष्ट्र, भारत"
        ],
        "profile": "👤 प्रोफाइल",
        "farm_size": "शेताचे क्षेत्र (हेक्टर)",
        "location": "शेताचे स्थान",
        "save_profile": "प्रोफाइल जतन करा",
        "crop_history": "📅 पीक इतिहास",
        "add_crop": "➕ पीक नोंद जोडा",
        "crop_name": "पिकाचे नाव",
        "planting_date": "लागवडीची तारीख",
        "harvest_date": "कापणीची तारीख",
        "yield_amount": "उत्पन्न (टन)",
        "notes": "नोट्स",
        "add_record": "नोंद जोडा",
        "no_records": "पीक नोंदी सापडल्या नाहीत",
        "weather_alerts": "⚠️ हवामान सतर्कता",
        "soil_health": "🌱 मातीचे आरोग्य",
        "market_prices": "💲 बाजारभाव",
        "language": "भाषा",
        "unknown": "अज्ञात",
        "yield_prediction_desc": "पर्यावरणीय घटकांवर आधारित पीक उत्पन्नाचा अंदाज लावा",
        "disease_detection_desc": "पानांच्या प्रतिमांवरून वनस्पती रोग ओळखा",
        "analytics_desc": "ऐतिहासिक डेटा आणि ट्रेंड पहा",
        "weather_desc": "स्थानिक हवामान अंदाज मिळवा",
        "soil_health_desc": "मातीच्या आरोग्यासाठी शिफारसी मिळवा",
        "market_insights_desc": "पिकांच्या किंमती आणि बाजारातील ट्रेंड पहा",
        "team_members": [
            {"name": "वैष्णवी बोरसे", "role": "फुल स्टॅक डेव्हलपर", "bio": "संगणक शास्त्रात बी.टेक"},  
            {"name": "प्रांजली पाटील", "role": "फ्रंटएंड डेव्हलपर", "bio": "संगणक शास्त्रात बी.टेक"},  
            {"name": "मैथिली पवार", "role": "फ्रंटएंड डेव्हलपर", "bio": "संगणक शास्त्रात बी.टेक"},  
            {"name": "युवराज रजुरे", "role": "एमएल डेव्हलपर", "bio": "संगणक शास्त्रात बी.टेक"},  
            {"name": "हार्दिक सोनवणे", "role": "एमएल डेव्हलपर", "bio": "संगणक शास्त्रात बी.टेक"}  
        ]
    }
}

def t(key, lang=None, default=None):
    """Get translation for the given key in the specified language"""
    if lang is None:
        lang = st.session_state.get('language', 'en')
    return translations.get(lang, {}).get(key, default or key)

# =============================================
# Database Functions
# =============================================

def init_db():
    """Initialize the SQLite database with required tables"""
    try:
        conn = sqlite3.connect(Config.DB_NAME)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY,
                     password TEXT NOT NULL,
                     name TEXT NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     role TEXT DEFAULT 'user',
                     farm_size REAL DEFAULT 5.0,
                     location TEXT,
                     login_attempts INTEGER DEFAULT 0,
                     last_login TIMESTAMP,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Crop history table
        c.execute('''CREATE TABLE IF NOT EXISTS crop_history
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT NOT NULL,
                     crop TEXT NOT NULL,
                     planted_date TEXT NOT NULL,
                     harvested_date TEXT,
                     yield_amount REAL,
                     notes TEXT,
                     FOREIGN KEY(username) REFERENCES users(username))''')
        
        # Disease detection history
        c.execute('''CREATE TABLE IF NOT EXISTS disease_history
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT NOT NULL,
                     image_path TEXT NOT NULL,
                     detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     disease_name TEXT,
                     confidence REAL,
                     treatment_advice TEXT,
                     FOREIGN KEY(username) REFERENCES users(username))''')
        
        # Weather cache
        c.execute('''CREATE TABLE IF NOT EXISTS weather_cache
                    (location TEXT PRIMARY KEY,
                     data TEXT NOT NULL,
                     last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        
        # Check if admin exists
        c.execute("SELECT username FROM users WHERE role='admin'")
        if not c.fetchone():
            hashed_pw = hash_password("admin123")
            c.execute('''INSERT INTO users 
                        (username, password, name, email, role, farm_size, location)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     ('admin', hashed_pw, 'Admin User', 'admin@smartagro.com', 
                      'admin', 10.0, 'Pune, India'))
            conn.commit()
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a database connection with row factory"""
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# =============================================
# Authentication Functions
# =============================================

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(hashed_password, user_password):
    """Check hashed password against user input"""
    return bcrypt.checkpw(user_password.encode(), hashed_password.encode())

def validate_email_address(email):
    """Validate email format using email-validator"""
    try:
        v = validate_email(email)
        return v["email"]
    except EmailNotValidError as e:
        logger.warning(f"Email validation failed: {str(e)}")
        return False

def register_user(username, password, name, email, farm_size, location, role="user"):
    """Register a new user"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Validate inputs
        if not username or not password or not name or not email:
            return False, t('all_fields_required')
        
        if len(password) < 8:
            return False, t('password_length_error')
        
        valid_email = validate_email_address(email)
        if not valid_email:
            return False, t('invalid_email')
        
        # Check if username or email exists
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return False, t('username_exists')
        
        c.execute("SELECT email FROM users WHERE email = ?", (valid_email,))
        if c.fetchone():
            return False, t('email_exists')
        
        # Insert new user
        hashed_pw = hash_password(password)
        c.execute('''INSERT INTO users 
                    (username, password, name, email, farm_size, location, role)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (username, hashed_pw, name, valid_email, farm_size, location, role))
        conn.commit()
        
        logger.info(f"New user registered: {username}")
        return True, t('reg_success')
        
    except sqlite3.Error as e:
        logger.error(f"Registration error: {str(e)}")
        return False, t('database_error')
    finally:
        if conn:
            conn.close()

def login_user(username, password):
    """Authenticate user"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check login attempts
        c.execute('''SELECT login_attempts, last_login 
                     FROM users WHERE username = ?''', (username,))
        result = c.fetchone()
        
        if result and result['login_attempts'] >= Config.MAX_LOGIN_ATTEMPTS:
            last_login = datetime.strptime(result['last_login'], '%Y-%m-%d %H:%M:%S')
            if (datetime.now() - last_login).seconds < 3600:  # 1 hour lockout
                return False, t('account_locked')
        
        # Get user credentials
        c.execute('''SELECT username, password, role, name, email, farm_size, location 
                     FROM users WHERE username = ?''', (username,))
        user = c.fetchone()
        
        if not user:
            return False, t('invalid')
        
        if not check_password(user['password'], password):
            # Increment failed login attempt
            c.execute('''UPDATE users 
                         SET login_attempts = login_attempts + 1,
                             last_login = CURRENT_TIMESTAMP
                         WHERE username = ?''', (username,))
            conn.commit()
            return False, t('invalid')
        
        # Reset login attempts on success
        c.execute('''UPDATE users 
                     SET login_attempts = 0,
                         last_login = CURRENT_TIMESTAMP
                     WHERE username = ?''', (username,))
        conn.commit()
        
        user_data = dict(user)
        del user_data['password']  # Don't store password in session
        
        logger.info(f"User logged in: {username}")
        return True, user_data
        
    except sqlite3.Error as e:
        logger.error(f"Login error: {str(e)}")
        return False, t('database_error')
    finally:
        if conn:
            conn.close()

# =============================================
# Crop Data Functions
# =============================================

def add_crop_record(username, crop_data):
    """Add a new crop record to database"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO crop_history 
                    (username, crop, planted_date, harvested_date, yield_amount, notes)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (username, crop_data['crop'], crop_data['planted'], 
                  crop_data['harvested'], crop_data['yield'], crop_data['notes']))
        conn.commit()
        
        return True, t('record_added')
    except sqlite3.Error as e:
        logger.error(f"Crop record error: {str(e)}")
        return False, t('record_failed')
    finally:
        if conn:
            conn.close()

def get_crop_history(username):
    """Get crop history for a user"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''SELECT id, crop, planted_date, harvested_date, yield_amount, notes
                     FROM crop_history 
                     WHERE username = ?
                     ORDER BY planted_date DESC''', (username,))
        
        records = [dict(row) for row in c.fetchall()]
        return records
    except sqlite3.Error as e:
        logger.error(f"Crop history error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

# =============================================
# Disease Detection Functions
# =============================================

def save_uploaded_file(uploaded_file, username):
    """Save uploaded file to assets directory"""
    try:
        # Create user directory if not exists
        user_dir = os.path.join(Config.ASSETS_DIR, username)
        os.makedirs(user_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leaf_{timestamp}{file_ext}"
        filepath = os.path.join(user_dir, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return filepath
    except Exception as e:
        logger.error(f"File save error: {str(e)}")
        return None

def predict_disease(image_path):
    """Predict disease from image (mock implementation)"""
    try:
        # In a real app, this would use a trained ML model
        # For now, we'll mock the response with translations
        diseases = {
            "Healthy": {
                "en": "Healthy",
                "hi": "स्वस्थ",
                "mr": "निरोगी"
            },
            "Powdery Mildew": {
                "en": "Powdery Mildew",
                "hi": "पाउडर फफूंदी",
                "mr": "पावडर बुरशी"
            },
            "Leaf Rust": {
                "en": "Leaf Rust",
                "hi": "पत्ती की जंग",
                "mr": "पानांची गंज"
            },
            "Bacterial Blight": {
                "en": "Bacterial Blight",
                "hi": "जीवाणु झुलसा",
                "mr": "जीवाणू झुलसा"
            },
            "Leaf Spot": {
                "en": "Leaf Spot",
                "hi": "पत्ती धब्बा",
                "mr": "पान डाग"
            }
        }
        
        disease_key = random.choice(list(diseases.keys()))
        disease_name = diseases[disease_key].get(st.session_state.get('language', 'en'), disease_key)
        confidence = round(random.uniform(80, 99), 1)
        
        # Treatment advice with translations
        treatments = {
            "Healthy": {
                "en": "No treatment needed. Maintain current care regimen.",
                "hi": "किसी उपचार की आवश्यकता नहीं है। वर्तमान देखभाल व्यवस्था बनाए रखें।",
                "mr": "उपचाराची गरज नाही. सध्याची काळजी व्यवस्था राखा."
            },
            "Powdery Mildew": {
                "en": "Apply sulfur or potassium bicarbonate treatments.",
                "hi": "सल्फर या पोटेशियम बाइकार्बोनेट उपचार लगाएं।",
                "mr": "सल्फर किंवा पोटॅशियम बायकार्बोनेट उपचार लावा."
            },
            "Leaf Rust": {
                "en": "Remove infected leaves and apply fungicide.",
                "hi": "संक्रमित पत्तियों को हटाकर फफूंदनाशक लगाएं।",
                "mr": "संसर्ग झालेली पाने काढून टाका आणि फंगिसाइड लावा."
            },
            "Bacterial Blight": {
                "en": "Apply copper-based bactericides and remove infected plants.",
                "hi": "कॉपर आधारित जीवाणुनाशक लगाएं और संक्रमित पौधों को हटा दें।",
                "mr": "कॉपर-आधारित बॅक्टेरिसाइड लावा आणि संसर्ग झालेल्या वनस्पती काढून टाका."
            },
            "Leaf Spot": {
                "en": "Apply fungicide and improve air circulation.",
                "hi": "फफूंदनाशक लगाएं और हवा के संचार में सुधार करें।",
                "mr": "फंगिसाइड लावा आणि हवेच्या फेरफटक्यात सुधारणा करा."
            }
        }
        
        treatment = treatments.get(disease_key, {}).get(
            st.session_state.get('language', 'en'), 
            t('consult_expert')
        )
        
        return {
            "disease": disease_name,
            "confidence": confidence,
            "treatment": treatment
        }
    except Exception as e:
        logger.error(f"Disease prediction error: {str(e)}")
        return None

def save_detection_result(username, image_path, result):
    """Save disease detection result to database"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO disease_history
                    (username, image_path, disease_name, confidence, treatment_advice)
                    VALUES (?, ?, ?, ?, ?)''',
                 (username, image_path, result['disease'], 
                  result['confidence'], result['treatment']))
        conn.commit()
        
        return True
    except sqlite3.Error as e:
        logger.error(f"Detection save error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_detection_history(username):
    """Get disease detection history for a user"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''SELECT id, image_path, detection_date, disease_name, confidence
                     FROM disease_history
                     WHERE username = ?
                     ORDER BY detection_date DESC''', (username,))
        
        records = [dict(row) for row in c.fetchall()]
        return records
    except sqlite3.Error as e:
        logger.error(f"Detection history error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

# =============================================
# Weather Functions
# =============================================

def get_cached_weather(location):
    """Get cached weather data if recent"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''SELECT data, last_updated 
                     FROM weather_cache 
                     WHERE location = ? 
                     AND datetime(last_updated) > datetime('now', '-1 hour')''',
                 (location,))
        result = c.fetchone()
        
        if result:
            return json.loads(result['data'])
        return None
    except sqlite3.Error as e:
        logger.error(f"Weather cache error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def cache_weather(location, data):
    """Cache weather data"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''INSERT OR REPLACE INTO weather_cache
                    (location, data)
                    VALUES (?, ?)''',
                 (location, json.dumps(data)))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Weather cache update error: {str(e)}")
    finally:
        if conn:
            conn.close()

def get_weather_forecast(location):
    """Get weather forecast with caching"""
    # Check cache first
    cached_data = get_cached_weather(location)
    if cached_data:
        return cached_data
    
    try:
        # In a real app, this would call a weather API
        days = 7
        base_temp = random.uniform(15, 30)
        
        forecast_data = {
            "location": location,
            "current": {
                "temp": round(base_temp, 1),
                "humidity": random.randint(40, 80),
                "wind_speed": round(random.uniform(5, 25), 1),
                "precipitation": random.randint(0, 30),
                "uv_index": random.choice(["Low", "Moderate", "High"])
            },
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "temp": round(base_temp + random.uniform(-5, 5), 1),
                    "precipitation": random.randint(0, 30),
                    "wind_speed": round(random.uniform(5, 25), 1)
                } for i in range(days)
            ]
        }
        
        # Cache the result
        cache_weather(location, forecast_data)
        
        return forecast_data
    except Exception as e:
        logger.error(f"Weather forecast error: {str(e)}")
        return None

# =============================================
# Utility Functions
# =============================================

def load_lottieurl(url):
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.error(f"Lottie load error: {str(e)}")
        return None

def predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide):
    """Improved yield prediction with more realistic factors"""
    # Base yields (tons/hectare) from agricultural research
    base_yields = {
        "Rice": 3.5, "Wheat": 2.8, "Maize": 4.2, 
        "Cotton": 1.8, "Soybean": 2.5, "Potato": 20.0
    }
    
    # State productivity factors
    state_factors = {
        "Punjab": 1.15, "Haryana": 1.10, "Uttar Pradesh": 1.05,
        "Maharashtra": 1.0, "Karnataka": 0.95, "Others": 0.90
    }
    
    # Season adjustments
    season_factors = {
        "Kharif": 1.0, "Rabi": 1.05, "Zaid": 0.95, 
        "Summer": 0.90, "Winter": 1.02
    }
    
    base = base_yields.get(crop, 3.0)
    state_factor = state_factors.get(state, state_factors["Others"])
    season_factor = season_factors.get(season, 1.0)
    
    # Calculate yield components
    rainfall_factor = 0.8 + (rainfall / 1000) * 0.2  # 0.8-1.2 range
    fertilizer_factor = 0.9 + (fertilizer / 200) * 0.3  # 0.9-1.2 range
    pesticide_factor = 1.1 - (pesticide / 50) * 0.2  # 1.1-0.9 range
    
    # Combine factors
    yield_estimate = (base * area * state_factor * season_factor * 
                     rainfall_factor * fertilizer_factor * pesticide_factor)
    
    # Add small random variation (5%)
    yield_estimate *= random.uniform(0.95, 1.05)
    
    return max(1.0, round(yield_estimate, 2))  # Ensure minimum yield

def get_image_base64(image_path):
    """Convert image to base64 for HTML display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Image conversion error: {str(e)}")
        return ""

# =============================================
# UI Components
# =============================================

def show_login_form():
    """Render login form UI"""
    with st.container():
        st.markdown(f"""
        <div style="max-width: 400px; margin: 0 auto; padding: 20px; 
                    border-radius: 10px; background: rgba(255,255,255,0.1);">
            <h2 style="text-align: center;">{t('login')}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('lottie_login'):
            st_lottie(st.session_state.lottie_login, height=150, key="login-anim")
        
        with st.form("login_form"):
            username = st.text_input(t('username'))
            password = st.text_input(t('password'), type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submit = st.form_submit_button(t('login_button'))
            with col2:
                register_btn = st.form_submit_button(t('need_account'))
            
            if login_submit:
                success, result = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = result
                    st.success(t('welcome'))
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result)
            
            if register_btn:
                st.session_state.show_register = True
                st.rerun()

def show_register_form():
    """Render registration form UI"""
    with st.container():
        st.markdown(f"""
        <div style="max-width: 400px; margin: 0 auto; padding: 20px; 
                    border-radius: 10px; background: rgba(255,255,255,0.1);">
            <h2 style="text-align: center;">{t('register')}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('lottie_login'):
            st_lottie(st.session_state.lottie_login, height=150, key="register-anim")
        
        with st.form("register_form"):
            username = st.text_input(t('username'))
            name = st.text_input(t('name'))
            email = st.text_input(t('email'))
            farm_size = st.number_input(t('farm_size'), 
                                      min_value=0.1, 
                                      value=Config.DEFAULT_FARM_SIZE, 
                                      step=0.5)
            location = st.text_input(t('location'))
            password = st.text_input(t('password'), type="password")
            confirm_password = st.text_input(t('confirm_password'), type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                register_submit = st.form_submit_button(t('register_button'))
            with col2:
                login_btn = st.form_submit_button(t('have_account'))
            
            if register_submit:
                if password != confirm_password:
                    st.error(t('password_mismatch'))
                else:
                    success, message = register_user(
                        username, password, name, email, farm_size, location
                    )
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
            
            if login_btn:
                st.session_state.show_register = False
                st.rerun()

def show_sidebar():
    """Render application sidebar"""
    with st.sidebar:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; background: rgba(255,255,255,0.1);">
            <h3>{t('profile')}</h3>
            <p><strong>{st.session_state.user['name']}</strong></p>
            <p>📍 {st.session_state.user.get('location', t('unknown'))}</p>
            <p>🌱 {st.session_state.user.get('farm_size', Config.DEFAULT_FARM_SIZE)} {t('area')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(t('logout')):
            st.session_state.clear()
            st.rerun()
        
        # Language selector
        selected_lang = st.selectbox(
            "🌐 " + t('language'),
            options=list(translations.keys()),
            index=list(translations.keys()).index(st.session_state.get('language', 'en')),
            format_func=lambda x: {"en": "English", "hi": "हिंदी", "mr": "मराठी"}[x]
        )
        st.session_state.language = selected_lang

def show_home_page():
    """Render home page content"""
    st.title(f"🌾 {t('hero_title')}")
    st.write(t('hero_subtitle'))
    
    # Load animations
    lottie_agro = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_vybwn7df.json")
    if lottie_agro:
        st_lottie(lottie_agro, height=300, key="home-anim")
    
    st.markdown("---")
    st.header(t('features_title'))
    
    cols = st.columns(3)
    features = [
        ("🌿 " + t('crop_yield'), t('yield_prediction_desc')),
        ("🦠 " + t('disease_detect'), t('disease_detection_desc')),
        ("📊 " + t('dashboard'), t('analytics_desc')),
        ("🌦️ " + t('weather'), t('weather_desc')),
        ("🌱 " + t('soil_health'), t('soil_health_desc')),
        ("💰 " + t('market_prices'), t('market_insights_desc'))
    ]
    
    for i, (title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border-radius: 10px; padding: 15px; margin-bottom: 15px; 
                        background: rgba(255,255,255,0.1); border-left: 4px solid #4CAF50;">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def show_yield_page():
    """Render crop yield prediction page"""
    st.header(t('yield_form_title'))
    
    lottie_yield = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5tkzkblw.json")
    if lottie_yield:
        st_lottie(lottie_yield, height=200, key="yield-anim")
    
    with st.form("yield_form"):
        col1, col2 = st.columns(2)
        with col1:
            crop = st.selectbox(t('crop'), ["Rice", "Wheat", "Maize", "Cotton", "Soybean", "Potato"])
            season = st.selectbox(t('season'), ["Kharif", "Rabi", "Zaid", "Summer", "Winter"])
            state = st.selectbox(t('state'), ["Maharashtra", "Punjab", "Tamil Nadu", "Uttar Pradesh", "Karnataka", "Gujarat"])
        with col2:
            area = st.number_input(t('area'), min_value=0.1, value=float(st.session_state.user.get('farm_size', Config.DEFAULT_FARM_SIZE)), step=0.1)
            rainfall = st.slider(t('rainfall'), min_value=0, max_value=2000, value=800)
            fertilizer = st.slider(t('fertilizer'), min_value=0, max_value=200, value=50)
            pesticide = st.slider(t('pesticide'), min_value=0, max_value=50, value=5)
        
        if st.form_submit_button(t('predict')):
            with st.spinner(t('calculating_yield')):
                time.sleep(1)  # Simulate processing
                result = predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide)
                st.success(f"{t('predicted_yield')}: {result:.2f} {t('tons_per_hectare')}")
                
                # Show comparison chart
                data = pd.DataFrame({
                    'Metric': [t('your_prediction'), t('region_avg'), t('best_in_region')],
                    'Yield': [result, result*0.8, result*1.3]
                })
                
                fig = px.bar(data, x='Metric', y='Yield', color='Metric',
                            color_discrete_sequence=['#4CAF50', '#FFC107', '#2E7D32'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Yield tips
                with st.expander(t('yield_tips_title')):
                    for tip in t('yield_tips'):
                        st.markdown(f"✅ {tip}")

def show_disease_page():
    """Render disease detection page"""
    st.header(t('disease_form_title'))
    
    lottie_disease = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ygiuluqn.json")
    if lottie_disease:
        st_lottie(lottie_disease, height=200, key="disease-anim")
    
    st.markdown(f"""
    <div style="border-radius: 10px; padding: 15px; margin-bottom: 20px; 
                background: rgba(255,255,255,0.1);">
        <h4>📌 {t('instructions')}</h4>
        <p>{t('for_best_results')}:</p>
        <ul>
            <li>{t('upload_clear_image')}</li>
            <li>{t('leaf_should_cover')}</li>
            <li>{t('use_natural_light')}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t('upload_image'), t('capture_image')])
    
    with tab1:
        uploaded_file = st.file_uploader(t('choose_image'), type=["jpg", "jpeg", "png"])
        if uploaded_file:
            try:
                if uploaded_file.size > Config.MAX_UPLOAD_SIZE * 1024 * 1024:
                    st.error(f"{t('file_too_large')} {Config.MAX_UPLOAD_SIZE}MB")
                else:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=t('uploaded_image'), use_container_width=True)
                    
                    if st.button(t('analyze')):
                        with st.spinner(t('analyzing_image')):
                            # Save the uploaded file
                            image_path = save_uploaded_file(uploaded_file, st.session_state.user['username'])
                            if image_path:
                                # Predict disease
                                result = predict_disease(image_path)
                                if result:
                                    st.success(f"{t('detected')}: {result['disease']} ({result['confidence']}% {t('confidence')})")
                                    
                                    # Save detection result
                                    save_detection_result(
                                        st.session_state.user['username'],
                                        image_path,
                                        result
                                    )
                                    
                                    # Show treatment advice
                                    with st.expander(t('treatment_title')):
                                        st.markdown(result['treatment'])
                                else:
                                    st.error(t('analysis_failed'))
            except Exception as e:
                st.error(f"{t('error_processing')}: {str(e)}")
    
    with tab2:
        img_file_buffer = st.camera_input(t('camera_instructions'))
        if img_file_buffer:
            try:
                image = Image.open(img_file_buffer)
                st.image(image, caption=t('captured_image'), use_container_width=True)
                
                if st.button(t('analyze_button')):
                    with st.spinner(t('analyzing_image')):
                        # Save the captured image
                        image_path = save_uploaded_file(img_file_buffer, st.session_state.user['username'])
                        if image_path:
                            # Predict disease
                            result = predict_disease(image_path)
                            if result:
                                st.success(f"{t('detected')}: {result['disease']} ({result['confidence']}% {t('confidence')})")
                                
                                # Save detection result
                                save_detection_result(
                                    st.session_state.user['username'],
                                    image_path,
                                    result
                                )
                                
                                # Show treatment advice
                                with st.expander(t('treatment_title')):
                                    st.markdown(result['treatment'])
                            else:
                                st.error(t('analysis_failed'))
            except Exception as e:
                st.error(f"{t('error_processing')}: {str(e)}")

def show_dashboard_page():
    """Render analytics dashboard page"""
    st.header(t('dashboard_title'))
    
    # Main layout
    main_col, side_col = st.columns([3, 1])
    
    with main_col:
        # Yield Trends Chart
        st.subheader(t('yield_trends'))
        crop_history = get_crop_history(st.session_state.user['username'])
        if crop_history:
            df = pd.DataFrame(crop_history)
            df['planted_date'] = pd.to_datetime(df['planted_date'])
            df = df.sort_values('planted_date')
            
            fig = px.line(
                df,
                x='planted_date',
                y='yield_amount',
                color='crop',
                markers=True,
                title=t('yield_over_time')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t('no_records'))
        
        # Disease Detection History
        st.subheader(t('disease_history'))
        detection_history = get_detection_history(st.session_state.user['username'])
        if detection_history:
            for detection in detection_history:
                with st.expander(f"{detection['disease_name']} - {detection['detection_date']}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if os.path.exists(detection['image_path']):
                            st.image(detection['image_path'], use_column_width=True)
                    with col2:
                        st.markdown(f"**{t('confidence')}:** {detection['confidence']}%")
                        st.markdown(f"**{t('date')}:** {detection['detection_date']}")
        else:
            st.info(t('no_disease_records'))
    
    with side_col:
        # Quick Stats
        st.subheader(t('farm_stats'))
        if crop_history:
            df = pd.DataFrame(crop_history)
            avg_yield = df['yield_amount'].mean()
            last_crop = df.iloc[0]['crop'] if len(df) > 0 else t('none')
            total_yield = df['yield_amount'].sum()
            
            st.metric(t('avg_yield'), f"{avg_yield:.1f} {t('tons')}")
            st.metric(t('last_crop'), last_crop)
            st.metric(t('total_yield'), f"{total_yield:.1f} {t('tons')}")
        else:
            st.info(t('no_data'))
        
        # Add Crop Form
        with st.expander(t('add_crop')):
            with st.form("add_crop_form"):
                crop_name = st.text_input(t('crop_name'))
                col1, col2 = st.columns(2)
                with col1:
                    planting_date = st.date_input(t('planting_date'))
                with col2:
                    harvest_date = st.date_input(t('harvest_date'))
                yield_amount = st.number_input(t('yield_amount'), min_value=0.0, step=0.1)
                notes = st.text_area(t('notes'))
                
                if st.form_submit_button(t('add_record')):
                    crop_data = {
                        "crop": crop_name,
                        "planted": str(planting_date),
                        "harvested": str(harvest_date),
                        "yield": yield_amount,
                        "notes": notes
                    }
                    success, message = add_crop_record(st.session_state.user['username'], crop_data)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

def show_weather_page():
    """Render weather forecast page"""
    st.header(t('weather_title'))
    
    lottie_weather = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_nKwET0.json")
    if lottie_weather:
        st_lottie(lottie_weather, height=200, key="weather-anim")
    
    location = st.text_input(t('enter_location'), value=st.session_state.user.get('location', ''))
    
    if location:
        with st.spinner(t('fetching_weather')):
            forecast = get_weather_forecast(location)
            
            if forecast:
                # Current weather
                st.markdown(f"""
                <div style="border-radius: 10px; padding: 20px; margin-bottom: 20px; 
                            background: rgba(255,255,255,0.1);">
                    <h3>{t('current_weather_for')} {forecast['location']}</h3>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 3rem; font-weight: bold;">{forecast['current']['temp']}°C</div>
                        <div>
                            <p>🌧️ {t('precipitation')}: {forecast['current']['precipitation']}%</p>
                            <p>💨 {t('wind')}: {forecast['current']['wind_speed']} km/h</p>
                            <p>☀️ {t('uv_index')}: {forecast['current']['uv_index']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Forecast chart
                st.subheader(t('forecast_7days'))
                forecast_df = pd.DataFrame(forecast['forecast'])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['temp'],
                    name=t('temperature'),
                    line=dict(color='#FFC107', width=4),
                    mode='lines+markers'
                ))
                fig.add_trace(go.Bar(
                    x=forecast_df['date'],
                    y=forecast_df['precipitation'],
                    name=t('precipitation'),
                    marker_color='#2196F3'
                ))
                st.plotly_chart(fig, use_container_width=True)
                
                # Farming recommendations
                st.subheader(t('farming_recommendations'))
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"""
                    <div style="border-radius: 10px; padding: 15px; background: rgba(255,255,255,0.1);">
                        <h4>🌱 {t('planting')}</h4>
                        <p>{t('optimal_time_for')}:</p>
                        <p>• {t('wheat')}</p>
                        <p>• {t('barley')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"""
                    <div style="border-radius: 10px; padding: 15px; background: rgba(255,255,255,0.1);">
                        <h4>💧 {t('irrigation')}</h4>
                        <p>{t('reduce_watering')} 20%</p>
                        <p>{t('expected_rainfall')}: 15mm</p>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"""
                    <div style="border-radius: 10px; padding: 15px; background: rgba(255,255,255,0.1);">
                        <h4>🛡️ {t('protection')}</h4>
                        <p>• {t('cover_plants')}</p>
                        <p>• {t('check_drainage')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(t('weather_fetch_failed'))

def show_about_page():
    """Render about page"""
    st.header(t('about_title'))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; background: rgba(255,255,255,0.1);">
            <h2>{t('mission')}</h2>
            <p>{t('mission_text')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; background: rgba(255,255,255,0.1);">
            <h2>{t('vision')}</h2>
            <p>{t('vision_text')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(t('features_title'))
    
    cols = st.columns(3)
    features = [
        (t('ai_detection'), t('ai_detection_desc')),
        (t('real_time_analysis'), t('real_time_analysis_desc')),
        (t('easy_to_use'), t('easy_to_use_desc'))
    ]
    
    for i, (title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div style="border-radius: 10px; padding: 15px; margin-bottom: 15px; 
                        background: rgba(255,255,255,0.1);">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(t('team'))
    
    for member in t('team_members'):
        st.markdown(f"""
        <div style="border-radius: 10px; padding: 15px; margin-bottom: 15px; 
                    background: rgba(255,255,255,0.1); border-top: 4px solid #FFC107;">
            <h4>{member['name']}</h4>
            <p><strong>{member['role']}</strong></p>
            <p>{member['bio']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_contact_page():
    """Render contact page"""
    st.header(t('contact_title'))
    
    cols = st.columns(2)
    with cols[0]:
        st.subheader(t('get_in_touch'))
        st.write(t('contact_us_message'))
        
        for info in t('contact_info'):
            st.markdown(f"- {info}")
    
    with cols[1]:
        st.subheader(t('send_message'))
        with st.form("contact_form"):
            name = st.text_input(t('your_name'))
            email = st.text_input(t('your_email'))
            subject = st.selectbox(t('subject'), 
                                 [t('general_inquiry'), t('tech_support'), t('feedback')])
            message = st.text_area(t('your_message'), height=150)
            
            if st.form_submit_button(t('send_message_button')):
                st.success(t('thank_you_message'))

# =============================================
# Main Application
# =============================================

def main():
    """Main application function"""
    
    # Initialize database
    init_db()
    
    # Load animations
    if 'lottie_login' not in st.session_state:
        st.session_state.lottie_login = load_lottieurl(
            "https://assets5.lottiefiles.com/packages/lf20_hu9cd9.json"
        )
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'language' not in st.session_state:
        st.session_state.language = "en"
    
    # Authentication check
    if not st.session_state.logged_in:
        if st.session_state.show_register:
            show_register_form()
        else:
            show_login_form()
        return
    
    # Main app layout for authenticated users
    st.set_page_config(
        page_title="AgroAI Advisor",
        layout="wide",
        page_icon="🌱",
        menu_items={
            'Get Help': 'https://example.com/help',
            'Report a bug': "https://example.com/bug",
            'About': "# AgroAI Advisor v4.0"
        }
    )
    
    # Sidebar
    show_sidebar()
    
    # Navigation
    pages = {
        t('home'): show_home_page,
        t('crop_yield'): show_yield_page,
        t('disease_detect'): show_disease_page,
        t('dashboard'): show_dashboard_page,
        t('weather'): show_weather_page,
        t('about'): show_about_page,
        t('contact'): show_contact_page
    }
    
    # Page selection
    selected_page = st.selectbox(
        t('navigate'),
        options=list(pages.keys()),
        label_visibility="collapsed"
    )
    
    # Display the selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()
