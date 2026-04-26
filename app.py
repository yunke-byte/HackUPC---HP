import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- 1. CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(page_title="MetalJet Digital Twin v1.2", layout="wide")
st.title("🖨️ HP Metal Jet S100 - Bessó Digital")

# --- 2. CÀRREGA DE DADES (Connexió amb Fase 2) ---
DATA_FOLDER = "output_data"

if not os.path.exists(DATA_FOLDER):
    st.error("❌ No s'ha trobat la carpeta 'output_data'. Executa 'python3 simulation.py 0' primer.")
    st.stop()

csv_files = sorted([f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')])
if not csv_files:
    st.warning("⚠️ No hi ha cap CSV. Executa la simulació primer.")
    st.stop()

with st.sidebar:
    st.header("📂 Base de Dades")
    selected_file = st.selectbox("Selecciona un Escenari:", csv_files)
    st.info("Aquestes dades provenen del motor de simulació híbrid (Física + IA) pre-calculat.")

# Llegim les dades generades pel simulation.py
df = pd.read_csv(os.path.join(DATA_FOLDER, selected_file))

# --- 3. INTERFÍCIE PRINCIPAL (TABS) ---
tab1, tab2 = st.tabs(["📊 Telemetria del Sistema", "🤖 Assistent IA (Gemini)"])

with tab1:
    st.subheader(f"Anàlisi de l'escenari: {selected_file}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gràfic de Salut
        fig_health = go.Figure()
        for comp in ["Rail", "Motor", "Recoater", "Nozzle", "Heater"]:
            fig_health.add_trace(go.Scatter(x=df['Cycle'], y=df[f'{comp}_Health'], mode='lines', name=comp))
        fig_health.update_layout(title="Degradació de Components", yaxis_title="Salut (0 a 1)")
        st.plotly_chart(fig_health, use_container_width=True)

    with col2:
        # Gràfic d'Entorn i OEE
        fig_env = go.Figure()
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Maint'], name='Esforç Manteniment', line=dict(color='orange')))
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Load']/50, name='Càrrega Operativa (Relativa)', line=dict(color='blue')))
        fig_env.add_trace(go.Scatter(x=df['Cycle'], y=df['Input_Temp']/50, name='Temperatura (Relativa)', line=dict(color='red', dash='dot')))
        fig_env.update_layout(title="Agent de Manteniment i OEE (Trade-off)", yaxis_title="Índex Relatiu")
        st.plotly_chart(fig_env, use_container_width=True)
        
    st.dataframe(df.tail(10), use_container_width=True)

# --- 4. INTEGRACIÓ AMB GEMINI ---
with tab2:
    st.subheader("Assistent de Diagnòstic Intel·ligent")
    
    # Intentem carregar la clau de forma segura
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.warning("Introdueix la teva clau de Gemini als secrets de Streamlit per activar l'assistent.")
    else:
        genai.configure(api_key=api_key)
        # Utilitzem un model actualitzat per a tasques generals de text
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        user_query = st.text_input("Fes una pregunta a l'assistent sobre les dades actuals:")
        
        if user_query:
            with st.spinner("L'assistent està analitzant la telemetria..."):
                # Li passem a Gemini un resum estadístic de les dades + l'últim cicle
                context_resum = df.describe().to_json()
                context_ultim_cicle = df.iloc[-1].to_json()
                
                prompt = f"""
                Ets un enginyer expert en manteniment predictiu de HP Metal Jet.
                Aquí tens un resum estadístic de l'escenari actual: {context_resum}
                Aquest és l'estat del sistema just abans de fallar o acabar: {context_ultim_cicle}
                
                Pregunta de l'usuari: {user_query}
                Respon de forma tècnica, concisa i utilitzant dades per justificar-ho.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("Anàlisi completat:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error de connexió amb Gemini: {e}")