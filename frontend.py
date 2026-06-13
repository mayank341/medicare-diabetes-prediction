import streamlit as st
import requests
import sqlite3
import hashlib
from datetime import datetime, date

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="MediCare+ | Diabetes Risk Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000/diabetes_prediction"
DB_PATH = "medicare.db"

# ----------------------------------------------------------------------------
# DATABASE SETUP
# ----------------------------------------------------------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            password_hash TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            clinic_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            reason TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(name, email, password):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
                  (email, name, hash_password(password)))
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()

def verify_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, password_hash FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    if row is None:
        return False, None
    name, stored_hash = row
    if stored_hash == hash_password(password):
        return True, name
    return False, None

def save_appointment(user_email, clinic_name, appt_date, appt_time, reason):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO appointments (user_email, clinic_name, appointment_date, appointment_time, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_email, clinic_name, str(appt_date), appt_time, reason, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_appointments(user_email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT clinic_name, appointment_date, appointment_time, reason, created_at
        FROM appointments WHERE user_email = ? ORDER BY appointment_date, appointment_time
    """, (user_email,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ----------------------------------------------------------------------------
# CLINIC DATA — 15 NCR Hospitals (Noida, Delhi, Gurgaon)
# ----------------------------------------------------------------------------
CLINICS = [
    {"name": "Fortis Hospital, Noida", "img": "https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?w=400",
     "distance": "2.1 km away", "address": "B-22, Sector 62, Noida, UP", "phone": "+91-120-712-2222"},
    {"name": "Max Super Speciality Hospital, Vaishali", "img": "https://images.unsplash.com/photo-1519494026892-80bbd3d3076a?w=400",
     "distance": "3.4 km away", "address": "W-3, Sector 1, Vaishali, Ghaziabad", "phone": "+91-120-471-2000"},
    {"name": "Yashoda Super Speciality Hospital, Ghaziabad", "img": "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400",
     "distance": "1.8 km away", "address": "Nehru Nagar, Ghaziabad, UP", "phone": "+91-120-471-2000"},
    {"name": "Apollo Hospital, Sarita Vihar, Delhi", "img": "https://images.unsplash.com/photo-1551076805-e1869033e561?w=400",
     "distance": "12.5 km away", "address": "Mathura Road, Sarita Vihar, New Delhi", "phone": "+91-11-7179-1090"},
    {"name": "AIIMS, New Delhi", "img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400",
     "distance": "15.2 km away", "address": "Ansari Nagar, New Delhi", "phone": "+91-11-2658-8500"},
    {"name": "Sir Ganga Ram Hospital, Delhi", "img": "https://images.unsplash.com/photo-1551601651-2a8555f1a136?w=400",
     "distance": "16.8 km away", "address": "Rajinder Nagar, New Delhi", "phone": "+91-11-2575-0000"},
    {"name": "Medanta - The Medicity, Gurgaon", "img": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=400",
     "distance": "32.0 km away", "address": "Sector 38, Gurugram, Haryana", "phone": "+91-124-441-4141"},
    {"name": "Fortis Memorial Research Institute, Gurgaon", "img": "https://images.unsplash.com/photo-1504439468489-c8920d796a29?w=400",
     "distance": "33.5 km away", "address": "Sector 44, Gurugram, Haryana", "phone": "+91-124-496-2200"},
    {"name": "Artemis Hospital, Gurgaon", "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400",
     "distance": "34.1 km away", "address": "Sector 51, Gurugram, Haryana", "phone": "+91-124-451-1111"},
    {"name": "Kailash Hospital, Noida", "img": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400",
     "distance": "4.0 km away", "address": "Sector 27, Noida, UP", "phone": "+91-120-258-1112"},
    {"name": "Metro Hospital, Noida", "img": "https://images.unsplash.com/photo-1666214280391-8ff5bd3c0bf0?w=400",
     "distance": "3.7 km away", "address": "Sector 12, Noida, UP", "phone": "+91-120-456-6666"},
    {"name": "Jaypee Hospital, Noida", "img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=400",
     "distance": "6.2 km away", "address": "Sector 128, Noida, UP", "phone": "+91-120-714-1414"},
    {"name": "BLK-Max Super Speciality Hospital, Delhi", "img": "https://images.unsplash.com/photo-1551884170-09fb70a3a2ed?w=400",
     "distance": "18.4 km away", "address": "Pusa Road, Rajinder Nagar, New Delhi", "phone": "+91-11-3040-3040"},
    {"name": "Indraprastha Apollo Hospital, Delhi", "img": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=400",
     "distance": "13.9 km away", "address": "Sarita Vihar, Delhi Mathura Road, New Delhi", "phone": "+91-11-2692-5858"},
    {"name": "Columbia Asia Hospital, Gurgaon", "img": "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400",
     "distance": "35.0 km away", "address": "Palam Vihar, Gurugram, Haryana", "phone": "+91-124-398-4444"},
]

# ----------------------------------------------------------------------------
# AUTHENTICATION (Clerk-style login/signup using local SQLite)
# ----------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

def login_signup_ui():
    st.markdown("""
    <div class="mantra-banner">
        <span class="chakra">☸️</span>
        <div class="mantra-text">ॐ सर्वे भवन्तु सुखिनः 🙏</div>
    </div>
    <div class="hero">
        <h1>🩺 MediCare+ Diabetes Risk Center</h1>
        <p>AI-Powered Health Screening • Trusted by Clinics • Instant Results</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-card" style="max-width:450px; margin:auto;">', unsafe_allow_html=True)
    st.subheader("🔐 Welcome — Please Sign In or Sign Up")

    tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])

    with tab_login:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In", use_container_width=True, type="primary"):
            ok, name = verify_user(login_email.strip().lower(), login_password)
            if ok:
                st.session_state.user = {"email": login_email.strip().lower(), "name": name}
                st.success(f"Welcome back, {name}! 🎉")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab_signup:
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_password2 = st.text_input("Confirm Password", type="password", key="signup_password2")
        if st.button("Create Account", use_container_width=True, type="primary"):
            if not signup_name or not signup_email or not signup_password:
                st.error("Please fill all fields.")
            elif signup_password != signup_password2:
                st.error("Passwords do not match.")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                ok, msg = create_user(signup_name.strip(), signup_email.strip().lower(), signup_password)
                if ok:
                    st.success(msg + " Please sign in now.")
                else:
                    st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# THEME TOGGLE (Light / Dark)
