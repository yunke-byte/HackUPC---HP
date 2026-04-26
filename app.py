import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
import json
import google.generativeai as genai

# --- PAGE CONFIG (ONLY ONCE, MUST BE FIRST STREAMLIT CALL) ---
st.set_page_config(page_title="MetalJet Digital Twin v1.2", layout="wide")

# --- CORE ENGINE LOGIC ---
class Component:
    def __init__(self, name):
        self.name = name
        self.health = 1.0
        self.cumulative_stress = 0.0

    def get_status(self):
        if self.health >= 0.80: return "OPTIMAL"
        elif self.health >= 0.40: return "DEGRADED"
        elif self.health >= 0.10: return "CRITICAL"
        else: return "TOTAL FAILURE"

class RecoaterBlade(Component):
    def __init__(self):
        super().__init__("Recoater Blade")
        self.eta, self.beta = 5000.0, 1.5

    def update(self, load, contamination, maintenance):
        stress_rate = load * (1.0 + (contamination * 2.5)) * (2.0 - maintenance)
        self.cumulative_stress += stress_rate
        self.health = math.exp(-math.pow(self.cumulative_stress / self.eta, self.beta))
        self.health = max(0.0, min(1.0, self.health))
        return {"thickness_mm": round(1.5 + (0.5 * self.health), 3)}

class HeatingElement(Component):
    def __init__(self):
        super().__init__("Heating Element")
        self.A, self.Ea_R = 0.05, 300.0

    def update(self, load, temp_celsius, maintenance):
        temp_kelvin = temp_celsius + 273.15
        lambda_rate = self.A * math.exp(-self.Ea_R / temp_kelvin)
        self.cumulative_stress += load * lambda_rate * (2.0 - maintenance)
        self.health = math.exp(-self.cumulative_stress * 0.005)
        self.health = max(0.0, min(1.0, self.health))
        return {"resistance_ohms": round(10.0 + (5.0 * (1.0 - self.health)), 2)}

class NozzlePlate(Component):
    def __init__(self):
        super().__init__("Nozzle Plate")
        self.clog_percentage = 0.0

    def update(self, load, external_contamination, temp_celsius, maintenance, recoater_health):
        internal_contamination = (0.6 - recoater_health) * 2.0 if recoater_health < 0.6 else 0.0
        total_contamination = external_contamination + internal_contamination
        temp_stress = abs(temp_celsius - 25.0) * 0.01
        clog_rate = load * (total_contamination + temp_stress) * (2.0 - maintenance)
        self.clog_percentage = min(100.0, self.clog_percentage + (clog_rate * 5.0))
        self.health = max(0.0, 1.0 - (self.clog_percentage / 100.0))
        return {"clog_percentage": round(self.clog_percentage, 1)}

# --- SESSION STATE ---
if 'twin' not in st.session_state:
    st.session_state.twin = {
        'recoater': RecoaterBlade(),
        'heater': HeatingElement(),
        'nozzle': NozzlePlate(),
        'history': []
    }

# --- SIDEBAR ---
with st.sidebar:
    st.header("Parameter Configuration")

    temp_input = st.slider("Operating Temperature (°C)", 10.0, 60.0, 25.0, key="temp")
    contam_input = st.slider("Contamination Coefficient", 0.0, 1.0, 0.2, key="contam")
    load_input = st.number_input("Duty Cycle Load (Hours)", 1.0, 500.0, 100.0, key="load")
    maint_input = st.select_slider(
        "Maintenance Fidelity",
        options=[0.0, 0.5, 1.0],
        value=1.0,
        key="maint"
    )

    if st.button("Commit Cycle Update ⏩", use_container_width=True):
        twin = st.session_state.twin

        m_rec = twin['recoater'].update(load_input, contam_input, maint_input)
        m_heat = twin['heater'].update(load_input, temp_input, maint_input)
        m_noz = twin['nozzle'].update(load_input, contam_input, temp_input, maint_input, twin['recoater'].health)

        twin['history'].append({
            "Cycle": len(twin['history']) + 1,
            "Recoater_Health": twin['recoater'].health,
            "Heater_Health": twin['heater'].health,
            "Nozzle_Health": twin['nozzle'].health,
            "Thickness": m_rec["thickness_mm"],
            "Resistance": m_heat["resistance_ohms"],
            "Clog": m_noz["clog_percentage"]
        })

    if st.button("System Reset 🔄", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN UI ---
st.title("MetalJet Digital Twin")
tab1, tab2 = st.tabs(["📊 System Telemetry", "🤖 AI Diagnostic Assistant"])

# --- TAB 1 ---
with tab1:
    st.subheader("Reliability Trend Analysis")

    if st.session_state.twin['history']:
        df = pd.DataFrame(st.session_state.twin['history']).set_index("Cycle")
        st.line_chart(df[["Recoater_Health", "Heater_Health", "Nozzle_Health"]])
        st.dataframe(df.tail(5))
    else:
        st.info("Awaiting telemetry...")

# --- GEMINI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key not found. Please set it in .streamlit/secrets.toml")
else:
    genai.configure(api_key=api_key)
    # CHANGE THIS LINE: From 'gemini-1.5-flash' to 'gemini-2.5-flash'
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- TAB 2 ---
with tab2:
    st.subheader("AI Diagnostic Assistant")

    if not st.session_state.twin['history']:
        st.warning("Run at least one cycle first.")
    else:
        current_data = st.session_state.twin['history'][-1]

        context_prompt = f"""
        Analyze this telemetry data:

        CURRENT:
        {json.dumps(current_data, indent=2)}

        HISTORY:
        {json.dumps(st.session_state.twin['history'][-5:], indent=2)}
        """

        user_query = st.text_input("Ask something about the system:", key="ai_input")

        if user_query:
            with st.spinner("Analyzing..."):
                try:
                    response = model.generate_content([context_prompt, user_query])
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")