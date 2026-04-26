# MetalJet Digital Twin Project
The MetalJet Digital Twin project is a comprehensive simulation-based platform designed to model and analyze the behavior of various components in a MetalJet system. The project utilizes a digital twin approach, combining simulation, data analysis, and artificial intelligence to provide insights into system performance, maintenance, and optimization. The platform is built using a range of technologies, including Streamlit, Pandas, Plotly, and Google's Generative AI library.

## Features
- **Simulation Engine**: A core simulation engine that models the behavior of various components and their interactions.
- **Data Visualization**: Interactive data visualization using Plotly charts to display component degradation and maintenance agent trade-off.
- **AI-Powered Diagnostic Assistance**: Integration with Google's Generative AI library to provide intelligent diagnostic assistance.
- **Scenario-Based Simulation**: Ability to run simulations based on predefined scenarios with specific parameters.
- **Component-Based Architecture**: A modular architecture that allows for easy addition or removal of components.
- **Configuration Management**: A centralized configuration file for easy modification of simulation settings and component parameters.

## Tech Stack
* Frontend: Streamlit
* Backend: Python
* Data Analysis: Pandas
* Data Visualization: Plotly
* AI Library: Google Generative AI
* Simulation Engine: Custom-built using Python
* Configuration Management: Python

## Installation
To install the project, follow these steps:
1. Clone the repository using `git clone`.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure the project by modifying the `config.py` file.

## Usage
1. Run the simulation using `python simulation.py`.
2. Visualize the results using `streamlit run app.py`.
3. Interact with the digital twin using the web-based interface.

## Project Structure
```markdown
MetalJet Digital Twin Project
├── app.py
├── engine.py
├── simulation.py
├── config.py
├── scenarios_config.py
├── components
│   ├── base_component.py
│   ├── recoater_blade.py
│   ├── heating_element.py
│   ├── nozzle_plate.py
│   ├── linear_guide.py
│   ├── recoater_motor.py
├── requirements.txt
└── README.md
```
