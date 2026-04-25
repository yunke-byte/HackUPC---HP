import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

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

# --- UI CONFIGURATION ---
st.set_page_config(page_title="MetalJet Digital Twin v1.0", layout="wide")

# Custom CSS for a more formal look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ MetalJet Digital Twin: Predictive Maintenance System")
st.caption("Industrial Monitoring & Reliability Simulation Engine")

# SESSION MANAGEMENT
if 'twin' not in st.session_state:
    st.session_state.twin = {
        'recoater': RecoaterBlade(),
        'heater': HeatingElement(),
        'nozzle': NozzlePlate(),
        'history': []
    }

# --- CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("Parameter Configuration")
    st.info("Adjust operating environmental variables below.")
    
    temp_input = st.slider("Operating Temperature (°C)", 10.0, 60.0, 25.0)
    contam_input = st.slider("Contamination Coefficient", 0.0, 1.0, 0.2, help="Includes humidity and airborne particulate levels.")
    load_input = st.number_input("Duty Cycle Load (Hours)", 1.0, 500.0, 100.0)
    maint_input = st.select_slider(
        "Maintenance Fidelity", 
        options=[0.0, 0.5, 1.0], 
        value=1.0,
        help="Efficiency of preventative maintenance tasks."
    )
    
    st.divider()
    if st.button("Commit Cycle Update ⏩", use_container_width=True, type="primary"):
        twin = st.session_state.twin
        m_rec = twin['recoater'].update(load_input, contam_input, maint_input)
        m_heat = twin['heater'].update(load_input, temp_input, maint_input)
        m_noz = twin['nozzle'].update(load_input, contam_input, temp_input, maint_input, twin['recoater'].health)
        
        twin['history'].append({
            "Cycle": len(twin['history']) + 1,
            "Recoater Health": twin['recoater'].health,
            "Heater Health": twin['heater'].health,
            "Nozzle Health": twin['nozzle'].health
        })
    
    if st.button("System Reset 🔄", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- ANALYTICS DASHBOARD ---
col1, col2, col3 = st.columns(3)

def create_gauge(val, name, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': name, 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "#f8d7da"},
                {'range': [40, 80], 'color': "#fff3cd"},
                {'range': [80, 100], 'color': "#d4edda"}
            ]
        }
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=20))
    return fig

with col1:
    st.plotly_chart(create_gauge(st.session_state.twin['recoater'].health, "Recoater Asset", "#1f77b4"), use_container_width=True)
    st.metric("Operational Status", st.session_state.twin['recoater'].get_status())

with col2:
    st.plotly_chart(create_gauge(st.session_state.twin['heater'].health, "Thermal System", "#ff7f0e"), use_container_width=True)
    st.metric("Operational Status", st.session_state.twin['heater'].get_status())

with col3:
    st.plotly_chart(create_gauge(st.session_state.twin['nozzle'].health, "Fluidics Plate", "#2ca02c"), use_container_width=True)
    st.metric("Operational Status", st.session_state.twin['nozzle'].get_status())

# --- TIME SERIES DATA ---
st.subheader("Reliability Trend Analysis")
if st.session_state.twin['history']:
    df = pd.DataFrame(st.session_state.twin['history']).set_index("Cycle")
    st.line_chart(df, height=300)
    
    # SYSTEM SUMMARY TABLE
    with st.expander("Detailed Telemetry Logs"):
        st.table(df.tail(5))
else:
    st.warning("Awaiting initial telemetry input. Please configure parameters and commit a cycle.")

# --- FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>MetalJet Digital Twin | Engineering Simulation Module | 2024</p>", unsafe_allow_html=True)