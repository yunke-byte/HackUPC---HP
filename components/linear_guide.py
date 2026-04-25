import math
import config
from .base_component import Component

class LinearGuide(Component):
    def __init__(self):
        super().__init__("Linear Guide Rail")
        
    def update(self, load, contamination, maintenance):
        # La contaminació és el pitjor enemic dels rails lineals
        contam_factor = 1.0 + (contamination * config.RAIL_CONTAM_MULT)
        maintenance_factor = config.MAINTENANCE_BASELINE - maintenance
        
        # El desgast (estrès) s'acumula
        stress_rate = load * contam_factor * maintenance_factor
        self.cumulative_stress += stress_rate
        
        # Model exponencial de degradació
        self.health = math.exp(-self.cumulative_stress * config.RAIL_DECAY_RATE)
        self.health = max(0.0, min(1.0, self.health))
        
        # Mètrica: Coeficient de fricció (puja a mesura que es degrada)
        friction = config.RAIL_BASE_FRICTION + (config.RAIL_FRICTION_VAR * (1.0 - self.health))
        return {"friction_coefficient": round(friction, 3)}