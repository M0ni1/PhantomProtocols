import streamlit as st
import openai
import requests
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="SECURO Crime Mitigation Hub", layout="wide")

# --- CSS Styling ---
st.markdown("""
<style>
body, .stApp {
    font-family: 'Times New Roman', serif !important;
}
.user-bubble {
    background-color: #e0e0e0;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.bot-bubble {
    background-color: #f1f1ff;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- API KEYS ---
openai.api_key = "AIzaSyAPS-3Oo6ofSnegNWZDO9SMe6Asf6fw5S8"
gemini_api_key = "AIzaSyCsb-NiyZwU5J-AitQan9HaHzNse2kN5_c"

# --- Session Init ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# --- Sidebar: Map, Chart, Emergency ---
with st.sidebar:
    st.header("📍 Crime Hotspot Map")

    m = folium.Map(location=[37.77, -122.42], zoom_start=12)
    for alert in st.session_state.alerts:
        folium.Marker(location=alert["location"], tooltip=alert["status"]).add_to(m)

    st_data = st_folium(m, width=300, height=250)

    st.divider()
    st.subheader("📊 Crime Stats")
    fig, ax = plt.subplots()
    categories = ["Theft", "Assault", "Burglary", "Robbery"]
    values = [15, 10, 5, 8]
    ax.bar(categories, values, color="#405DE6")
    ax.set_ylabel("Incidents")
    st.pyplot(fig)

    st.divider()
    st.subheader("🚨 Emergency Contacts")
    st.markdown("[📞 Call Police](tel:911)", unsafe_allow_html=True)
    st.markdown("[🚒 Call Fire Department](tel:911)", unsafe_allow_html=True)
    st.markdown("[🏥 Call Hospital](tel:911)", unsafe_allow_html=True)

# --- Main Title ---
st.title("🔒 SECURO Crime Mitigation Hub")

# --- Chat Interface ---
st.subheader("🧠 Intelligence Assistant")

# Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'><strong>You:</strong> {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'><strong>Bot:</strong> {msg['content']}</div>", unsafe_allow_html=True)

# Chat Input Form
with st.form("crime_chat_form", clear_on_submit=True):
    user_input = st.text_area("Enter your crime report (start with 'report:') or ask a criminology question")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if user_input.lower().startswith("report:"):
        # Use OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're a professional crime analyst. Provide insights on incidents."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"OpenAI error: {str(e)}"
    else:
        # Use Gemini (Pure HTTP)
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta1/models/chat-bison-001:generateMessage?key={gemini_api_key}"
            payload = {
                "prompt": {
                    "context": "You're a criminology expert AI assistant.",
                    "examples": [],
                    "messages": [{"author": "user", "content": user_input}]
                },
                "temperature": 0.7,
                "candidate_count": 1
            }
            headers = {"Content-Type": "application/json"}
            res = requests.post(gemini_url, headers=headers, json=payload)
            reply = res.json()["candidates"][0]["content"]
        except Exception as e:
            reply = f"Gemini error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.experimental_rerun()

# --- Alert Submission ---
st.divider()
st.subheader("🚨 Submit Crime Alert")

with st.form("alert_form"):
    lat = st.number_input("Latitude", value=37.77)
    lon = st.number_input("Longitude", value=-122.42)
    status = st.text_input("Alert Status (e.g. Robbery, Suspicious Activity)")
    submitted_alert = st.form_submit_button("Submit Alert")

if submitted_alert:
    new_alert = {"location": [lat, lon], "status": status}
    st.session_state.alerts.append(new_alert)
    st.success("✅ Alert submitted.")
    st.experimental_rerun()
