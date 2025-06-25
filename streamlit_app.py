# Complete AgroAI Advisor App with Admin Panel
import streamlit as st
from PIL import Image
import os
import hashlib
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
import gdown
import zipfile

def download_and_extract_train_images():
    zip_path = "data/train.zip"
    extract_path = "data/train"
    
    if not os.path.exists(extract_path):
        print("Downloading training images...")
        gdown.download("https://drive.google.com/uc?id=1SlFCW7RKvhlmrLtJypKZBZlkFZk8ycp4", zip_path, quiet=False)
        
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("data/")
        print("Extraction complete.")

# =============================================
# Utility Functions 
# =============================================

def predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide):
    """Mock yield prediction function"""
    base_yields = {
        "Rice": 3.5, "Wheat": 2.8, "Maize": 4.2, 
        "Cotton": 1.8, "Soybean": 2.5, "Potato": 20.0
    }
    base = base_yields.get(crop, 3.0)
    
    # Apply multipliers based on conditions
    yield_estimate = base * area
    yield_estimate *= 1 + (rainfall - 800) / 4000  # Rainfall effect
    yield_estimate *= 1 + (fertilizer - 50) / 500  # Fertilizer effect
    yield_estimate *= 1 - (pesticide - 5) / 200    # Pesticide effect
    
    # Add some randomness
    yield_estimate *= random.uniform(0.95, 1.05)
    
    return max(1.0, yield_estimate)  # Ensure minimum yield

def predict_disease(image):
    """Mock disease detection function"""
    diseases = [
        ("Healthy", 0.95),
        ("Powdery Mildew", 0.85),
        ("Leaf Rust", 0.78),
        ("Bacterial Blight", 0.72),
        ("Early Blight", 0.68)
    ]
    # Select random disease (weighted toward healthy)
    return random.choices(
        diseases,
        weights=[50, 15, 15, 10, 10]
    )[0]

def get_weather_forecast(location):
    """Mock weather forecast function"""
    days = 7
    base_temp = random.uniform(15, 30)
    
    return {
        "temp": round(base_temp, 1),
        "humidity": random.randint(40, 80),
        "wind_speed": random.uniform(5, 25),
        "time": [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)],
        "temperature": [round(base_temp + random.uniform(-5, 5), 1) for _ in range(days)],
        "precipitation": [random.randint(0, 30) for _ in range(days)],
        "uv": random.choice(["Low", "Moderate", "High"])
    }

# =============================================
# User Management Functions
# =============================================

def is_admin():
    """Check if current user is admin"""
    return st.session_state.get('user', {}).get('role') == 'admin'

def get_all_users():
    """Get all registered users (admin only)"""
    if not is_admin():
        return {}
    return load_users()

def delete_user(username):
    """Delete a user (admin only)"""
    if not is_admin():
        return False
        
    users = load_users()
    if username in users:
        del users[username]
        with open("user_database.json", "w") as f:
            json.dump(users, f)
        return True
    return False

# =============================================
# App Configuration
# =============================================

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    if 'language' not in st.session_state:
        st.session_state.language = "en"
    if 'crop_data' not in st.session_state:
        st.session_state.crop_data = []
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

    # Initialize with sample crop data if empty
    if len(st.session_state.crop_data) == 0:
        st.session_state.crop_data = [
            {"Crop": "Wheat", "Planted": "2023-10-01", "Harvested": "2024-03-15", "Yield": 4.2, "Notes": "Good harvest"},
            {"Crop": "Corn", "Planted": "2023-06-15", "Harvested": "2023-09-30", "Yield": 5.8, "Notes": "Affected by drought"},
            {"Crop": "Soybean", "Planted": "2023-05-01", "Harvested": "2023-08-20", "Yield": 3.5, "Notes": "Standard yield"}
        ]

# Call initialization function
init_session_state()

# Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_agro = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_vybwn7df.json")
lottie_weather = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_nKwET0.json")
lottie_disease = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ygiuluqn.json")
lottie_yield = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5tkzkblw.json")
lottie_login = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_hu9cd9.json")

