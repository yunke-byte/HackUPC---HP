import sys
import os
import random
import pandas as pd
from engine import MetalJetDigitalTwin
from scenarios_config import SCENARIOS

def run_scenario(scenario_id, config, total_cycles=200, use_dynamic_maintenance=True):
    random.seed(254 + scenario_id)
    engine = MetalJetDigitalTwin()
    historian = []
    
    current_temp = config['base_temp']
    current_contam = config['base_contam']
    
    for cycle in range(1, total_cycles + 1):
        # 1. Dinamiques ambientals (Mean Reversion cap a 20 graus)
        thermal_inertia = (config['base_temp'] - current_temp) * 0.15
        current_temp += random.gauss(0.0, 1.0) + thermal_inertia
        current_temp = max(10.0, min(current_temp, 50.0))
        
        if config['chaos_enabled'] and random.random() < 0.03:
            current_temp += 15.0
            current_contam = min(1.0, current_contam + 0.5)

        # 2. Agent de manteniment proporcional
        current_maint = 0.5
        worst_health = min([
            engine.recoater.health, engine.heater.health, 
            engine.nozzle.health, engine.rail.health, engine.motor.health
        ])
        
        if use_dynamic_maintenance and worst_health < 0.80:
            maintenance_demand = 0.80 - worst_health
            current_maint = min(0.90, 0.5 + (maintenance_demand * 1.2))

        # 3. Ajust de càrrega (OEE Trade-off)
        # Es redueix la càrrega proporcionalment al manteniment realitzat
        load_variance = random.uniform(0.85, 1.15)
        theoretical_load = config['load_profile'] * load_variance
        
        if current_maint > 0.5:
            downtime_ratio = (current_maint - 0.5) * 2.0
            current_load = theoretical_load * (1.0 - downtime_ratio)
        else:
            current_load = theoretical_load
        current_load = max(0.0, current_load)

        # 4. Feedback de vibracio i contaminacio
        maint_efficiency = current_maint - 0.5
        current_contam = max(0.0, min(1.0, current_contam + random.uniform(-0.02, 0.02) - (maint_efficiency * 0.1)))
        
        vibration_base = 0.1
        rail_impact = (1.0 - engine.rail.health) * 0.5
        vibration_feedback = vibration_base + rail_impact + random.uniform(0, 0.02)
        current_vibration = min(1.0, vibration_feedback)

        # 5. Actualitzacio del model (Fase 1)
        report = engine.step_simulation(
            temp_c=current_temp, 
            humidity_contam=current_contam, 
            load=current_load, 
            maintenance=current_maint, 
            vibration=current_vibration
        )
        
        # 6. Captura de dades
        log_entry = {
            "Scenario": config['name'],
            "Cycle": report["cycle"],
            "Input_Temp": round(current_temp, 2),
            "Input_Contam": round(current_contam, 2),
            "Input_Load": round(current_load, 2),
            "Input_Maint": round(current_maint, 2),
            "Input_Vibration": round(current_vibration, 2)
        }
        
        for name, data in report["components"].items():
            log_entry[f"{name}_Health"] = data["HealthIndex"]
            log_entry[f"{name}_Status"] = data["OperationalStatus"]
            
        historian.append(log_entry)
        
        # Monitoritzacio de fallades per aturar la simulacio
        if any(c["OperationalStatus"] == "FAILED" for c in report["components"].values()):
            break
            
    return historian

def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    try:
        choice = int(sys.argv[1])
    except ValueError:
        sys.exit(1)

    os.makedirs("output_data", exist_ok=True)
    all_results = []

    if choice == 0:
        for sc_id, sc_config in SCENARIOS.items():
            all_results.extend(run_scenario(sc_id, sc_config))
        filename = "output_data/simulation_all_scenarios.csv"
    elif choice in SCENARIOS:
        all_results = run_scenario(choice, SCENARIOS[choice])
        filename = f"output_data/scenario_{choice}_results.csv"
    else:
        sys.exit(1)

    df = pd.DataFrame(all_results)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    main()