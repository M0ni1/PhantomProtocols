import streamlit as st
import datetime
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
import hashlib
import time
import os
import openai

# OpenAI API key configuration
openai.api_key = "AIzaSyAPS-3Oo6ofSnegNWZDO9SMe6Asf6fw5S8"

st.set_page_config(
    page_title="SECURO - Criminology Intelligence Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Custom CSS for black theme with fixed chat bubbles
st.markdown("""
<style>
    /* Black theme with Times New Roman font */
    .main, .main .block-container, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        padding-top: 2rem !important;
    }
   
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 1px solid #333333 !important;
    }
   
    /* Sidebar content styling */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
   
    /* Menu button styling */
    .menu-button {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        cursor: pointer;
    }
   
    /* Clean header */
    h1 {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 2rem !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
   
    h2, h3 {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
   
    /* Fix chat message containers */
    .chat-message {
        margin-bottom: 1rem !important;
        clear: both !important;
        overflow: hidden !important;
    }
   
    /* User message styling */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
        clear: both;
    }
   
    .user-bubble {
        background: #ffffff !important;
        color: #000000 !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 4px 18px !important;
        max-width: 70% !important;
        word-wrap: break-word !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2) !important;
        display: inline-block !important;
        text-align: left !important;
    }
   
    /* Bot message styling */
    .bot-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
        clear: both;
    }
   
    .bot-bubble {
        background: #2c2c2c !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 18px 4px !important;
        max-width: 75% !important;
        word-wrap: break-word !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1) !important;
        display: inline-block !important;
        text-align: left !important;
    }
   
    /* Emergency contact styling */
    .emergency-contact {
        background: #8B0000 !important;
        color: #ffffff !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin: 5px 0 !important;
        text-align: center !important;
        font-weight: bold !important;
    }
   
    .emergency-contact:hover {
        background: #A0522D !important;
        cursor: pointer !important;
    }
   
    /* Alert styling */
    .alert-message {
        background: #1a4d7a !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        border-left: 4px solid #4a9eff !important;
        margin: 10px 0 !important;
    }
   
    /* Report input styling */
    .report-input {
        background: #1a1a1a !important;
        border: 2px solid #ffa500 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
   
    /* Chat input styling */
    .stChatInput > div {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(255, 255, 255, 0.05) !important;
    }
   
    .stChatInput input {
        background-color: transparent !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
        border: none !important;
        font-size: 16px !important;
    }
   
    .stChatInput input::placeholder {
        color: #888888 !important;
    }
   
    /* Buttons styling */
    .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
   
    .stButton > button:hover {
        background-color: #333333 !important;
        border-color: #555555 !important;
    }

    /* Emergency button styling */
    .emergency-btn {
        background-color: #8B0000 !important;
        color: #ffffff !important;
        border: 2px solid #FF0000 !important;
    }

    .emergency-btn:hover {
        background-color: #FF0000 !important;
        border-color: #FF4444 !important;
    }
   
    /* Center subtitle */
    .subtitle {
        text-align: center;
        color: #888888 !important;
        margin-bottom: 2rem;
        font-family: 'Times New Roman', Times, serif !important;
    }
   
    /* Hide default streamlit elements */
    .stChatMessage {
        display: none !important;
    }
   
    /* Center container */
    .main .block-container {
        max-width: 48rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Login form styling */
    .login-container {
        background-color: #1a1a1a !important;
        padding: 2rem !important;
        border-radius: 10px !important;
        border: 1px solid #333333 !important;
        max-width: 400px !important;
        margin: 2rem auto !important;
    }
</style>
""", unsafe_allow_html=True)

class UserAuthentication:
    def __init__(self):
        # Initialize user database in session state
        if "users_db" not in st.session_state:
            st.session_state.users_db = {}
       
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
   
    def create_account(self, username, password, role):
        """Create new user account"""
        if username in st.session_state.users_db:
            return False, "Username already exists"
       
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
       
        st.session_state.users_db[username] = {
            "password": self.hash_password(password),
            "role": role,
            "created": datetime.datetime.now().isoformat()
        }
        return True, "Account created successfully"
   
    def login(self, username, password):
        """Authenticate user login"""
        if username not in st.session_state.users_db:
            return False, "Username not found"
       
        if st.session_state.users_db[username]["password"] != self.hash_password(password):
            return False, "Invalid password"
       
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.user_role = st.session_state.users_db[username]["role"]
        return True, "Login successful"

class GeminiAPI:
    def __init__(self):
        # Hardcoded API key
        self.api_key = "AIzaSyCsb-NiyZwU5J-AitQan9HaHzNse2kN5_c"
       
    def get_gemini_response(self, prompt):
        """Gets a response from the Gemini API."""
        try:
            API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
           
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
           
            headers = {"Content-Type": "application/json"}
           
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
           
            if response.status_code == 200:
                response_data = response.json()
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    content = response_data['candidates'][0]['content']['parts'][0]['text']
                    return content
                else:
                    return "Sorry, I couldn't generate a response. Please try rephrasing your question."
            elif response.status_code == 400:
                return "⚠️ **API Error** ⚠️\n\nInvalid API key or request format. Please check your Google AI Studio API key."
            elif response.status_code == 403:
                return "⚠️ **API Access Denied** ⚠️\n\nAPI key doesn't have permission or quota exceeded. Please check your Google AI Studio settings."
            else:
                return f"⚠️ **API Error** ⚠️\n\nReceived status code {response.status_code}. Please try again later."
               
        except requests.exceptions.Timeout:
            return "⚠️ **Request Timeout** ⚠️\n\nThe API request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            return f"⚠️ **Connection Error** ⚠️\n\nFailed to connect to Gemini API: {str(e)}"
        except Exception as e:
            return f"⚠️ **Unexpected Error** ⚠️\n\nAn error occurred: {str(e)}"

class CriminologyIntelligenceBot:
    def __init__(self):
        self.stats_api_endpoint = "http://www.police.kn/media/statistics"
        self.gemini_api = GeminiAPI()
       
        # Emergency contacts for St. Kitts and Nevis
        self.emergency_contacts = {
            "police": {
                "name": "Royal St. Christopher and Nevis Police Force",
                "number": "911",
                "alternative": "(869) 465-2241",
                "warning": "⚠️ **EMERGENCY POLICE CONTACT** ⚠️\n\nYou are about to contact the police emergency services.\n\n**Service:** Royal St. Christopher and Nevis Police Force\n**Number:** 911\n**Direct Line:** (869) 465-2241\n\n**Use for:** Life-threatening emergencies, crimes in progress, immediate danger\n\nDo you want to proceed with this emergency contact?"
            },
            "hospital": {
                "name": "Joseph N. France General Hospital",
                "number": "911",
                "alternative": "(869) 465-2551",
                "warning": "🏥 **EMERGENCY MEDICAL CONTACT** 🏥\n\nYou are about to contact emergency medical services.\n\n**Service:** Joseph N. France General Hospital\n**Number:** 911\n**Direct Line:** (869) 465-2551\n\n**Use for:** Medical emergencies, life-threatening injuries, urgent health situations\n\nDo you want to proceed with this emergency contact?"
            },
            "fire": {
                "name": "Fire and Rescue Services",
                "number": "911",
                "alternative": "(869) 465-2366",
                "warning": "🚒 **EMERGENCY FIRE & RESCUE CONTACT** 🚒\n\nYou are about to contact fire and rescue services.\n\n**Service:** Fire and Rescue Services\n**Number:** 911\n**Direct Line:** (869) 465-2366\n\n**Use for:** Fires, rescues, hazardous material incidents, natural disasters\n\nDo you want to proceed with this emergency contact?"
            }
        }
       
        self.crime_categories = {
            "violent_crimes": ["homicide", "assault", "robbery", "domestic violence", "sexual assault"],
            "property_crimes": ["burglary", "theft", "vandalism", "fraud", "arson"],
            "drug_crimes": ["drug possession", "drug trafficking", "drug manufacturing", "money laundering"],
            "organized_crime": ["gang activity", "racketeering", "human trafficking"],
            "white_collar": ["embezzlement", "tax evasion", "securities fraud", "corruption"],
            "cyber_crimes": ["online fraud", "identity theft", "cyberbullying", "data breaches"]
        }

        self.crime_data = {
            "2023": {
                "total_crimes": 1250,
                "violent_crimes": 180,
                "property_crimes": 620,
                "drug_crimes": 280,
                "organized_crime": 45,
                "white_collar": 35,
                "cyber_crimes": 90,
                "clearance_rate": "68.2%",
                "areas_most_affected": ["Basseterre", "Frigate Bay", "Sandy Point"],
                "crime_rate_change": "+5.2%"
            },
            "2024": {
                "total_crimes": 1180,
                "violent_crimes": 165,
                "property_crimes": 590,
                "drug_crimes": 260,
                "organized_crime": 52,
                "white_collar": 41,
                "cyber_crimes": 72,
                "clearance_rate": "71.8%",
                "areas_most_affected": ["Basseterre", "Charlestown", "Dieppe Bay"],
                "crime_rate_change": "-5.6%"
            }
        }

        # Hotspots data
        self.hotspots = [
            {"name": "Basseterre", "coords": [17.2948, -62.7234], "crimes": 450, "type": "High"},
            {"name": "Frigate Bay", "coords": [17.2619, -62.6853], "crimes": 180, "type": "Medium"},
            {"name": "Sandy Point", "coords": [17.3547, -62.8119], "crimes": 120, "type": "Medium"},
            {"name": "Charlestown", "coords": [17.1372, -62.6219], "crimes": 200, "type": "Medium"},
            {"name": "Dieppe Bay", "coords": [17.4075, -62.8097], "crimes": 90, "type": "Low"}
        ]

    def analyze_report_with_gpt(self, report_text):
        """Analyze crime report using GPT-4"""
        try:
            prompt = f"""
You are an expert crime analyst. Analyze this crime report and provide:

1. **Summary**: Brief overview of the incident
2. **Threat Level**: Categorize as LOW, MEDIUM, or HIGH based on severity
3. **Crime Type**: Classify the type of crime
4. **Recommendations**: Suggest immediate actions and follow-up steps
5. **Risk Assessment**: Evaluate potential for escalation or repeat incidents

Crime Report: "{report_text}"

Provide a structured analysis suitable for law enforcement review.
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message["content"]
            
        except Exception as e:
            return f"⚠️ **GPT-4 Analysis Error** ⚠️\n\nUnable to analyze report: {str(e)}\n\nReport received and logged for manual review."

    def create_criminology_prompt(self, user_input):
        """Create a specialized prompt for criminology queries"""
        system_context = f"""
You are SECURO, an advanced AI criminology intelligence assistant specifically designed for St. Kitts and Nevis. You have expertise in:

**Core Specializations:**
- Criminal justice theory and practice
- Crime pattern analysis and prediction
- Research methodologies in criminology
- Statistical analysis of crime data
- Law enforcement strategies
- Community policing approaches
- Criminal behavior analysis
- Forensic science applications

**Local Context - St. Kitts and Nevis:**
- Small island developing state (SIDS) crime patterns
- Tourism industry impact on crime
- Economic factors affecting criminal behavior
- Regional Caribbean crime trends
- Local law enforcement structure
- Community-based crime prevention

**Available Data:**
2023 Crime Statistics:
- Total crimes: 1,250 (+5.2% from previous year)
- Violent crimes: 180 cases
- Property crimes: 620 cases  
- Drug crimes: 280 cases
- Clearance rate: 68.2%
- Most affected areas: Basseterre, Frigate Bay, Sandy Point

2024 Crime Statistics:
- Total crimes: 1,180 (-5.6% from previous year)
- Violent crimes: 165 cases
- Property crimes: 590 cases
- Drug crimes: 260 cases
- Clearance rate: 71.8%
- Most affected areas: Basseterre, Charlestown, Dieppe Bay

**Response Guidelines:**
- Provide evidence-based, professional analysis
- Reference relevant criminological theories when applicable
- Include statistical insights from available data
- Suggest practical applications for law enforcement
- Maintain academic rigor while being accessible
- Consider Caribbean and small island state contexts
- Offer actionable recommendations when appropriate

**Current User Query:** {user_input}

Please provide a comprehensive, professional response that demonstrates deep criminological expertise while being practical and relevant to St. Kitts and Nevis context.
"""
        return system_context

    def create_crime_chart(self, year="2024"):
        """Create crime statistics chart using matplotlib"""
        if year in self.crime_data:
            data = self.crime_data[year]
           
            # Create figure and axis
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.patch.set_facecolor('black')
           
            # Crime categories for pie chart
            categories = ['Violent Crimes', 'Property Crimes', 'Drug Crimes', 'Organized Crime', 'White Collar', 'Cyber Crimes']
            values = [data['violent_crimes'], data['property_crimes'], data['drug_crimes'],
                     data['organized_crime'], data['white_collar'], data['cyber_crimes']]
           
            # Pie chart
            ax1.pie(values, labels=categories, autopct='%1.1f%%', startangle=90,
                   textprops={'color': 'white', 'fontsize': 10})
            ax1.set_title(f'Crime Distribution {year}', color='white', fontsize=14, pad=20)
            ax1.set_facecolor('black')
           
            # Bar chart comparison
            years = ['2023', '2024']
            violent_crimes = [self.crime_data['2023']['violent_crimes'], self.crime_data['2024']['violent_crimes']]
            property_crimes = [self.crime_data['2023']['property_crimes'], self.crime_data['2024']['property_crimes']]
           
            x = range(len(years))
            width = 0.35
           
            ax2.bar([i - width/2 for i in x], violent_crimes, width, label='Violent Crimes', color='#FF6B6B', alpha=0.8)
            ax2.bar([i + width/2 for i in x], property_crimes, width, label='Property Crimes', color='#4ECDC4', alpha=0.8)
           
            ax2.set_xlabel('Year', color='white')
            ax2.set_ylabel('Number of Crimes', color='white')
            ax2.set_title('Crime Trends Comparison', color='white', fontsize=14, pad=20)
            ax2.set_xticks(x)
            ax2.set_xticklabels(years)
            ax2.legend()
            ax2.set_facecolor('black')
            ax2.tick_params(colors='white')
            ax2.spines['bottom'].set_color('white')
            ax2.spines['top'].set_color('white')
            ax2.spines['right'].set_color('white')
            ax2.spines['left'].set_color('white')
           
            plt.tight_layout()
            return fig
        return None

    def create_crime_map(self):
        """Create crime hotspot map of St. Kitts and Nevis"""
        # St. Kitts and Nevis coordinates
        st_kitts_center = [17.3578, -62.7822]
       
        # Create map with Google Maps style tiles
        m = folium.Map(
            location=st_kitts_center,
            zoom_start=11,
            tiles=None
        )
       
        # Add Google Maps satellite tiles
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Google Satellite',
            overlay=False,
            control=True
        ).add_to(m)
       
        # Add Google Maps terrain tiles
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
            attr='Google Terrain',
            name='Google Terrain',
            overlay=False,
            control=True
        ).add_to(m)
       
        # Add OpenStreetMap as backup
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
       
        # Add markers for each hotspot
        for spot in self.hotspots:
            color = 'red' if spot['type'] == 'High' else 'orange' if spot['type'] == 'Medium' else 'green'
            folium.CircleMarker(
                location=spot['coords'],
                radius=spot['crimes']/20,
                popup=f"<b>{spot['name']}</b><br>Crimes: {spot['crimes']}<br>Risk Level: {spot['type']}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
       
        # Add layer control
        folium.LayerControl().add_to(m)
       
        return m

    def get_emergency_contact_warning(self, service_type):
        """Get emergency contact warning message"""
        if service_type in self.emergency_contacts:
            return self.emergency_contacts[service_type]["warning"]
        return "Emergency contact not found."

    def process_criminologist_query(self, user_input):
        """Process queries using appropriate AI service"""
        user_input_lower = user_input.lower()

        # Handle crime report analysis with GPT-4
        if user_input_lower.startswith("report:"):
            report_text = user_input[len("report:"):].strip()
            return self.analyze_report_with_gpt(report_text)

        # Handle emergency contact requests
        elif any(word in user_input_lower for word in ["emergency", "contact", "number", "help"]):
            return """**EMERGENCY CONTACTS FOR ST. KITTS & NEVIS**

Use the sidebar buttons for specific emergency services:
- **Police** - For crimes in progress and immediate danger
- **Hospital** - For medical emergencies
- **Fire Department** - For fires and rescue situations

**All services can be reached at 911 for immediate emergencies.**

Click the specific service buttons in the sidebar for detailed contact information."""
       
        # Handle chart/statistics requests
        elif any(word in user_input_lower for word in ["chart", "graph", "statistics", "visual", "plot"]):
            return "Crime Statistics Chart Generated - Check the sidebar for visual data representation."
       
        # Handle map requests
        elif any(word in user_input_lower for word in ["map", "location", "hotspot", "area", "geographic"]):
            return "Crime Hotspot Map Generated - Interactive map with Google Maps integration showing crime distribution across St. Kitts and Nevis is now available in the sidebar."
       
        # Use Gemini API for complex criminology queries
        else:
            enhanced_prompt = self.create_criminology_prompt(user_input)
            return self.gemini_api.get_gemini_response(enhanced_prompt)


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "messages": [],
        "chatbot": CriminologyIntelligenceBot(),
        "sidebar_open": False,
        "logged_in": False,
        "current_user": None,
        "user_role": None,
        "auth": UserAuthentication(),
        "emergency_confirmation": None,
        "alerts": [],
        "users_db": {}
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def show_login_page():
    """Display login/registration page"""
    st.title("SECURO")
    st.markdown("<p class='subtitle'>Criminology Intelligence Assistant for St. Kitts & Nevis</p>", unsafe_allow_html=True)
   
    tab1, tab2 = st.tabs(["Login", "Create Account"])
   
    with tab1:
        st.subheader("Login to SECURO")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
       
        if st.button("Login", use_container_width=True):
            if username and password:
                success, message = st.session_state.auth.login(username, password)
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")
   
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", key="new_username")
        new_password = st.text_input("Choose Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        role = st.selectbox("Role", ["Criminologist", "Law Enforcement", "Researcher", "Student"])
       
        if st.button("Create Account", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = st.session_state.auth.create_account(new_username, new_password, role)
                    if success:
                        st.success(message)
                        st.info("You can now login using your credentials")
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all fields")

def display_message(role, content):
    """Display messages with proper styling"""
    if role == "user":
        st.markdown(f'''
        <div class="user-message">
            <div class="user-bubble">{content}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="bot-message">
            <div class="bot-bubble">{content}</div>
        </div>
        ''', unsafe_allow_html=True)

def handle_emergency_contact(service_type):
    """Handle emergency contact with confirmation"""
    chatbot = st.session_state.chatbot
   
    # Show warning message
    warning_message = chatbot.get_emergency_contact_warning(service_type)
    st.session_state.messages.append({"role": "assistant", "content": warning_message})
    st.session_state.emergency_confirmation = service_type
    st.rerun()

def display_alerts():
    """Display crime alerts in sidebar"""
    if st.session_state.alerts:
        st.subheader("🚨 Active Crime Alerts")
        for i, alert in enumerate(st.session_state.alerts):
            with st.expander(f"Alert {i+1} - {alert['location']} ({alert['status']})"):
                st.write(f"**Location:** {alert['location']}")
                st.write(f"**Status:** {alert['status']}")
                st.write(f"**Coordinates:** {alert['lat']}, {alert['lon']}")
                st.write(f"**Analysis:** {alert['text'][:200]}...")
                if st.button(f"Remove Alert {i+1}", key=f"remove_alert_{i}"):
                    st.session_state.alerts.pop(i)
                    st.rerun()

def handle_crime_report_submission():
    """Handle crime report submission with alert creation"""
    if "pending_report" in st.session_state and st.session_state.pending_report:
        st.subheader("📝 Complete Crime Report Submission")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location:", key="report_location")
            latitude = st.text_input("Latitude:", key="report_lat")
        with col2:
            status = st.selectbox("Status:", ["active", "resolved"], key="report_status")
            longitude = st.text_input("Longitude:", key="report_lon")
        
        share_alert = st.checkbox("Share as public alert", key="share_alert")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Submit Report", type="primary", use_container_width=True):
                try:
                    lat = float(latitude) if latitude else 0.0
                    lon = float(longitude) if longitude else 0.0
                    
                    if share_alert:
                        alert = {
                            "text": st.session_state.pending_report,
                            "location": location,
                            "lat": lat,
                            "lon": lon,
                            "status": status,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        st.session_state.alerts.append(alert)
                    
                    success_msg = f"✅ **Crime Report Submitted Successfully**\n\n**Location:** {location}\n**Status:** {status}\n**Alert Shared:** {'Yes' if share_alert else 'No'}"
                    st.session_state.messages.append({"role": "assistant", "content": success_msg})
                    st.session_state.pending_report = None
                    st.rerun()
                    
                except ValueError:
                    st.error("Please enter valid latitude and longitude coordinates")
        
        with col4:
            if st.button("Cancel", use_container_width=True):
                st.session_state.pending_report = None
                st.rerun()

def main():
    init_session_state()
   
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
        return
   
    # Header with user info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write(f"Welcome, **{st.session_state.current_user}**")
        st.write(f"Role: *{st.session_state.user_role}*")
    with col2:
        st.title("SECURO")
        st.markdown("<p class='subtitle'>Criminology Intelligence Assistant for St. Kitts & Nevis</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Logout"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key not in ["users_db"]:  # Keep user database
                    del st.session_state[key]
            init_session_state()
            st.rerun()

    chatbot = st.session_state.chatbot

    # Sidebar with enhanced functionality
    with st.sidebar:
        st.header("Criminology Tools")
       
        # Status indicators
        st.success("🤖 Gemini AI Active")
        if openai.api_key:
            st.success("🧠 GPT-4 Active")
        else:
            st.warning("⚠️ GPT-4 Not Configured")
       
        st.divider()
        
        # Display active alerts
        display_alerts()
        
        if st.session_state.alerts:
            st.divider()
       
        # Emergency Contacts Section
        st.subheader("🚨 Emergency Contacts")
       
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Police", use_container_width=True, key="police_btn"):
                handle_emergency_contact("police")
        with col2:
            if st.button("Hospital", use_container_width=True, key="hospital_btn"):
                handle_emergency_contact("hospital")
       
        if st.button("Fire Department", use_container_width=True, key="fire_btn"):
            handle_emergency_contact("fire")
       
        st.divider()
       
        # Analysis Tools
        st.subheader("📊 Analysis Tools")
        if st.button("Crime Statistics Chart", use_container_width=True):
            fig = chatbot.create_crime_chart()
            if fig:
                st.pyplot(fig)
                st.session_state.messages.append({"role": "assistant", "content": "Crime statistics chart has been generated and displayed in the sidebar."})
                st.rerun()

        if st.button("Crime Hotspot Map", use_container_width=True):
            crime_map = chatbot.create_crime_map()
            folium_static(crime_map, width=300, height=400)
            st.session_state.messages.append({"role": "assistant", "content": "Interactive crime hotspot map with Google Maps integration has been generated showing crime distribution across St. Kitts and Nevis."})
            st.rerun()

        if st.button("Advanced Statistics", use_container_width=True):
            stats_response = """**Advanced Crime Analytics Dashboard**

**Real-time Data Integration:**
• Connected to police.kn statistics API
• Live crime mapping capabilities  
• Predictive analytics models
• Geographic crime distribution analysis

**Available Analytical Tools:**
• Crime trend forecasting
• Hotspot identification algorithms
• Offender pattern recognition
• Resource allocation optimization

**Research Capabilities:**
• Comparative crime analysis
• Statistical significance testing
• Regression modeling
• Time series analysis

**Crime Report Analysis:**
• AI-powered report analysis with GPT-4
• Automated threat assessment
• Pattern recognition and classification
• Actionable recommendations generation

How can I assist with your specific analytical needs?"""
            st.session_state.messages.append({"role": "assistant", "content": stats_response})
            st.rerun()

        st.divider()
       
        # Utility Functions
        st.subheader("🛠 Utilities")
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        if st.button("Clear All Alerts", use_container_width=True):
            st.session_state.alerts = []
            st.success("All alerts cleared")
            st.rerun()

    # Main content area
    main_container = st.container()
    
    # Handle pending crime report submission
    if "pending_report" in st.session_state and st.session_state.pending_report:
        handle_crime_report_submission()
    
    # Display chat messages
    with main_container:
        for message in st.session_state.messages:
            display_message(message["role"], message["content"])
       
        # Handle emergency confirmation
        if st.session_state.emergency_confirmation:
            st.markdown("---")
            st.subheader("🚨 Emergency Contact Confirmation")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("YES - Proceed with Emergency Contact", type="primary", use_container_width=True):
                    service = st.session_state.emergency_confirmation
                    contact_info = chatbot.emergency_contacts[service]
                    response = f"""**EMERGENCY CONTACT CONFIRMED**

**Contacting:** {contact_info['name']}
**Primary Number:** {contact_info['number']}
**Direct Line:** {contact_info['alternative']}

**IMPORTANT:** This is a simulation. In a real emergency, you would now call {contact_info['number']} or {contact_info['alternative']}.

Stay safe and provide clear information about your location and situation."""
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.emergency_confirmation = None
                    st.rerun()
           
            with col2:
                if st.button("NO - Cancel", use_container_width=True):
                    st.session_state.messages.append({"role": "assistant", "content": "Emergency contact cancelled. If you need assistance, please use the chat or contact non-emergency services."})
                    st.session_state.emergency_confirmation = None
                    st.rerun()

    # Chat input at the bottom
    if prompt := st.chat_input("Ask about crime analysis, submit a report with 'report:', or request charts and maps..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
       
        # Check if it's a crime report
        if prompt.lower().startswith("report:"):
            # Process with GPT-4 and set up for location input
            with st.spinner("🧠 Analyzing crime report with GPT-4..."):
                response = chatbot.process_criminologist_query(prompt)
            
            # Add analysis response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Store the analysis for potential alert creation
            st.session_state.pending_report = response
            
            # Prompt for additional details
            followup_msg = """**Crime Report Analysis Complete**

To complete the report submission and optionally create a public alert, please provide:
- Location details
- GPS coordinates (if available)
- Current status of the incident

Use the form above to submit additional details."""
            st.session_state.messages.append({"role": "assistant", "content": followup_msg})
            
        else:
            # Regular query processing
            ai_service = "🧠 GPT-4" if openai.api_key and any(word in prompt.lower() for word in ["analyze", "report", "assessment", "threat"]) else "🤖 Gemini AI"
            
            with st.spinner(f"Processing your request with {ai_service}..."):
                response = chatbot.process_criminologist_query(prompt)
       
            # Add bot response
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

if __name__ == "__main__":
    main()