# ----------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    theme_choice = st.toggle("🌿 Calm Mode", value=(st.session_state.theme == "dark"))
    st.session_state.theme = "dark" if theme_choice else "light"

    st.markdown("---")
    if st.session_state.user:
        st.markdown(f"### 👤 {st.session_state.user['name']}")
        st.caption(st.session_state.user['email'])
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        st.markdown("---")

    st.markdown("### 🏥 About MediCare+")
    st.info("This tool gives an AI-based estimate of diabetes risk. "
            "It is **not** a substitute for professional medical advice.")
    st.markdown("---")
    st.markdown("### 📞 Emergency Helpline")
    st.success("**Toll Free:** 1800-MEDI-CARE")

# ----------------------------------------------------------------------------
# THEME COLORS
# ----------------------------------------------------------------------------
if st.session_state.theme == "dark":
    # "Calm" mode - softer blue-green, still readable
    bg_color = "#102a2f"
    card_bg = "#1c3b3f"
    text_color = "#e6f7f5"
    accent = "#22c3a6"        # green
    secondary_accent = "#0ea5e9"  # blue
else:
    # "Fresh" mode - hospital blue-green on white
    bg_color = "#f0fbfa"
    card_bg = "#ffffff"
    text_color = "#0f3d3e"
    accent = "#16a34a"        # green
    secondary_accent = "#0ea5e9"  # blue

# ----------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(135deg, {bg_color} 0%, {bg_color} 100%);
    color: {text_color};
}}

