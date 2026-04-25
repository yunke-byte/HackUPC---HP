import json
import pandas as pd
from engine import MetalJetDigitalTwin

def run_simulation(total_cycles=5):
    engine = MetalJetDigitalTwin()
    historian = []
    
    print(f"🚀 Iniciant simulació de {total_cycles} cicles...\n")
    
    for cycle in range(1, total_cycles + 1):
        current_temp = 35.0
        current_contam = 0.8
        current_load = 100.0
        current_maint = 0.2
        
        report = engine.step_simulation(
            temp_c=current_temp, 
            humidity_contam=current_contam, 
            load=current_load, 
            maintenance=current_maint
        )
        
        # Afegim les noves dades a l'historial
        historian.append({
            "Cycle": report["cycle"],
            "Input_Temp": current_temp,
            "Input_Contam": current_contam,
            
            "Rail_Health": report["components"]["LinearGuide"]["HealthIndex"],
            "Rail_Status": report["components"]["LinearGuide"]["OperationalStatus"],
            
            "Motor_Health": report["components"]["RecoaterMotor"]["HealthIndex"],
            "Motor_Status": report["components"]["RecoaterMotor"]["OperationalStatus"],
            
            "Recoater_Health": report["components"]["RecoaterBlade"]["HealthIndex"],
            "Recoater_Status": report["components"]["RecoaterBlade"]["OperationalStatus"],
            
            "Nozzle_Health": report["components"]["NozzlePlate"]["HealthIndex"],
            "Nozzle_Status": report["components"]["NozzlePlate"]["OperationalStatus"],
            
            "Heater_Health": report["components"]["HeatingElement"]["HealthIndex"],
            "Heater_Status": report["components"]["HeatingElement"]["OperationalStatus"],
        })
        
        print(f"--- Cicle {cycle} Completat ---")
        # Pots descomentar això per veure el JSON sencer a la terminal, 
        # però si fas molts cicles embrutarà molt la pantalla.
        # print(json.dumps(report, indent=2))
        
    df = pd.DataFrame(historian)
    df.to_csv("simulation_historian.csv", index=False)
    print("\n Simulació guardada a 'simulation_historian.csv'")

if __name__ == "__main__":
    # Prova a posar 50 o 100 cicles per veure com cau la salut!
    run_simulation(total_cycles=100)