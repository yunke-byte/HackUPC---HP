import math

# -------------------------
# Utility: Deterministic Noise
# -------------------------
def pseudo_noise(x):
    return (math.sin(x * 12.9898) * 43758.5453) % 1

# -------------------------
# Base Component
# -------------------------
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

# -------------------------
# Recoater Blade (Weibull + improved maintenance + noise)
# -------------------------
class RecoaterBlade(Component):
    def __init__(self):
        super().__init__("Recoater Blade")
        self.eta = 5000.0
        self.beta = 1.5
        self.thickness_initial = 2.0

    def update(self, load, contamination, maintenance):
        # Maintenance reduces contamination impact
        effective_contamination = contamination * (1.2 - 0.8 * maintenance)

        stress_rate = load * (1.0 + (effective_contamination * 2.5))

        # Add deterministic micro-variation
        noise = 0.95 + 0.1 * pseudo_noise(self.cumulative_stress + load)
        stress_rate *= noise

        self.cumulative_stress += stress_rate

        # Weibull degradation
        self.health = math.exp(-((self.cumulative_stress / self.eta) ** self.beta))
        self.health = max(0.0, min(1.0, self.health))

        # Realistic thickness decay
        current_thickness = self.thickness_initial * self.health
        return {"thickness_mm": round(current_thickness, 3)}

# -------------------------
# Heating Element (Arrhenius + feedback-ready)
# -------------------------
class HeatingElement(Component):
    def __init__(self):
        super().__init__("Heating Element")
        self.A = 0.05
        self.Ea_R = 300.0

    def update(self, load, temp_celsius, maintenance):
        temp_kelvin = temp_celsius + 273.15

        lambda_rate = self.A * math.exp(-self.Ea_R / temp_kelvin)

        # Nonlinear maintenance effect
        stress_multiplier = 1.0 + (1.0 - maintenance) ** 2

        stress = load * lambda_rate * stress_multiplier

        # Add deterministic noise
        noise = 0.97 + 0.06 * pseudo_noise(self.cumulative_stress + temp_celsius)
        stress *= noise

        self.cumulative_stress += stress

        # Exponential decay
        self.health = math.exp(-self.cumulative_stress * 0.005)
        self.health = max(0.0, min(1.0, self.health))

        # Resistance increases with degradation
        resistance = 10.0 + (5.0 * (1.0 - self.health))
        return {"resistance_ohms": round(resistance, 2)}

# -------------------------
# Nozzle Plate (Weibull + cascading + maintenance cleaning)
# -------------------------
class NozzlePlate(Component):
    def __init__(self):
        super().__init__("Nozzle Plate")
        self.clog_percentage = 0.0

    def update(self, load, external_contamination, temp_celsius, maintenance, recoater_health):
        # Cascading failure from recoater
        internal_contamination = 0.0
        if recoater_health < 0.6:
            internal_contamination = (0.6 - recoater_health) * 2.0

        total_contamination = external_contamination + internal_contamination

        # Temperature stress
        temp_stress = abs(temp_celsius - 25.0) * 0.01

        # Clog accumulation
        clog_rate = load * (total_contamination + temp_stress)

        noise = 0.95 + 0.1 * pseudo_noise(self.cumulative_stress + temp_celsius)
        clog_rate *= noise

        self.clog_percentage += clog_rate * 5.0

        # Maintenance cleaning effect
        self.clog_percentage *= (1.0 - 0.3 * maintenance)

        self.clog_percentage = min(100.0, self.clog_percentage)

        # Weibull-based failure probability
        lambda_factor = 50.0 / (1.0 + total_contamination + temp_stress)
        k = 2.0

        failure_prob = 1 - math.exp(-((self.clog_percentage / lambda_factor) ** k))
        self.health = 1.0 - failure_prob

        self.health = max(0.0, min(1.0, self.health))

        return {"clog_percentage": round(self.clog_percentage, 1)}

# -------------------------
# Digital Twin Engine
# -------------------------
class MetalJetDigitalTwin:
    def __init__(self):
        self.recoater = RecoaterBlade()
        self.heater = HeatingElement()
        self.nozzle = NozzlePlate()
        self.cycle_count = 0

    def step_simulation(self, temp_c, humidity_contam, load, maintenance):
        self.cycle_count += 1

        # 1. Update Recoater
        metrics_recoater = self.recoater.update(load, humidity_contam, maintenance)

        # 2. Update Heater
        metrics_heater = self.heater.update(load, temp_c, maintenance)

        # FEEDBACK LOOP: Heater degradation affects effective temperature
        effective_temp = temp_c + (1.0 - self.heater.health) * 10.0

        # 3. Update Nozzle with cascading + feedback
        metrics_nozzle = self.nozzle.update(
            load,
            humidity_contam,
            effective_temp,
            maintenance,
            self.recoater.health
        )

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

# -------------------------
# Example Run
# -------------------------
if __name__ == "__main__":
    import json

    engine = MetalJetDigitalTwin()

    print("Running Enhanced Digital Twin Engine...\n")

    for i in range(1, 6):
        report = engine.step_simulation(
            temp_c=35.0,
            humidity_contam=0.8,
            load=100.0,
            maintenance=0.2
        )

        print(f"--- Step {i} ---")
        print(json.dumps(report, indent=2))
