import joblib
import warnings
import config
from .base_component import Component

# Ignorem els avisos molestos de scikit-learn
warnings.filterwarnings("ignore", category=UserWarning)

class RecoaterBlade(Component):
    def __init__(self):
        super().__init__("Recoater Blade")
        # CARREGUEM EL MODEL DE MACHINE LEARNING!
        try:
            self.ml_model = joblib.load("models/recoater_rf_model.pkl")
            self.uses_ml = True
        except FileNotFoundError:
            print("AVÍS: No s'ha trobat el model ML. Fes 'python train_ml_model.py' primer.")
            self.uses_ml = False
        
    def update(self, load, contamination, maintenance, vibration, temp_c):
        
        if self.get_status() == "FAILED":
            return {"thickness_mm": config.RECOATER_THICKNESS_BASE, "ml_prediction": False}

        if self.uses_ml:
            # Ordre exacte: Load, Contamination, Maintenance, Vibration, Temperature
            input_features = [[load, contamination, maintenance, vibration, temp_c]]
            predicted_wear = self.ml_model.predict(input_features)[0]
            self.health -= predicted_wear
        else:
            self.health -= (load * 0.001)

        self.health = max(0.0, min(1.0, self.health))
        
        current_thickness = config.RECOATER_THICKNESS_BASE + (config.RECOATER_THICKNESS_VAR * self.health)
        return {"thickness_mm": round(current_thickness, 3), "ml_prediction": self.uses_ml}