# User database functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_db():
    if not Path("user_database.json").exists():
        with open("user_database.json", "w") as f:
            json.dump({
                "admin": {
                    "password": hash_password("admin123"),
                    "name": "Admin User",
                    "role": "admin",
                    "email": "admin@smartagro.com",
                    "farm_size": "10",
                    "location": "Pune, India"
                }
            }, f)

def load_users():
    try:
        with open("user_database.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def register_user(username, password, name, email, farm_size="5", location="Unknown", role="user"):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    if role == "admin" and not is_admin():
        return False, "Only admins can create admin accounts"
    
    users[username] = {
        "password": hash_password(password),
        "name": name,
        "email": email,
        "role": role,
        "farm_size": farm_size,
        "location": location
    }
    
    with open("user_database.json", "w") as f:
        json.dump(users, f)
    return True, f"User {username} registered as {role}"

# Translation system
languages = {
    "English": "en", 
    "हिंदी (Hindi)": "hi", 
    "मराठी (Marathi)": "mr"
}

text = {
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
        "team_members": [
            {"name": "Vaishnavi Borse", "role": "Full Stack Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Pranjali Patil", "role": "Frontend Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Maithili Pawar", "role": "Frontend Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Yuvraj Rajure", "role": "ML Developer", "bio": "B.Tech in Computer Science"},
            {"name": "Hardik Sonawane", "role": "ML Developer", "bio": "B.Tech in Computer Science"}
        ],
        "admin_panel": "🔐 Admin Panel",
        "admin_access_required": "⛔ Admin access required",
        "registered_users": "Registered Users",
        "user_actions": "User Actions",
        "view_details": "View Details",
        "delete_user": "Delete User",
        "add_new_admin": "Add New Admin",
        "create_admin": "Create Admin"
    },
    "hi": {
        # ... (keep all existing Hindi translations)
        "admin_panel": "🔐 एडमिन पैनल",
        "admin_access_required": "⛔ व्यवस्थापक पहुँच आवश्यक",
        "registered_users": "पंजीकृत उपयोगकर्ता",
        "user_actions": "उपयोगकर्ता क्रियाएँ",
        "view_details": "विवरण देखें",
        "delete_user": "उपयोगकर्ता हटाएं",
        "add_new_admin": "नया व्यवस्थापक जोड़ें",
        "create_admin": "व्यवस्थापक बनाएं"
    },
    "mr": {
        # ... (keep all existing Marathi translations)
        "admin_panel": "🔐 प्रशासक पॅनेल",
        "admin_access_required": "⛔ प्रशासक प्रवेश आवश्यक",
        "registered_users": "नोंदणीकृत वापरकर्ते",
        "user_actions": "वापरकर्ता क्रिया",
        "view_details": "तपशील पहा",
        "delete_user": "वापरकर्ता हटवा",
        "add_new_admin": "नवीन प्रशासक जोडा",
        "create_admin": "प्रशासक तयार करा"
    }
}

def t(key, default=None):
    """Get translation for current language"""
    return text.get(st.session_state.language, {}).get(key, default or key)

# =============================================
# Authentication System
# =============================================

