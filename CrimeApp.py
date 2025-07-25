import streamlit as st
import os, time, datetime, hashlib
import openai
import requests
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# —— OpenAI API key (for GPT-4) —— 
openai.api_key = os.getenv("AIzaSyAPS-3Oo6ofSnegNWZDO9SMe6Asf6fw5S8")

st.set_page_config(
    page_title="SECURO Crime Hub",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# —— Custom Styles ——
st.markdown("""<style>/* your custom CSS here (as in your original) */</style>""", unsafe_allow_html=True)

# —— Session-state initialization ——
def init_session():
    for key, default in {
        "users_db": {},
        "logged_in": False,
        "current_user": None,
        "user_role": None,
        "messages": [],
        "alerts": [],
        "emergency_confirmation": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session()

# —— User Authentication —— 
class UserAuth:
    def hash_pass(self, pw): return hashlib.sha256(pw.encode()).hexdigest()
    def create(self, user, pw, role):
        if user in st.session_state.users_db:
            return False, "Username exists"
        if len(pw) < 6:
            return False, "Password too short"
        st.session_state.users_db[user] = {
            "password": self.hash_pass(pw),
            "role": role,
            "created": datetime.datetime.now().isoformat()
        }
        return True, "Account created"
    def login(self, user, pw):
        db = st.session_state.users_db
        if user not in db:
            return False, "Username not found"
        if db[user]["password"] != self.hash_pass(pw):
            return False, "Invalid password"
        st.session_state.logged_in = True
        st.session_state.current_user = user
        st.session_state.user_role = db[user]["role"]
        return True, "Login successful"

auth = UserAuth()

# —— Gemini API wrapper ——
class GeminiAPI:
    def __init__(self):
        self.api_key = os.getenv("AIzaSyCsb-NiyZwU5J-AitQan9HaHzNse2kN5_c")
    def query(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
        payload = {
            "contents":[{"parts":[{"text":prompt}]}],
            "generationConfig":{"temperature":0.7,"topK":40,"topP":0.95,"maxOutputTokens":1024}
        }
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type":"application/json"}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"⚠️ Gemini API error: {e}"

gemini = GeminiAPI()

# —— Main criminology assistant —— 
class CrimBot:
    def __init__(self):
        self.stats = {
            "2023": {"total":1250,"violent":180,"property":620,"drug":280,"organized":45,"white":35,"cyber":90,"clearance":"68.2%"},
            "2024": {"total":1180,"violent":165,"property":590,"drug":260,"organized":52,"white":41,"cyber":72,"clearance":"71.8%"},
        }
        self.hotspots = [
            ("Basseterre",[17.2948,-62.7234],450,"High"),
            ("Frigate Bay",[17.2619,-62.6853],180,"Medium"),
            ("Sandy Point",[17.3547,-62.8119],120,"Medium"),
            ("Charlestown",[17.1372,-62.6219],200,"Medium"),
            ("Dieppe Bay",[17.4075,-62.8097],90,"Low"),
        ]
        self.emergency = {
            "police":("Royal St. Christopher and Nevis Police Force","911","(869) 465‑2241"),
            "hospital":("Joseph N. France General Hospital","911","(869) 465‑2551"),
            "fire":("Fire & Rescue Services","911","(869) 465‑2366")
        }

    def analyze_report_with_gpt(self, text):
        prompt = (
            f"You are a crime mitigation assistant. A user submitted this report:\n\"{text}\"\n"
            "1. Summarize.\n2. Threat level (low/medium/high).\n3. Next steps."
        )
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}]
        )
        return resp.choices[0].message["content"]

    def create_crime_chart(self, year="2024"):
        d = self.stats[year]
        categories = ["Violent","Property","Drug","Organized","White","Cyber"]
        values = [d["violent"],d["property"],d["drug"],d["organized"],d["white"],d["cyber"]]
        fig, (ax1,ax2) = plt.subplots(1,2,figsize=(14,6))
        ax1.pie(values, labels=categories, autopct="%1.1f%%", startangle=90)
        ax1.set_title(f"Crime Distribution {year}")
        ax2.bar(["2023","2024"],[self.stats["2023"]["violent"],d["violent"]], label="Violent")
        ax2.bar(["2023","2024"],[self.stats["2023"]["property"],d["property"]], label="Property")
        ax2.set_title("Violent vs Property Crime Trends")
        ax2.legend()
        plt.tight_layout()
        return fig

    def create_hotspot_map(self):
        m = folium.Map(location=[17.3578,-62.7822], zoom_start=11)
        for name, coords, count, lvl in self.hotspots:
            color = {"High":"red","Medium":"orange","Low":"green"}.get(lvl, "blue")
            folium.CircleMarker(location=coords, radius=count/20,
                                popup=f"{name}: {count} crimes ({lvl})",
                                color=color, fill=True, fillOpacity=0.6).add_to(m)
        return m

    def get_contact(self, svc):
        if svc in self.emergency:
            name,num,alt = self.emergency[svc]
            return (
                f"⚠️ You’re about to contact **{name}**.\n"
                f"Call **{num}** or alternative **{alt}**.\n"
                "Proceed?"
            )
        return "Service not found."

