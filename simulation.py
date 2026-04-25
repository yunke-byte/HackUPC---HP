import sys
import random
import pandas as pd
from engine import MetalJetDigitalTwin
from scenarios_config import SCENARIOS

def run_scenario(scenario_id, config, total_cycles=150, use_dynamic_maintenance=True):
    # Fixem la llavor perquè sigui 100% determinista. 
    # Sumem l'ID de l'escenari perquè cada escenari tingui la seva pròpia variació constant.
    random.seed(254 + scenario_id) 
    
    engine = MetalJetDigitalTwin()
    historian = []
    
    print(f"\n🚀 Iniciant Escenari {scenario_id}: {config['name']} ({total_cycles} cicles)")
    
    # Valors inicials que aniran "caminant"
    current_temp = config['base_temp']
    current_contam = config['base_contam']
    
    for cycle in range(1, total_cycles + 1):
        # ---------------------------------------------------------
        # 1. DINÀMIQUES DE L'ENTORN (El Camí Aleatori)
        # ---------------------------------------------------------
        
        # A) Temperatura: Distribució Normal. Majoria de canvis entre -1 i 1. Màxim [-5, 5].
        delta_temp = random.gauss(mu=0.0, sigma=1.5) 
        delta_temp = max(-5.0, min(5.0, delta_temp)) # Tallem els extrems
        current_temp += delta_temp
        
        # Límits físics de la sala perquè no arribi a -100ºC o +100ºC a la llarga
        current_temp = max(10.0, min(current_temp, 50.0)) 
        
        # B) Manteniment Dinàmic (L'Agent)
        current_maint = 0.5 
        worst_health = min([
            engine.recoater.health, engine.heater.health, 
            engine.nozzle.health, engine.rail.health, engine.motor.health
        ])
        
        if use_dynamic_maintenance and worst_health < 0.80:
            health_gap = 0.80 - worst_health
            current_maint = min(1.0, current_maint + (health_gap * 1.5))
            if cycle % 15 == 0: 
                print(f"   🔧 [AGENT] Manteniment augmentat al {round(current_maint*100)}% (Salut: {round(worst_health*100)}%)")

        # C) Contaminació: Distribució Uniforme + Efecte Manteniment
        # Si el manteniment és alt (>0.5), la sala es neteja. Si és baix (<0.5), s'acumula pols.
        maint_impact = 0.5 - current_maint # Negatiu si es neteja, positiu si s'abandona
        delta_contam = random.uniform(-0.02, 0.02) + (maint_impact * 0.05)
        current_contam = max(0.0, min(1.0, current_contam + delta_contam))

        # D) NOU FACTOR: Vibració Mecànica (Bucle de feedback)
        # La vibració base és 0.1, però es dispara si el rail o el motor estan fallant.
        rail_penalty = (1.0 - engine.rail.health) * 0.4
        motor_penalty = (1.0 - engine.motor.health) * 0.4
        current_vibration = 0.1 + random.uniform(0, 0.05) + rail_penalty + motor_penalty
        current_vibration = min(1.0, current_vibration)

        current_load = config['load_profile']

        # ---------------------------------------------------------
        # 2. ACTUALITZACIÓ DEL BESSÓ DIGITAL
        # ---------------------------------------------------------
        # **ATENCIÓ:** Hauràs d'afegir 'vibration' al step_simulation del teu engine.py
        report = engine.step_simulation(
            temp_c=current_temp, 
            humidity_contam=current_contam, 
            load=current_load, 
            maintenance=current_maint,
            vibration=current_vibration # NOVA VARIABLE!
        )
        
        # ---------------------------------------------------------
        # 3. GUARDEM A L'HISTORIAL
        # ---------------------------------------------------------
        historian.append({
            "Scenario": config['name'],
            "Cycle": report["cycle"],
            "Input_Temp": round(current_temp, 2),
            "Input_Contam": round(current_contam, 2),
            "Input_Load": current_load,
            "Input_Maint": round(current_maint, 2),
            "Input_Vibration": round(current_vibration, 2),
            
            "Rail_Health": round(report["components"]["LinearGuide"]["HealthIndex"], 3),
            "Rail_Status": report["components"]["LinearGuide"]["OperationalStatus"],
            
            "Motor_Health": round(report["components"]["RecoaterMotor"]["HealthIndex"], 3),
            "Motor_Status": report["components"]["RecoaterMotor"]["OperationalStatus"],
            
            "Recoater_Health": round(report["components"]["RecoaterBlade"]["HealthIndex"], 3),
            "Recoater_Status": report["components"]["RecoaterBlade"]["OperationalStatus"],
            
            "Nozzle_Health": round(report["components"]["NozzlePlate"]["HealthIndex"], 3),
            "Nozzle_Status": report["components"]["NozzlePlate"]["OperationalStatus"],
            
            "Heater_Health": round(report["components"]["HeatingElement"]["HealthIndex"], 3),
            "Heater_Status": report["components"]["HeatingElement"]["OperationalStatus"],
        })
        
        # Comprovació de fallada
        statuses = [
            report["components"]["LinearGuide"]["OperationalStatus"],
            report["components"]["RecoaterMotor"]["OperationalStatus"],
            report["components"]["RecoaterBlade"]["OperationalStatus"],
            report["components"]["NozzlePlate"]["OperationalStatus"],
            report["components"]["HeatingElement"]["OperationalStatus"]
        ]
        if "FAILED" in statuses:
            print(f"   💥 FALLADA CRÍTICA al cicle {cycle}. Màquina aturada.")
            break
            
    return historian