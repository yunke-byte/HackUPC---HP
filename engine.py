from components.recoater_blade import RecoaterBlade
from components.heating_element import HeatingElement
from components.nozzle_plate import NozzlePlate
from components.linear_guide import LinearGuide
from components.recoater_motor import RecoaterMotor

class MetalJetDigitalTwin:
    def __init__(self):
        self.recoater = RecoaterBlade()
        self.heater = HeatingElement()
        self.nozzle = NozzlePlate()
        self.rail = LinearGuide()      # NOU
        self.motor = RecoaterMotor()   # NOU
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance, vibration):
        self.cycle_count += 1
        
        # 1. Update Rail primer (es veu afectat per la contaminació)
        metrics_rail = self.rail.update(load, humidity_contam, maintenance)
        
        # 2. Update Motor (es veu afectat per la salut del rail! Cascada!)
        metrics_motor = self.motor.update(load, temp_c, maintenance, self.rail.health)
        
        # 3. Update altres components
        metrics_recoater = self.recoater.update(load, humidity_contam, maintenance)
        metrics_heater = self.heater.update(load, temp_c, maintenance)
        metrics_nozzle = self.nozzle.update(load, humidity_contam, temp_c, maintenance, self.recoater.health)
        
        # 4. Construir Telemetria
# 4. Construir Telemetria
        return {
            "cycle": self.cycle_count,
            "components": {
                "LinearGuide": {  # <--- COMPROVA QUE AQUEST NOM ESTIGUI EXACTAMENT AIXÍ
                    "HealthIndex": round(self.rail.health, 3),
                    "OperationalStatus": self.rail.get_status(),
                    "Metrics": metrics_rail
                },
                "RecoaterMotor": { # <--- I AQUEST TAMBÉ
                    "HealthIndex": round(self.motor.health, 3),
                    "OperationalStatus": self.motor.get_status(),
                    "Metrics": metrics_motor
                },
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