@keyframes heroGradientFlow {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.hero {{
    background: linear-gradient(120deg, #16a34a, #0ea5e9, #14b8a6, #22c3a6);
    background-size: 300% 300%;
    animation: heroGradientFlow 12s ease infinite;
    padding: 48px;
    border-radius: 22px;
    text-align: center;
    color: white;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(22,163,74,0.15);
}}
.hero h1 {{
    font-size: 44px;
    margin-bottom: 6px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.15);
}}
.hero p {{ font-size: 18px; opacity: 0.95; }}

.section-card {{
    background-color: {card_bg};
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}}

.metric-box {{
    background-color: {card_bg};
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}}

.result-high {{
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border-left: 8px solid #dc2626;
    padding: 25px;
    border-radius: 16px;
    color: #7f1d1d;
}}
.result-low {{
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border-left: 8px solid #16a34a;
    padding: 25px;
    border-radius: 16px;
    color: #14532d;
}}

.do-box {{
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border-radius: 14px;
    padding: 18px;
    color: #065f46;
}}
.diet-eat {{
    background: linear-gradient(135deg, #e0f2fe, #bae6fd);
    border-radius: 14px;
    padding: 18px;
    color: #0c4a6e;
}}
.diet-avoid {{
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-radius: 14px;
    padding: 18px;
    color: #78350f;
}}

.clinic-card {{
    background-color: {card_bg};
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    text-align: center;
    padding-bottom: 15px;
    transition: transform 0.2s ease;
    margin-bottom: 15px;
}}
.clinic-card:hover {{ transform: translateY(-5px); }}
.clinic-card img {{ width: 100%; height: 140px; object-fit: cover; }}
.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background-color: {accent};
    color: white;
    font-size: 12px;
    font-weight: 600;
    margin-top: 5px;
}}
/* FIX: form labels, widget text - force theme text color */
label, .stMarkdown, .stText, p, span, div[data-testid="stWidgetLabel"] label {{
    color: {text_color} !important;
}}

/* Number input / text input box text */
input, textarea, select {{
    color: {text_color} !important;
    background-color: {card_bg} !important;
}}

/* Tabs */
button[data-baseweb="tab"] {{
    color: {text_color} !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {accent} !important;
    border-bottom-color: {accent} !important;
}}

/* Override red focus/highlight colors -> blue accent */
*:focus {{
    box-shadow: 0 0 0 1px {accent} !important;
    border-color: {accent} !important;
}}
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="select"]:focus-within {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 1px {accent} !important;
}}

button[kind="secondary"] {{
    color: {accent} !important;
}}

/* SIDEBAR FIXES */
section[data-testid="stSidebar"] {{
    background-color: {card_bg} !important;
    border-right: 1px solid {accent}33;
}}
section[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}
section[data-testid="stSidebar"] .stAlert {{
    color: #0f3d3e !important;
}}

/* NAV TAB HOVER -> GREEN */
button[data-baseweb="tab"]:hover {{
    color: #16a34a !important;
    background-color: #16a34a1a !important;
    border-radius: 8px 8px 0 0;
}}
/* Remove default dark top header bar */
header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
}}
.stApp {{
    margin-top: -2.5rem;
}}

/* Primary button (Analyze) -> Green */
button[kind="primary"] {{
    background-color: #16a34a !important;
    border-color: #16a34a !important;
    color: white !important;
}}
button[kind="primary"]:hover {{
    background-color: #15803d !important;
    border-color: #15803d !important;
}}
button[kind="primary"]:active,
button[kind="primary"]:focus {{
    background-color: #16a34a !important;
    border-color: #16a34a !important;
    color: white !important;
}}

/* Toggle -> Blue */
[data-testid="stToggle"] [role="switch"][aria-checked="true"] {{
    background-color: #0ea5e9 !important;
}}
[data-testid="stToggle"] [role="switch"] {{
    background-color: #93c5fd !important;
}}

