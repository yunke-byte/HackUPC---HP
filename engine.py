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
        self.rail = LinearGuide()
        self.motor = RecoaterMotor()
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance, vibration):
        self.cycle_count += 1
        
        m_rail = self.rail.update(load, humidity_contam, maintenance)
        m_motor = self.motor.update(load, temp_c, maintenance, self.rail.health)
        m_recoater = self.recoater.update(load, humidity_contam, maintenance, vibration, temp_c)
        m_heater = self.heater.update(load, temp_c, maintenance)
        m_nozzle = self.nozzle.update(load, humidity_contam, temp_c, maintenance, self.recoater.health, vibration)
        
        return {
            "cycle": self.cycle_count,
            "components": {
                "LinearGuide": {"HealthIndex": round(self.rail.health, 3), "OperationalStatus": self.rail.get_status(), "Metrics": m_rail},
                "RecoaterMotor": {"HealthIndex": round(self.motor.health, 3), "OperationalStatus": self.motor.get_status(), "Metrics": m_motor},
                "RecoaterBlade": {"HealthIndex": round(self.recoater.health, 3), "OperationalStatus": self.recoater.get_status(), "Metrics": m_recoater},
                "HeatingElement": {"HealthIndex": round(self.heater.health, 3), "OperationalStatus": self.heater.get_status(), "Metrics": m_heater},
                "NozzlePlate": {"HealthIndex": round(self.nozzle.health, 3), "OperationalStatus": self.nozzle.get_status(), "Metrics": m_nozzle}
            }
        }