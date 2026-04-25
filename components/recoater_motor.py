import math
import config
from .base_component import Component

class RecoaterMotor(Component):
    def __init__(self):
        super().__init__("Recoater Drive Motor")
        
    def update(self, load, temp_celsius, maintenance, rail_health):
        # 1. Estrès Tèrmic (si fa molta calor, el motor refrigera malament)
        temp_stress = 1.0 + (max(0, temp_celsius - config.MOTOR_OPTIMAL_TEMP) * config.MOTOR_TEMP_STRESS_MULT)
        
        # 2. FALLADA EN CASCADA: Si el rail està malament (<80%), el motor pateix molt
        rail_penalty = 1.0
        if rail_health < config.HEALTH_FUNCTIONAL:
            # Com pitjor estigui el rail, més es multiplica l'esforç del motor
            rail_penalty = 1.0 + ((1.0 - rail_health) * config.MOTOR_RAIL_PENALTY_MULT)
            
        maintenance_factor = config.MAINTENANCE_BASELINE - maintenance
        
        # Estrès total que rep el motor en aquest cicle
        stress_rate = load * temp_stress * rail_penalty * maintenance_factor
        self.cumulative_stress += stress_rate
        
        # Distribució Weibull (típica per components mecànics rotatoris)
        weibull_pow = math.pow(self.cumulative_stress / config.MOTOR_ETA, config.MOTOR_BETA)
        self.health = math.exp(-weibull_pow)
        self.health = max(0.0, min(1.0, self.health))
        
        # Mètrica: Consum elèctric (Amperes). Un motor forçat gasta més llum.
        current_draw = config.MOTOR_BASE_CURRENT + (config.MOTOR_CURRENT_VAR * (1.0 - self.health))
        return {"current_draw_amps": round(current_draw, 2)}