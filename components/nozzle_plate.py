import config
from .base_component import Component

class NozzlePlate(Component):
    def __init__(self):
        super().__init__("Nozzle Plate")
        self.clog_percentage = 0.0
        
    def update(self, load, external_contamination, temp_celsius, maintenance, recoater_health):
        # FALLADA EN CASCADA: El Recoater espatllat genera brutícia interna
        internal_contamination = 0.0
        if recoater_health < config.NOZZLE_CASCADING_THRESH:
            internal_contamination = (config.NOZZLE_CASCADING_THRESH - recoater_health) * config.NOZZLE_INTERNAL_CONTAM_MULT
            
        total_contamination = external_contamination + internal_contamination
        
        # Estrès per temperatura (desviació de l'òptim)
        temp_stress = abs(temp_celsius - config.NOZZLE_OPTIMAL_TEMP) * config.NOZZLE_TEMP_STRESS_MULT
        
        maintenance_factor = config.MAINTENANCE_BASELINE - maintenance
        clog_rate = load * (total_contamination + temp_stress) * maintenance_factor
        
        self.clog_percentage += clog_rate * config.NOZZLE_CLOG_SCALE
        self.clog_percentage = min(config.NOZZLE_MAX_CLOG, self.clog_percentage)
        
        # Model de degradació lineal basat en l'obstrucció
        self.health = 1.0 - (self.clog_percentage / config.NOZZLE_MAX_CLOG)
        self.health = max(0.0, min(1.0, self.health))
        
        return {"clog_percentage": round(self.clog_percentage, 1)}