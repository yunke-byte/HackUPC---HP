import math
import config
from .base_component import Component

class RecoaterBlade(Component):
    def __init__(self):
        super().__init__("Recoater Blade")
        
    def update(self, load, contamination, maintenance):
        # El desgast s'accelera amb la contaminació i es frena amb el manteniment
        maintenance_factor = config.MAINTENANCE_BASELINE - maintenance
        contam_factor = 1.0 + (contamination * config.RECOATER_CONTAM_MULT)
        
        stress_rate = load * contam_factor * maintenance_factor
        self.cumulative_stress += stress_rate
        
        # Distribució de Weibull per a la salut
        weibull_pow = math.pow(self.cumulative_stress / config.RECOATER_ETA, config.RECOATER_BETA)
        self.health = math.exp(-weibull_pow)
        self.health = max(0.0, min(1.0, self.health))
        
        # Càlcul de la mètrica (Gruix de la fulla)
        current_thickness = config.RECOATER_THICKNESS_BASE + (config.RECOATER_THICKNESS_VAR * self.health)
        return {"thickness_mm": round(current_thickness, 3)}