bot = CrimBot()

# —— Login / Signup UI —— 
def auth_ui():
    tabs = st.tabs(["Login","Create Account"])
    with tabs[0]:
        u = st.text_input("Username", key="li_user")
        p = st.text_input("Password", type="password", key="li_pw")
        if st.button("Login"):
            ok, msg = auth.login(u,p)
            st.success(msg) if ok else st.error(msg)
            if ok: st.experimental_rerun()
    with tabs[1]:
        u2 = st.text_input("New Username", key="cu_user")
        p2 = st.text_input("New Password", type="password", key="cu_pw")
        p2c = st.text_input("Confirm", type="password", key="cu_pwc")
        role = st.selectbox("Role", ["Criminologist","Law Enforcement","Researcher","Student"])
        if st.button("Create"):
            if p2 != p2c:
                st.error("Passwords mismatch")
            else:
                ok,msg = auth.create(u2,p2,role)
                st.success(msg) if ok else st.error(msg)

if not st.session_state.logged_in:
    st.title("SECURO Crime Mitigation Hub")
    st.markdown("<p class='subtitle'>Login or create account</p>", unsafe_allow_html=True)
    auth_ui()
    st.stop()

# —— Sidebar —— 
with st.sidebar:
    st.write(f"User: **{st.session_state.current_user}**\nRole: *{st.session_state.user_role}*")
    if st.button("Logout"):
        st.session_state.logged_in=False; st.session_state.current_user=None
        st.experimental_rerun()
    st.header("Tools")
    if st.button("Crime Stats Chart"):
        fig = bot.create_crime_chart()
        st.pyplot(fig)
    if st.button("Crime Hotspot Map"):
        folium_static(bot.create_hotspot_map(), width=300, height=400)
    st.markdown("### Emergency Contacts")
    for svc in ["police","hospital","fire"]:
        if st.button(svc.title()):
            st.session_state.emergency_confirmation = svc
    if st.session_state.emergency_confirmation:
        svc = st.session_state.emergency_confirmation
        if st.button("Confirm Contact"):
            resp = bot.get_contact(svc)
            st.session_state.messages.append({"role":"assistant","content":resp})
            st.session_state.emergency_confirmation = None
            st.experimental_rerun()
        if st.button("Cancel"):
            st.session_state.messages.append({"role":"assistant","content":"Emergency contact canceled."})
            st.session_state.emergency_confirmation = None
            st.experimental_rerun()

# —— Chat / alert entry UI —— 
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(f"<div class='user-message'><div class='user-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'><div class='bot-bubble'>{msg['content']}</div></div>", unsafe_allow_html=True)

# Input loop for crime reports or queries
user_input = st.chat_input("Enter crime report or ask criminology question...")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    lower = user_input.lower()
    if lower.startswith("report:"):
        report = user_input[len("report:"):].strip()
        analysis = bot.analyze_report_with_gpt(report)
        st.session_state.messages.append({"role":"assistant","content":analysis})
        location = st.text_input("Location for this report:", key="loc_in")
        lat = st.text_input("Latitude:", key="lat_in")
        lon = st.text_input("Longitude:", key="lon_in")
        status = st.selectbox("Status", ["active","resolved"], key="status_in")
        share = st.checkbox("Share alert", key="share_in")
        if st.button("Submit alert"):
            try:
                lt,ln = float(lat), float(lon)
                if share:
                    st.session_state.alerts.append({
                        "text": analysis, "location": location,
                        "lat": lt, "lon": ln, "status": status
                    })
                st.success(f"Alert for {location} added as {status}")
            except:
                st.error("Invalid coordinates")
    else:
        # non-report queries => delegate to Gemini
        resp = gemini.query(
            CrimBot().create_criminology_prompt(user_input) if hasattr(bot, "create_criminology_prompt") else user_input
        )
        st.session_state.messages.append({"role":"assistant","content":resp})
    st.experimental_rerun()
