# 🌱 Smart Agro Advisor

An AI-powered Streamlit application for **crop yield prediction**, **plant disease detection**, **weather forecasts**, and **farm management**, built for Indian farmers with multilingual support (English, Hindi, Marathi).

---

## 📌 Features

- 🌿 **Crop Yield Prediction** using a trained machine learning model (`yield_model.pkl`)
- 🦠 **Plant Disease Detection** from uploaded or captured leaf images using a deep learning model (`plant_disease_model.h5`)
- 📊 **Crop History Dashboard**
- 🌦️ **Weather Forecast Integration**
- 👤 **User Login, Profile & Admin Access**
- 📝 **Multilingual Support:** English, हिंदी, मराठी
- 🔗 **Lightweight Deployment:** Downloads models & data at runtime from Google Drive

---

## 🚀 Deployment (Render)

### 1. **Prepare the Repo**
Push the following files to GitHub:

📁 streamlit_app.py
📁 disease_detector.py
📁 yield_predictor.py
📁 requirements.txt
📁 user_database.json (optional)


> Exclude heavy models/datasets using `.gitignore`:
notebooks/.h5
notebooks/.pkl
data/
*.zip


### 2. **Google Drive Model Hosting**

| File | Google Drive ID |
|------|------------------|
| `plant_disease_model.h5` | `1S6f-gU6mMo9htxzJhNZmxwV__2SqxATp` |
| `yield_model.pkl`        | `1OTkpN5Yhig9DwHRaX5Luyf1_khkeMGQU` |
| `disease_classes.json`   | `1J-onrbrJKyOfzd13wKHhMk92E5gBS80h` |

> Files are downloaded dynamically via `gdown`.

---

### 3. **requirements.txt**

```txt
streamlit
pandas
numpy
scikit-learn
tensorflow==2.9.3
keras==2.9.0
matplotlib
seaborn
opencv-python
pillow
gdown
joblib
plotly
streamlit-lottie
4. Deploy on Render
Create a new Web Service

Connect your GitHub repo

Set these:

Build command:

nginx
Copy code
pip install -r requirements.txt
Start command:

arduino
Copy code
streamlit run streamlit_app.py
🧠 Tech Stack
Frontend/UI: Streamlit, Plotly, Lottie

ML Models: scikit-learn, TensorFlow, Keras

Data Processing: Pandas, NumPy

Auth: Simple JSON-based user registration/login

📁 Folder Structure (Simplified)
kotlin
Copy code
├── streamlit_app.py
├── disease_detector.py
├── yield_predictor.py
├── requirements.txt
├── user_database.json
├── notebooks/
│   ├── (Downloads .h5 and .pkl here)
├── data/
│   └── (Optionally extracts training images)
📝 Notes
Use gdown to download large files at runtime

Don’t push large models or images to GitHub directly

Works great with free Render tier

👨‍💻 Developed By
Team Smart Agro AI

Vaishnavi Borse – Full Stack Developer

Pranjali Patil – Frontend Developer

Maithili Pawar – Frontend Developer

Yuvraj Rajure – ML Developer

Hardik Sonawane – ML Developer

🔗 License
This project is for educational and social impact purposes. Attribution required for reuse.

---