/* Mantra / Chakra header */
.mantra-banner {{
    text-align: center;
    padding: 14px 10px 6px 10px;
}}
.mantra-banner .chakra {{
    font-size: 34px;
    animation: spinChakra 10s linear infinite;
    display: inline-block;
    filter: drop-shadow(0 0 6px rgba(14,165,233,0.5));
}}
.mantra-banner .mantra-text {{
    color: #0ea5e9;
    font-weight: 600;
    font-size: 18px;
    margin-top: 4px;
    letter-spacing: 0.5px;
}}
@keyframes spinChakra {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

/* Footer credit */
.made-by {{
    text-align: center;
    color: #0ea5e9;
    font-weight: 600;
    font-size: 15px;
    padding: 10px 0;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# AUTH GATE
# ----------------------------------------------------------------------------
if st.session_state.user is None:
    login_signup_ui()
    st.stop()

# ----------------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------------
st.markdown("""
<div class="mantra-banner">
    <span class="chakra">☸️</span>
    <div class="mantra-text">ॐ सर्वे भवन्तु सुखिनः 🙏</div>
</div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div class="hero">
    <h1>🩺 MediCare+ Diabetes Risk Center</h1>
    <p>AI-Powered Health Screening • Trusted by Clinics • Instant Results</p>
    <p style="font-size:14px;">Logged in as <b>{st.session_state.user['name']}</b> ({st.session_state.user['email']})</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# NAV BAR
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Risk Assessment", "🏥 Nearby Clinics", "📅 My Appointments", "ℹ️ About"])

# ============================================================================
# TAB 1: RISK ASSESSMENT
# ============================================================================
with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📋 Patient Health Information")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        bmi = st.number_input("BMI", min_value=0.0, max_value=100.0, value=24.0, step=0.1)
    with col2:
        glucose = st.number_input("Glucose (mg/dL)", min_value=0, max_value=300, value=100)
        dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, value=0.4, step=0.01)
    with col3:
        bp = st.number_input("Blood Pressure (mmHg)", min_value=0, max_value=200, value=70)
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
    with col4:
        skin = st.number_input("Skin Thickness (mm)", min_value=0, max_value=100, value=20)
        insulin = st.number_input("Insulin (mu U/ml)", min_value=0, max_value=1000, value=80)

    st.markdown("</div>", unsafe_allow_html=True)

    predict_btn = st.button("🔍 Analyze My Health Risk", use_container_width=True, type="primary")

    if predict_btn:
        payload = {
            "Pregnancies": int(pregnancies), "Glucose": int(glucose), "BloodPressure": int(bp),
            "SkinThickness": int(skin), "Insulin": int(insulin), "BMI": float(bmi),
            "DiabetesPedigreeFunction": float(dpf), "Age": int(age)
        }
        try:
            with st.spinner("Analyzing your health data..."):
                response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code != 200:
                st.error(f"⚠️ API Error ({response.status_code}): {response.text}")
            else:
                result = response.json()
                prediction = result.get("prediction", "Unknown")
                risk_level = result.get("risk_level", "N/A")

                st.markdown("## 📊 Your Result")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-box"><h4>Prediction</h4><h2>{prediction}</h2></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-box"><h4>Risk Level</h4><h2>{risk_level}</h2></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-box"><h4>BMI</h4><h2>{bmi}</h2></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if prediction == "Diabetic":
                    st.markdown("""
                    <div class="result-high">
                        <h2>⚠️ High Risk Detected</h2>
                        <p>Your inputs indicate a higher likelihood of diabetes. Please consult a healthcare professional soon.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        precautions = result.get("precautions", [])
                        items = "".join([f"<li>✅ {p}</li>" for p in precautions])
                        st.markdown(f'<div class="do-box"><h4>👍 Precautions To Follow</h4><ul>{items}</ul></div>', unsafe_allow_html=True)
                    with c2:
                        diet = result.get("diet_plan", {})
                        eat_items = "".join([f"<li>🥗 {x}</li>" for x in diet.get("eat", [])])
                        avoid_items = "".join([f"<li>🚫 {x}</li>" for x in diet.get("avoid", [])])
                        st.markdown(f"""
                        <div class="diet-eat" style="margin-bottom:10px;"><h4>✅ Foods To Eat</h4><ul>{eat_items}</ul></div>
                        <div class="diet-avoid"><h4>❌ Foods To Avoid</h4><ul>{avoid_items}</ul></div>
                        """, unsafe_allow_html=True)

                    st.info("👉 Visit the **Nearby Clinics** tab above to book an appointment with a specialist.")
                else:
                    recommendations = result.get("recommendations", [])
                    items = "".join([f"<li>🌿 {r}</li>" for r in recommendations])
                    st.markdown(f"""
                    <div class="result-low">
                        <h2>✅ Low Risk — You're Doing Great!</h2>
                        <p>Your health indicators look good. Keep up the healthy lifestyle.</p>
                        <ul>{items}</ul>
                    </div>
                    """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error("🔌 Could not connect to the prediction API. Make sure your FastAPI server is running at: " + API_URL)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ============================================================================
# TAB 2: NEARBY CLINICS + BOOKING
# ============================================================================
with tab2:
    st.subheader("🏥 Clinics & Hospitals Near You (Noida / Delhi / Gurgaon)")
    st.caption("Connect with specialists for diabetes care, diagnosis, and treatment.")

    for clinic in CLINICS:
        with st.container():
            colA, colB = st.columns([1, 2])
            with colA:
                st.image(clinic["img"], use_container_width=True)
            with colB:
                st.markdown(f"### {clinic['name']}")
                st.write(f"📍 **Distance:** {clinic['distance']}")
                st.write(f"🏠 **Address:** {clinic['address']}")
                st.write(f"📞 **Phone:** {clinic['phone']}")

                with st.expander("📅 Book Appointment"):
                    with st.form(key=f"form_{clinic['name']}"):
                        appt_date = st.date_input("Preferred Date", min_value=date.today(), key=f"date_{clinic['name']}")
                        appt_time = st.selectbox(
                            "Preferred Time Slot",
                            ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM",
                             "02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM", "05:00 PM - 06:00 PM"],
                            key=f"time_{clinic['name']}"
                        )
                        reason = st.text_area("Reason for Visit / Notes", key=f"reason_{clinic['name']}",
                                               placeholder="e.g. Diabetes consultation, sugar level check-up")
                        submitted = st.form_submit_button("✅ Confirm Appointment", use_container_width=True, type="primary")

                        if submitted:
                            save_appointment(
                                st.session_state.user["email"], clinic["name"], appt_date, appt_time, reason
                            )
                            st.success(f"🎉 Appointment booked at **{clinic['name']}** on "
                                       f"**{appt_date.strftime('%d %b %Y')}** ({appt_time}). "
                                       f"View it in 'My Appointments'.")
            st.markdown("---")

# ============================================================================
# TAB 3: MY APPOINTMENTS
# ============================================================================
with tab3:
    st.subheader("📅 My Booked Appointments")
    appts = get_appointments(st.session_state.user["email"])

    if not appts:
        st.info("You haven't booked any appointments yet. Go to the **Nearby Clinics** tab to book one.")
    else:
        for clinic_name, appt_date, appt_time, reason, created_at in appts:
            st.markdown(f"""
            <div class="section-card">
                <h4>🏥 {clinic_name}</h4>
                <p>📅 <b>Date:</b> {appt_date} &nbsp;&nbsp; 🕐 <b>Time:</b> {appt_time}</p>
                <p>📝 <b>Reason:</b> {reason if reason else 'Not specified'}</p>
                <p style="font-size:12px; opacity:0.7;">Booked on {created_at[:16].replace('T',' ')}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: ABOUT
# ============================================================================
with tab4:
    st.subheader("ℹ️ About MediCare+")

    st.markdown("""
    **MediCare+** is an AI-powered diabetes screening and clinic-connection platform built to make
    preventive healthcare simple, fast, and accessible — right from your browser.

    #### 🔬 How the Prediction Works
    When you enter your health details (glucose level, BMI, blood pressure, age, insulin levels, etc.),
    this information is sent securely to a machine learning model (trained on real medical datasets)
    hosted via a FastAPI backend. The model analyzes the patterns in your data and returns:
    - A **prediction** (Diabetic / Non-Diabetic)
    - A **risk level** (High / Low)
    - Personalized **precautions** and **diet recommendations**

    #### 🏥 Why Connect With Clinics?
    A prediction is only useful if it leads to action. That's why MediCare+ includes a directory of
    **real, well-known hospitals across Noida, Delhi, and Gurgaon**, complete with addresses, contact
    numbers, and an in-app **appointment booking system** — so if your result shows higher risk,
    you can immediately schedule a consultation with a specialist.

    #### 📅 How Appointment Booking & Storage Works
    - You select a clinic, preferred date, time slot, and reason for visit
    - On confirmation, the appointment is saved to a local database (SQLite) linked to your account email
    - You can view all your bookings anytime under **My Appointments**
    - In a production setup, this would sync with the hospital's real scheduling system via API/HL7-FHIR integration

    #### 🔐 Account & Login
    - Sign up with your **name, email, and password**
    - Passwords are stored as secure one-way hashes (never in plain text)
    - Your login session lets you book and track appointments tied to your profile
    - *(For production apps requiring social logins, OTP, or enterprise SSO, a dedicated auth provider
    like Clerk/Auth0 integrated via a React/Next.js frontend is recommended.)*

    #### 🌗 Personalization
    - Toggle between **Light** and **Dark** mode anytime from the sidebar for comfortable viewing

    #### ⚠️ Important Disclaimer
    MediCare+ is an **educational/demo tool**. It is not a certified medical device and the predictions
    should never replace a real diagnosis from a licensed physician. Always consult a doctor for
    actual diabetes screening, especially tests like **HbA1c**, **Fasting Plasma Glucose**, and
    **Oral Glucose Tolerance Test (OGTT)**.
    """)

# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.markdown("---")
st.caption("⚠️ Disclaimer: This is an AI-based screening tool for educational purposes only. "
           "It does not replace professional medical diagnosis. Always consult a certified doctor.")

st.markdown('<div class="made-by">💙 Made by Mayank_Anand</div>', unsafe_allow_html=True)