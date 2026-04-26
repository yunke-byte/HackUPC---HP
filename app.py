import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
import json
import google.generativeai as genai

# --- PAGE CONFIG ---
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
        else: return "FAILED"

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

# --- NEW COMPONENTS FROM SCENARIO ENGINE ---

class RailSystem(Component):
    def __init__(self):
        super().__init__("Rail System")
    def update(self, load, vibration, maintenance):
        # High vibration and low maintenance accelerate mechanical wear
        stress_rate = load * (1.0 + (vibration * 3.0)) * (2.0 - maintenance)
        self.cumulative_stress += stress_rate * 0.0001
        self.health = max(0.0, 1.0 - self.cumulative_stress)
        return {"wear_coefficient": round(self.cumulative_stress, 4)}

class Motor(Component):
    def __init__(self):
        super().__init__("Drive Motor")
    def update(self, load, temp_celsius, vibration, maintenance):
        # Thermal stress + mechanical vibration impact the motor windings
        thermal_impact = max(1.0, temp_celsius / 40.0)
        stress_rate = load * thermal_impact * (1.0 + vibration) * (2.0 - maintenance)
        self.cumulative_stress += stress_rate * 0.00005
        self.health = max(0.0, 1.0 - self.cumulative_stress)
        return {"efficiency": round(self.health * 100, 1)}

# --- UPDATED DIGITAL TWIN WRAPPER ---
class MetalJetDigitalTwin:
    def __init__(self):
        self.recoater = RecoaterBlade()
        self.heater = HeatingElement()
        self.nozzle = NozzlePlate()
        self.rail = RailSystem()
        self.motor = Motor()
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance, vibration=0.1):
        self.cycle_count += 1
        
        # Update each component
        m_rec = self.recoater.update(load, humidity_contam, maintenance)
        m_heat = self.heater.update(load, temp_c, maintenance)
        m_noz = self.nozzle.update(load, humidity_contam, temp_c, maintenance, self.recoater.health)
        m_rail = self.rail.update(load, vibration, maintenance)
        m_motor = self.motor.update(load, temp_c, vibration, maintenance)

        return {
            "cycle": self.cycle_count,
            "components": {
                "Recoater": {"HealthIndex": self.recoater.health, "OperationalStatus": self.recoater.get_status()},
                "Heater": {"HealthIndex": self.heater.health, "OperationalStatus": self.heater.get_status()},
                "Nozzle": {"HealthIndex": self.nozzle.health, "OperationalStatus": self.nozzle.get_status()},
                "Rail": {"HealthIndex": self.rail.health, "OperationalStatus": self.rail.get_status()},
                "Motor": {"HealthIndex": self.motor.health, "OperationalStatus": self.motor.get_status()}
            }
        }

# --- STREAMLIT UI INTEGRATION ---

if 'twin' not in st.session_state:
    st.session_state.twin = MetalJetDigitalTwin()
    st.session_state.history = []

with st.sidebar:
    st.header("Parameter Configuration")
    temp_input = st.slider("Temperature (°C)", 10.0, 60.0, 25.0)
    contam_input = st.slider("Contamination", 0.0, 1.0, 0.2)
    load_input = st.number_input("Duty Load (Hours)", 1.0, 500.0, 100.0)
    maint_input = st.select_slider("Maintenance", options=[0.0, 0.5, 1.0], value=1.0)
    vibration_input = st.slider("System Vibration", 0.0, 1.0, 0.1)

    if st.button("Commit Cycle Update ⏩"):
        report = st.session_state.twin.step_simulation(
            temp_input, contam_input, load_input, maint_input, vibration_input
        )
        
        # Flatten for history
        entry = {"Cycle": report["cycle"]}
        for name, data in report["components"].items():
            entry[f"{name}_Health"] = data["HealthIndex"]
        st.session_state.history.append(entry)

# --- TAB VIEW ---
tab1, tab2 = st.tabs(["📊 System Telemetry", "🤖 AI Diagnostic Assistant"])

with tab1:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history).set_index("Cycle")
        st.line_chart(df)
        st.dataframe(df.tail(5))
    else:
        st.info("Awaiting telemetry data...")

# --- GEMINI SETUP ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

with tab2:
    st.subheader("AI Diagnostic Assistant")
    if not st.session_state.history:
        st.warning("Run at least one cycle first.")
    else:
        user_query = st.text_input("Ask about the new Rail or Motor systems:")
        if user_query:
            context = f"Latest Data: {json.dumps(st.session_state.history[-1])}"
            response = model.generate_content([context, user_query])
            st.write(response.text)