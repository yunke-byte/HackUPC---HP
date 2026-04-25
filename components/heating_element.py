import math
import config
from .base_component import Component

class HeatingElement(Component):
    def __init__(self):
        super().__init__("Heating Element")
        
    def update(self, load, temp_celsius, maintenance):
        # Equació d'Arrhenius per a degradació tèrmica
        temp_kelvin = temp_celsius + config.KELVIN_OFFSET
        lambda_rate = config.HEATER_PRE_EXP_FACTOR * math.exp(-config.HEATER_ACTIVATION_ENERGY / temp_kelvin)
        
        maintenance_factor = config.MAINTENANCE_BASELINE - maintenance
        self.cumulative_stress += load * lambda_rate * maintenance_factor
        
        # Decaïment exponencial per a la salut
        self.health = math.exp(-self.cumulative_stress * config.HEATER_DECAY_RATE)
        self.health = max(0.0, min(1.0, self.health))
        
        # Càlcul de la mètrica (La resistència puja quan es degrada)
        resistance = config.HEATER_BASE_RESISTANCE + (config.HEATER_RESISTANCE_VAR * (1.0 - self.health))
        return {"resistance_ohms": round(resistance, 2)}