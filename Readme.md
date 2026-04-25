Here is the raw Markdown code for your README.md file. You can copy and paste
this directly into your repository!

# 🖨️ HP Metal Jet S100 - Digital Twin Engine (Phase 1)

**A deterministic, mathematics-driven reliability engine for modeling the physical degradation of HP Metal Jet 3D Printers.**

## 🎯 Project Overview
This repository contains the Phase 1 deliverable for the HP Digital Twin Hackathon: **The Logic Engine**. 

Instead of relying on basic linear subtractions or arbitrary `if/else` statements, this engine is built on **standard reliability engineering mathematics**. It dynamically calculates the Cumulative Effective Stress ($t_{eff}$) of critical 3D printer subsystems based on real-world operational and environmental vectors.

## 🧠 The Mathematical Models

To accurately reflect the physics of the **Binder Jetting** process, we modeled three distinct components (one across each core subsystem), applying a specific failure mechanic to each:

### 1. Recoater Blade (Subsystem: Recoating System)
* **Failure Mechanic:** Abrasive Wear.
* **Mathematical Model:** **Weibull Distribution** ($e^{-(t_{eff} / \eta)^\beta}$). We utilize a shape parameter ($\beta = 1.5$) to accurately model wear-out over time. Environmental contamination acts as a stress multiplier.
* **Custom Metric:** Blade Thickness (mm).

### 2. Heating Element (Subsystem: Thermal Control)
* **Failure Mechanic:** Thermal Fatigue & Electrical Degradation.
* **Mathematical Model:** **Arrhenius Equation + Exponential Decay**. The degradation rate scales exponentially with environmental temperature deviations, mapping Kelvin temperature directly to electrical breakdown.
* **Custom Metric:** Electrical Resistance ($\Omega$).

### 3. Nozzle Plate (Subsystem: Printhead Array)
* **Failure Mechanic:** Clogging & Binder Curing.
* **Mathematical Model:** Linear Accumulation with **CASCADING FAILURES**.
* **Custom Metric:** Clog Percentage (%).

## ⚙️ Input Drivers & The Data Contract
The engine natively ingests four primary vectors per step, acting strictly deterministically (identical inputs yield identical outputs).

1. **Temperature Stress (°C):** Drives exponential thermal decay and binder curing.
2. **Humidity/Contamination (0.0 - 1.0):** Multiplies abrasive friction on moving parts.
3. **Operational Load (Hours):** Dictates the baseline accumulation of structural fatigue.
4. **Maintenance Level (0.0 - 1.0):** Acts as a dynamic dampening coefficient. High maintenance slows stress accumulation; neglect accelerates it by up to 80%.

The engine strictly adheres to the requested **Telemetry Data Contract**, outputting a nested JSON structure containing the `HealthIndex` (0.0 to 1.0), categorical `OperationalStatus` (FUNCTIONAL, DEGRADED, CRITICAL, FAILED), and physical `Metrics`.

## 🚀 Bonus Criteria Achieved
We specifically engineered the engine to hit the **Complexity & Innovation** hackathon rubrics:

* 🌟 **Cascading Failures:** Subsystems are not isolated. If the Recoater Blade drops below 60% health, it stops spreading powder evenly, creating "internal metal dust." This internal contamination is passed directly into the Nozzle Plate's model, drastically accelerating clogging. A failure in Subsystem A causes Subsystem B to fail.
* 🌟 **Systemic Interaction:** Every single input driver interacts mathematically with the components. Maintenance isn't just a flat health boost; it alters the fundamental derivative of the wear curves.

## 💻 How to Run

**Requirements:** Python 3.x (No external libraries required)

```bash
# Run the standalone engine to simulate a 5-step stress test
python twin_engine.py

Upon running, the console will output the telemetry JSON for 5 simulation cycles
under harsh environmental conditions (35°C ambient, high contamination, poor
maintenance) to demonstrate the cascading failure logic in action.


