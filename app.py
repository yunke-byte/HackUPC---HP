import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. WEBPAGE CONFIGURATION ---
st.set_page_config(page_title="MetalJet Digital Twin v1.2", layout="wide")
st.title("HP Metal Jet S100 - Digital Twin")

# --- 2. DATA LOADING ---
DATA_FOLDER = "output_data"

if not os.path.exists(DATA_FOLDER):
    st.error("'output_data' folder not found. Run 'python3 simulation.py 0'.")
    st.stop()

csv_files = sorted([f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')])
if not csv_files:
    st.warning("No .csv found. Run the simulation first.")
    st.stop()

with st.sidebar:
    st.header("Database")
    selected_file = st.selectbox("Select a scenario:", csv_files)

df = pd.read_csv(os.path.join(DATA_FOLDER, selected_file))

# --- 3. UIX ---
tab1, tab2 = st.tabs(["System telemetry", "AI assistant (Gemini)"])

with tab1:
    st.subheader(f"Scenario analysis: {selected_file}")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_health = go.Figure()
        for comp in ["LinearGuide", "RecoaterMotor","RecoaterBlade","HeatingElement", "NozzlePlate"]:
            fig_health.add_trace(go.Scatter(x=df['Cycle'], y=df[f'{comp}_Health'], mode='lines', name=comp))
        fig_health.update_layout(title="Component degradation", yaxis_title="Health (0 to 1)")
        st.plotly_chart(fig_health, use_container_width=True)

    with col2:
        fig_env = go.Figure()
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Maint'], name='Maintenance effort', line=dict(color='orange')))
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Load']/50, name='Relative operating load', line=dict(color='blue')))
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Temp']/50, name='Relative temperature', line=dict(color='red', dash='dot')))
        fig_env.update_layout(title="Maintenance Agent and OEE Trade-off", yaxis_title="Relative index")
        st.plotly_chart(fig_env, use_container_width=True)
        
    st.dataframe(df.tail(10), use_container_width=True)

# --- 4. GEMINI INTEGRATION ---
with tab2:
    st.subheader("Intelligent Diagnostic Assistant")
    
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.warning("Enter your Gemini API key in Streamlit secrets to activate the assistant.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        user_query = st.text_input("Ask the assistant about current data:")
        
        if user_query:
            with st.spinner("Analyzing telemetry..."):
                context_summary = df.describe().to_json()
                context_last_cycle = df.iloc[-1].to_json()
                prompt = f"""
                You are an expert Maintenance Engineer for HP Metal Jet systems.
                Here is a statistical summary of the current scenario: {context_summary}
                This is the system state immediately before failure or completion: {context_last_cycle}
                User Question: {user_query}
                Provide a technical, concise response using data points to justify your analysis.
                """
                try:
                    response = model.generate_content(prompt)
                    st.success("Analysis completed:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Connection error with Gemini: {e}")
