import math

class Component:
    def __init__(self, name):
        self.name = name
        self.health = 1.0
        self.cumulative_stress = 0.0

    def get_status(self):
        if self.health >= 0.80: return "FUNCTIONAL"
        elif self.health >= 0.40: return "DEGRADED"
        elif self.health >= 0.10: return "CRITICAL"
        else: return "FAILED"

class RecoaterBlade(Component):
    def __init__(self):
        super().__init__("Recoater Blade")
        self.eta = 5000.0  # Characteristic life
        self.beta = 1.5    # Weibull shape parameter (wear-out)
        self.thickness_initial = 2.0 # mm
        
    def update(self, load, contamination, maintenance):
        # Stress accumulates faster with high contamination, slower with good maintenance
        stress_rate = load * (1.0 + (contamination * 2.5)) * (2.0 - maintenance)
        self.cumulative_stress += stress_rate
        
        # Weibull Distribution formula for Health
        self.health = math.exp(-math.pow(self.cumulative_stress / self.eta, self.beta))
        self.health = max(0.0, min(1.0, self.health))
        
        # Calculate metric
        current_thickness = 1.5 + (0.5 * self.health)
        return {"thickness_mm": round(current_thickness, 3)}

class HeatingElement(Component):
    def __init__(self):
        super().__init__("Heating Element")
        self.A = 0.05 # Pre-exponential factor
        self.Ea_R = 300.0 # Activation energy over Gas Constant (simplified)
        
    def update(self, load, temp_celsius, maintenance):
        # Arrhenius Equation for thermal degradation rate
        temp_kelvin = temp_celsius + 273.15
        lambda_rate = self.A * math.exp(-self.Ea_R / temp_kelvin)
        
        # Stress accumulation
        self.cumulative_stress += load * lambda_rate * (2.0 - maintenance)
        
        # Exponential Decay formula for Health
        self.health = math.exp(-self.cumulative_stress * 0.005)
        self.health = max(0.0, min(1.0, self.health))
        
        # Calculate metric (Resistance increases from 10 to 15 ohms)
        resistance = 10.0 + (5.0 * (1.0 - self.health))
        return {"resistance_ohms": round(resistance, 2)}

class NozzlePlate(Component):
    def __init__(self):
        super().__init__("Nozzle Plate")
        self.clog_percentage = 0.0
        
    def update(self, load, external_contamination, temp_celsius, maintenance, recoater_health):
        # CASCADING FAILURE LOGIC:
        # If the recoater blade is degrading (<60% health), it creates internal powder dust.
        internal_contamination = 0.0
        if recoater_health < 0.6:
            internal_contamination = (0.6 - recoater_health) * 2.0 
            
        total_contamination = external_contamination + internal_contamination
        
        # Temperature stress (optimal is ~25C, deviates cause binder to dry improperly)
        temp_stress = abs(temp_celsius - 25.0) * 0.01
        
        clog_rate = load * (total_contamination + temp_stress) * (2.0 - maintenance)
        self.clog_percentage += clog_rate * 5.0 # Scaling factor
        self.clog_percentage = min(100.0, self.clog_percentage)
        
        # Linear degradation model based on accumulated clog
        self.health = 1.0 - (self.clog_percentage / 100.0)
        self.health = max(0.0, min(1.0, self.health))
        
        return {"clog_percentage": round(self.clog_percentage, 1)}


class MetalJetDigitalTwin:
    def __init__(self):
        self.recoater = RecoaterBlade()
        self.heater = HeatingElement()
        self.nozzle = NozzlePlate()
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance):
        """
        Inputs:
        - temp_c: Ambient/Operating Temperature in Celsius
        - humidity_contam: Normalized 0.0 to 1.0 (0=Clean, 1=Dirty)
        - load: Print hours / cycles in this step
        - maintenance: Normalized 0.0 to 1.0 (0=Neglected, 1=Perfect care)
        """
        self.cycle_count += 1
        
        # 1. Update Recoater
        metrics_recoater = self.recoater.update(load, humidity_contam, maintenance)
        
        # 2. Update Heater
        metrics_heater = self.heater.update(load, temp_c, maintenance)
        
        # 3. Update Nozzle (Passes recoater.health to trigger Cascading Failures!)
        metrics_nozzle = self.nozzle.update(load, humidity_contam, temp_c, maintenance, self.recoater.health)
        
        # Assemble Telemetry Contract
        telemetry = {
            "cycle": self.cycle_count,
            "components": {
                "RecoaterBlade": {
                    "HealthIndex": round(self.recoater.health, 3),
                    "OperationalStatus": self.recoater.get_status(),
                    "Metrics": metrics_recoater
                },
                "HeatingElement": {
                    "HealthIndex": round(self.heater.health, 3),
                    "OperationalStatus": self.heater.get_status(),
                    "Metrics": metrics_heater
                },
                "NozzlePlate": {
                    "HealthIndex": round(self.nozzle.health, 3),
                    "OperationalStatus": self.nozzle.get_status(),
                    "Metrics": metrics_nozzle
                }
            }
        }
        return telemetry

# --- EXAMPLE USAGE & TESTING ---
if __name__ == "__main__":
    import json
    engine = MetalJetDigitalTwin()
    
    print("Running Digital Twin Engine for 5 iterations under harsh conditions...\n")
    for i in range(1, 6):
        # Harsh inputs: 35°C, high contamination (0.8), high load (100 hours), poor maintenance (0.2)
        report = engine.step_simulation(
            temp_c=35.0, 
            humidity_contam=0.8, 
            load=100.0, 
            maintenance=0.2
        )
        print(f"--- Step {i} ---")
        print(json.dumps(report, indent=2))