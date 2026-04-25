# FASE 1
from components.recoater_blade import RecoaterBlade
from components.heating_element import HeatingElement
from components.nozzle_plate import NozzlePlate

class MetalJetDigitalTwin:
    def __init__(self):
        self.recoater = RecoaterBlade()
        self.heater = HeatingElement()
        self.nozzle = NozzlePlate()
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance):
        self.cycle_count += 1
        
        # 1. Update components
        metrics_recoater = self.recoater.update(load, humidity_contam, maintenance)
        metrics_heater = self.heater.update(load, temp_c, maintenance)
        metrics_nozzle = self.nozzle.update(load, humidity_contam, temp_c, maintenance, self.recoater.health)
        
        # 2. Construir Telemetria
        return {
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