import json
import pandas as pd
from engine import MetalJetDigitalTwin

def run_simulation(total_cycles=5):
    engine = MetalJetDigitalTwin()
    historian = []
    
    print(f"Iniciant simulació de {total_cycles} cicles...\n")
    
    for cycle in range(1, total_cycles + 1):
        # Aquí podríeu llegir aquests valors d'un CSV extern al futur!
        # Dades d'exemple: condicions dures.
        current_temp = 35.0
        current_contam = 0.8
        current_load = 100.0
        current_maint = 0.2
        
        # Cridem la Fase 1
        report = engine.step_simulation(
            temp_c=current_temp, 
            humidity_contam=current_contam, 
            load=current_load, 
            maintenance=current_maint
        )
        
        # Aplanem el diccionari per poder-lo guardar fàcilment a un CSV
        historian.append({
            "Cycle": report["cycle"],
            "Input_Temp": current_temp,
            "Input_Contam": current_contam,
            "Recoater_Health": report["components"]["RecoaterBlade"]["HealthIndex"],
            "Recoater_Status": report["components"]["RecoaterBlade"]["OperationalStatus"],
            "Nozzle_Health": report["components"]["NozzlePlate"]["HealthIndex"],
            "Nozzle_Status": report["components"]["NozzlePlate"]["OperationalStatus"],
            "Heater_Health": report["components"]["HeatingElement"]["HealthIndex"],
            "Heater_Status": report["components"]["HeatingElement"]["OperationalStatus"],
        })
        
        print(f"--- Cicle {cycle} Completat ---")
        print(json.dumps(report, indent=2))
        
    # Convertim a DataFrame i guardem per a la Fase 3
    df = pd.DataFrame(historian)
    df.to_csv("simulation_historian.csv", index=False)
    print("\n Simulació guardada a 'simulation_historian.csv'")

if __name__ == "__main__":
    run_simulation(total_cycles=5)