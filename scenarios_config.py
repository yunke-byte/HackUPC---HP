# Definició de tots els escenaris de prova
SCENARIOS = {
    1: {
        "name": "Normal (Laboratori)",
        "base_temp": 25.0,
        "base_contam": 0.1,
        "load_profile": 10.0,
        "chaos_enabled": False
    },
    2: {
        "name": "Entorn Brut (Calor+Pols)",
        "base_temp": 40.0,
        "base_contam": 0.8,
        "load_profile": 10.0,
        "chaos_enabled": False
    },
    3: {
        "name": "Sobreproducció 24/7",
        "base_temp": 28.0,
        "base_contam": 0.2,
        "load_profile": 50.0, # Càrrega multiplicada per 5
        "chaos_enabled": False
    },
    4: {
        "name": "Fred Extrem",
        "base_temp": 5.0,
        "base_contam": 0.1,
        "load_profile": 10.0,
        "chaos_enabled": False
    },
    5: {
        "name": "Caos (Shocks Aleatoris)",
        "base_temp": 25.0,
        "base_contam": 0.1,
        "load_profile": 10.0,
        "chaos_enabled": True # Activa l'enginyeria del caos
    }
}