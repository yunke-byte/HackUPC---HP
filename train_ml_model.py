import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def generate_training_data(samples=10000):
    print("Generant dades físiques d'entrenament...")
    np.random.seed(42)
    
    # Generem condicions aleatòries d'entorn
    load = np.random.uniform(5, 50, samples)
    contam = np.random.uniform(0.0, 1.0, samples)
    maint = np.random.uniform(0.0, 1.0, samples)
    vib = np.random.uniform(0.0, 1.0, samples)
    temp = np.random.uniform(15.0, 45.0, samples)
    
    # FÓRMULA NO LINEAL SECRETA (El que l'ML haurà de descobrir)
    # Imaginem que la física real fa que la vibració i la contaminació interactuïn de forma exponencial,
    # i que la temperatura només afecti si passa de 35 graus.
    
    wear_rate = np.zeros(samples)
    for i in range(samples):
        base_wear = (load[i] * 0.0001)
        
        # Sinergia destructiva: Si hi ha pols I vibració juntes, el desgast es multiplica x5
        contam_vib_synergy = (contam[i] * vib[i]) * 0.002
        
        # Efecte temperatura no lineal
        temp_stress = 0.001 * (temp[i] - 35)**2 if temp[i] > 35 else 0.0
        
        # El manteniment ho redueix tot
        maint_factor = 2.0 - maint[i]
        
        wear_rate[i] = (base_wear + contam_vib_synergy + temp_stress) * maint_factor
        wear_rate[i] += np.random.normal(0, 0.00005) # Soroll aleatori inevitable dels sensors
        wear_rate[i] = max(0.0, wear_rate[i])

    df = pd.DataFrame({
        'Load': load, 'Contamination': contam, 'Maintenance': maint, 
        'Vibration': vib, 'Temperature': temp, 'WearRate': wear_rate
    })
    return df

# 1. Obtenir Dades
df = generate_training_data()
X = df[['Load', 'Contamination', 'Maintenance', 'Vibration', 'Temperature']]
y = df['WearRate']

# 2. Entrenar Random Forest
print("Entrenant Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
model.fit(X, y)

# 3. Guardar el Model
os.makedirs("models", exist_ok=True)
model_path = "models/recoater_rf_model.pkl"
joblib.dump(model, model_path)
print(f"Model d'IA guardat correctament a {model_path}!")