def show_login():
    st.markdown("""
    <div style="max-width: 400px; margin: 0 auto; padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.1);">
        <h2 style="text-align: center;">Login</h2>
    """, unsafe_allow_html=True)
    
    if lottie_login:
        st_lottie(lottie_login, height=150, key="login-anim")
    
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("login_button")):
            users = load_users()
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user = users[username]
                st.success(t("welcome"))
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error(t("invalid"))
    with col2:
        if st.button(t("need_account")):
            st.session_state.show_register = True
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_register():
    st.markdown("""
    <div style="max-width: 400px; margin: 0 auto; padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.1);">
        <h2 style="text-align: center;">Register</h2>
    """, unsafe_allow_html=True)
    
    if lottie_login:
        st_lottie(lottie_login, height=150, key="register-anim")
    
    username = st.text_input(t("username"))
    name = st.text_input(t("name"))
    email = st.text_input(t("email"))
    farm_size = st.number_input(t("farm_size"), min_value=0.1, value=5.0, step=0.5)
    location = st.text_input(t("location"))
    password = st.text_input(t("password"), type="password")
    confirm_password = st.text_input(t("confirm_password"), type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("register_button")):
            if password != confirm_password:
                st.error(t("password_mismatch"))
            elif "@" not in email or "." not in email:
                st.error(t("invalid_email"))
            else:
                success, message = register_user(username, password, name, email, farm_size, location)
                if success:
                    st.success(t("reg_success"))
                    time.sleep(1)
                    st.session_state.show_register = False
                    st.experimental_rerun()
                else:
                    st.error(message)
    with col2:
        if st.button(t("have_account")):
            st.session_state.show_register = False
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_admin_panel():
    st.header(t("admin_panel"))
    
    if not is_admin():
        st.warning(t("admin_access_required"))
        st.stop()
    
    st.subheader(t("registered_users"))
    users = get_all_users()
    
    if not users:
        st.info("No users registered yet")
    else:
        # Display users in a nice table
        user_data = []
        for username, details in users.items():
            user_data.append({
                "Username": username,
                "Name": details['name'],
                "Email": details['email'],
                "Role": details.get('role', 'user'),
                "Farm Size": details.get('farm_size', 'N/A'),
                "Location": details.get('location', 'N/A')
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        # User management actions
        st.subheader(t("user_actions"))
        selected_user = st.selectbox("Select user", list(users.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("view_details")):
                st.json(users[selected_user])
        
        with col2:
            if st.button(t("delete_user")):
                if delete_user(selected_user):
                    st.success(f"User {selected_user} deleted")
                    st.experimental_rerun()
                else:
                    st.error("Deletion failed")
        
        # Create new admin
        st.subheader(t("add_new_admin"))
        with st.form("new_admin_form"):
            new_username = st.text_input(t("username"))
            new_password = st.text_input("Password", type="password")
            new_name = st.text_input(t("name"))
            new_email = st.text_input(t("email"))
            
            if st.form_submit_button(t("create_admin")):
                success, message = register_user(
                    new_username,
                    new_password,
                    new_name,
                    new_email,
                    role="admin"
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Initialize user database
init_user_db()

# =============================================
# Main App Layout
# =============================================

# Page config
st.set_page_config(
    page_title="AgroAI Advisor",
    layout="wide",
    page_icon="🌱",
    menu_items={
        'Get Help': 'https://example.com/help',
        'Report a bug': "https://example.com/bug",
        'About': "# AgroAI Advisor v3.0"
    }
)

# CSS styling
st.markdown("""
<style>
/* Main styling */
:root {
    --primary: #4CAF50;
    --primary-dark: #2E7D32;
    --primary-light: #81C784;
    --secondary: #FFC107;
    --accent: #FF5722;
    --bg-dark: #121212;
    --bg-card: #1E1E1E;
    --text-light: #FFFFFF;
}

body {
    background-color: var(--bg-dark);
    color: var(--text-light);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Cards */
.card {
    background-color: var(--bg-card);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    border-left: 4px solid var(--primary);
}

/* Buttons */
.stButton>button {
    background-color: var(--primary);
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    border: none;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
}

/* Inputs */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: var(--bg-card);
    color: var(--text-light);
    border-radius: 8px;
}

/* Navigation */
.navbar {
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background: linear-gradient(90deg, var(--primary-dark), var(--primary));
    border-radius: 12px;
    margin-bottom: 1.5rem;
}

.navbar button {
    background: transparent;
    border: none;
    color: white;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.navbar button:hover {
    background: rgba(255,255,255,0.15);
}

/* Team cards */
.team-card {
    background-color: var(--bg-card);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border-top: 4px solid var(--secondary);
}

.team-card h4 {
    color: var(--secondary);
    margin-bottom: 0.5rem;
}

.team-card p {
    margin: 0.2rem 0;
}

/* Admin panel specific */
.admin-table {
    width: 100%;
    border-collapse: collapse;
}

.admin-table th, .admin-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #444;
}

.admin-table tr:hover {
    background-color: rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)

# Authentication check
if not st.session_state.logged_in:
    if st.session_state.show_register:
        show_register()
    else:
        show_login()
    st.stop()

# =============================================
# Application Pages
# =============================================

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div class="card">
        <h3>{t('profile')}</h3>
        <p><strong>{st.session_state.user['name']}</strong></p>
        <p>📍 {st.session_state.user.get('location', 'Unknown')}</p>
        <p>🌱 {st.session_state.user.get('farm_size', '5')} {t('area')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(t("logout")):
        st.session_state.clear()
        st.experimental_rerun()
    
    selected_lang = st.selectbox(
        "🌐 Language",
        options=list(languages.keys()),
        index=list(languages.values()).index(st.session_state.language)
    )
    st.session_state.language = languages[selected_lang]

# Navigation
nav_items = [
    ("🏠 Home", "Home"),
    ("🌿 Crop Yield", "Crop Yield"),
    ("🦠 Disease Detection", "Disease Detection"),
    ("📊 Dashboard", "Dashboard"),
    ("🌦️ Weather", "Weather")
]

# Only show admin panel to admins
if is_admin():
    nav_items.append((t("admin_panel"), "Admin"))

nav_items.extend([
    ("📖 About", "About"),
    ("📬 Contact", "Contact")
])

st.markdown("<div class='navbar'>", unsafe_allow_html=True)
cols = st.columns(len(nav_items))
for i, (icon, page) in enumerate(nav_items):
    with cols[i]:
        if st.button(icon, key=f"nav_{page}"):
            st.session_state.page = page
st.markdown("</div>", unsafe_allow_html=True)

# Page routing
if st.session_state.page == "Home":
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 0; background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(46, 125, 50, 0.2)); border-radius: 16px;">
        <h1>{t('hero_title')}</h1>
        <p style="font-size: 1.5rem;">{t('hero_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if lottie_agro:
        st_lottie(lottie_agro, height=300, key="home-anim")
    
    st.markdown("---")
    st.header(t("features_title"))
    
    cols = st.columns(2)
    features = [
        ("🌾 Crop Yield Prediction", "Predict harvest amounts based on environmental factors"),
        ("🦠 Disease Detection", "Identify plant diseases from leaf images"),
        ("📊 Analytics Dashboard", "View historical data and trends"),
        ("🌦️ Weather Integration", "Get localized weather forecasts")
    ]
    
    for i, (title, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Crop Yield":
    st.header(t("yield_form_title"))
    
    if lottie_yield:
        st_lottie(lottie_yield, height=200, key="yield-anim")
    
    with st.form("yield_form"):
        col1, col2 = st.columns(2)
        with col1:
            crop = st.selectbox(t("crop"), ["Rice", "Wheat", "Maize", "Cotton", "Soybean", "Potato"])
            season = st.selectbox(t("season"), ["Kharif", "Rabi", "Zaid", "Summer", "Winter"])
            state = st.selectbox(t("state"), ["Maharashtra", "Punjab", "Tamil Nadu", "Uttar Pradesh", "Karnataka", "Gujarat"])
        with col2:
            area = st.number_input(t("area"), min_value=0.1, value=float(st.session_state.user.get('farm_size', 5.0)), step=0.1)
            rainfall = st.slider(t("rainfall"), min_value=0, max_value=2000, value=800)
            fertilizer = st.slider(t("fertilizer"), min_value=0, max_value=200, value=50)
            pesticide = st.slider(t("pesticide"), min_value=0, max_value=50, value=5)
        
        if st.form_submit_button(t("predict")):
            with st.spinner("Predicting yield..."):
                time.sleep(1)  # Simulate processing
                result = predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide)
                st.success(f"Predicted Yield: {result:.2f} tons/hectare")
                
                # Show comparison chart
                data = pd.DataFrame({
                    'Metric': ['Your Prediction', 'Region Average', 'Best in Region'],
                    'Yield': [result, result*0.8, result*1.3]
                })
                
                fig = px.bar(data, x='Metric', y='Yield', color='Metric',
                            color_discrete_sequence=['#4CAF50', '#FFC107', '#2E7D32'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Yield tips
                with st.expander(t("yield_tips_title")):
                    for tip in t("yield_tips"):
                        st.markdown(f"✅ {tip}")

elif st.session_state.page == "Disease Detection":
    st.header(t("disease_form_title"))
    
    if lottie_disease:
        st_lottie(lottie_disease, height=200, key="disease-anim")
    
    tab1, tab2 = st.tabs([t("upload_leaf"), t("capture_button")])
    
    with tab1:
        uploaded_file = st.file_uploader(t("upload_leaf"), type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")
            
            if st.button(t("analyze")):
                with st.spinner("Analyzing..."):
                    time.sleep(2)  # Simulate processing
                    disease, confidence = predict_disease(image)
                    st.success(f"Detected: {disease} ({(confidence*100):.1f}% confidence)")
                    
                    with st.expander(t("treatment_title")):
                        for advice in t("treatment_advice"):
                            st.markdown(f"🔹 {advice}")
    
    with tab2:
        img_file_buffer = st.camera_input(t("camera_instructions"))
        if img_file_buffer:
            image = Image.open(img_file_buffer)
            st.image(image, caption="Captured Image")
            
            if st.button(t("analyze_button")):
                with st.spinner("Analyzing..."):
                    time.sleep(2)  # Simulate processing
                    disease, confidence = predict_disease(image)
                    st.success(f"Detected: {disease} ({(confidence*100):.1f}% confidence)")
                    
                    with st.expander(t("treatment_title")):
                        for advice in t("treatment_advice"):
                            st.markdown(f"🔹 {advice}")

elif st.session_state.page == "Dashboard":
    st.header(t("dashboard_title"))
    
    # Main layout
    main_col, side_col = st.columns([3, 1])
    
    with main_col:
        # Yield Trends Chart
        st.subheader("Yield Trends")
        if len(st.session_state.crop_data) > 0:
            df = pd.DataFrame(st.session_state.crop_data)
            df['Planted'] = pd.to_datetime(df['Planted'])
            df = df.sort_values('Planted')
            
            fig = px.line(
                df,
                x='Planted',
                y='Yield',
                color='Crop',
                markers=True,
                title='Crop Yield Over Time'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t("no_records"))
        
        # Crop History Table
        st.subheader(t("crop_history"))
        if len(st.session_state.crop_data) > 0:
           df = pd.DataFrame(st.session_state.crop_data)
           df.index = [''] * len(df)  # Hide index by making it empty
           st.dataframe(
                df,
                use_container_width=True
           )
        else:
            st.info(t("no_records"))
    
    with side_col:
        # Quick Stats
        st.subheader("Farm Stats")
        if len(st.session_state.crop_data) > 0:
            df = pd.DataFrame(st.session_state.crop_data)
            avg_yield = df['Yield'].mean()
            last_crop = df.iloc[-1]['Crop']
            total_yield = df['Yield'].sum()
            
            st.metric("Average Yield", f"{avg_yield:.1f} tons")
            st.metric("Last Crop", last_crop)
            st.metric("Total Yield", f"{total_yield:.1f} tons")
        else:
            st.info("No data available")
        
        # Add Crop Form
        with st.expander(t("add_crop")):
            with st.form("add_crop_form"):
                crop_name = st.text_input(t("crop_name"))
                col1, col2 = st.columns(2)
                with col1:
                    planting_date = st.date_input(t("planting_date"))
                with col2:
                    harvest_date = st.date_input(t("harvest_date"))
                yield_amount = st.number_input(t("yield_amount"), min_value=0.0, step=0.1)
                notes = st.text_area(t("notes"))
                
                if st.form_submit_button(t("add_record")):
                    new_record = {
                        "Crop": crop_name,
                        "Planted": str(planting_date),
                        "Harvested": str(harvest_date),
                        "Yield": yield_amount,
                        "Notes": notes
                    }
                    st.session_state.crop_data.append(new_record)
                    st.success("Record added successfully!")
                    st.experimental_rerun()

elif st.session_state.page == "Weather":
    st.header(t("weather_title"))
    
    if lottie_weather:
        st_lottie(lottie_weather, height=200, key="weather-anim")
    
    location = st.text_input("Enter location", value=st.session_state.user.get('location', ''))
    
    if location:
        with st.spinner("Fetching weather data..."):
            time.sleep(1)  # Simulate API call
            forecast = get_weather_forecast(location)
            
            # Current weather
            st.markdown(f"""
            <div class="card">
                <h3>Current Weather for {location}</h3>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 3rem; font-weight: bold;">{forecast['temp']}°C</div>
                    <div>
                        <p>🌧️ Precipitation: {forecast.get('precip', '0')}%</p>
                        <p>💨 Wind: {forecast['wind_speed']} km/h</p>
                        <p>☀️ UV Index: {forecast.get('uv', 'Moderate')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Forecast chart
            st.subheader("7-Day Forecast")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast['time'],
                y=forecast['temperature'],
                name='Temperature',
                line=dict(color='#FFC107', width=4),
                mode='lines+markers'
            ))
            fig.add_trace(go.Bar(
                x=forecast['time'],
                y=forecast['precipitation'],
                name='Precipitation',
                marker_color='#2196F3'
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Farming recommendations
            st.subheader("Farming Recommendations")
            cols = st.columns(3)
            with cols[0]:
                st.markdown("""
                <div class="card">
                    <h4>🌱 Planting</h4>
                    <p>Optimal time for:</p>
                    <p>• Wheat</p>
                    <p>• Barley</p>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown("""
                <div class="card">
                    <h4>💧 Irrigation</h4>
                    <p>Reduce watering by 20%</p>
                    <p>Expected rainfall: 15mm</p>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown("""
                <div class="card">
                    <h4>🛡️ Protection</h4>
                    <p>• Cover young plants</p>
                    <p>• Check drainage</p>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.page == "Admin":
    show_admin_panel()

elif st.session_state.page == "About":
    st.header(t("about_title"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h2>{t('mission')}</h2>
            <p>{t('mission_text')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <h2>{t('vision')}</h2>
            <p>{t('vision_text')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(t("features_title"))
    
    cols = st.columns(3)
    features = [
        ("AI-Powered Detection", "Advanced algorithms for accurate results"),
        ("Real-Time Analysis", "Instant feedback on plant health"),
        ("Easy to Use", "Simple interface for all users")
    ]
    
    for i, (title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader(t("team"))
    
    for member in t("team_members"):
        st.markdown(f"""
        <div class="team-card">
            <h4>{member['name']}</h4>
            <p><strong>{member['role']}</strong></p>
            <p>{member['bio']}</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Contact":
    st.header(t("contact_title"))
    
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Get in Touch")
        st.write("We'd love to hear from you!")
        
        for info in t("contact_info"):
            st.markdown(f"- {info}")
    
    with cols[1]:
        st.subheader("Send Us a Message")
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feedback"])
            message = st.text_area("Your Message", height=150)
            
            if st.form_submit_button("Send Message"):
                st.success("Thank you for your message! We'll respond within 24 hours.")

# Footer
st.markdown("""
<footer style="margin-top: 4rem; padding: 2rem 0; text-align: center;">
    <p>AgroAI Advisor © 2025 | All Rights Reserved</p>
</footer>
""", unsafe_allow_html=True)
