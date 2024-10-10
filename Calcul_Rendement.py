import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Calorific power in kJ/kg for each type of fuel
CALORIFIC_POWER = {
    "Gas": 35000,  # kJ/kg
    "LFO": 42000,  # kJ/kg
    "HFO": 40000   # kJ/kg
}

# Function to get enthalpy based on pressure
def get_enthalpy(pressure):
    enthalpy_values = {
        0: 0,
        1: 2676,
        2: 2794,
        3: 2827,
        4: 2850,
        5: 2765,
        6: 2800,
        7: 2810,
        8: 2830,
        9: 2850,
        10: 2793,
        11: 2900,
        12: 2920,
        13: 2950,
        14: 2980,
        15: 2930
    }
    return enthalpy_values.get(pressure, None)

# Function to adjust calorific power based on inlet water temperature
def adjust_calorific_power():
    return 1.3  # Always return the adjustment for 70°C

# Main function
def main():
    # Define labels in both languages
    labels = {
        "title": {
            "English": "Steam Boiler Efficiency Calculator",
            "Français": "Calculateur d'Efficacité de Chaudière à Vapeur"
        },
        "language_selection": {
            "English": "Select Language",
            "Français": "Sélectionner la langue"
        },
        "water_flow": {
            "English": "Makeup Water Flow (kg/h)",
            "Français": "Débit d'eau de makeup (kg/h)"
        },
        "steam_pressure": {
            "English": "Steam Pressure (bar)",
            "Français": "Pression de la vapeur (bar)"
        },
        "steam_flow": {
            "English": "Steam Output Flow (kg/h)",
            "Français": "Débit de vapeur sortante (kg/h)"
        },
        "fuel_type": {
            "English": "Fuel Type",
            "Français": "Type de combustible"
        },
        "gas_flow": {
            "English": "Gas Flow (m³/h)",
            "Français": "Débit de gaz (m³/h)"
        },
        "fuel_flow": {
            "English": "Fuel Flow (liters/h)",
            "Français": "Débit de combustible (litres/h)"
        },
        "results": {
            "English": "Results",
            "Français": "Résultats"
        },
        "energy_lost": {
            "English": "Energy Lost (during purge)",
            "Français": "Énergie perdue (pendant la purge)"
        },
        "contact_message": {
            "English": "To enhance your boiler's energy efficiency and achieve significant energy savings, I recommend consulting with a specialist in energy and boiler efficiency. They can provide valuable assistance in this area. Please reach out to Ramzi Ferjeni at Ramzi.Ferjeni@bosch.com for expert guidance.",
            "Français": "Pour améliorer l'efficacité énergétique de votre chaudière et réaliser des économies d'énergie significatives, je vous recommande de consulter un spécialiste en efficacité énergétique et en chaudières. Ils peuvent fournir une assistance précieuse dans ce domaine. Veuillez contacter Ramzi Ferjeni à Ramzi.Ferjeni@bosch.com pour des conseils d'expert."
        }
    }

    # Language selection on the left side
    language = st.sidebar.selectbox(labels["language_selection"]["English"], ["English", "Français"])

    # Set the current language
    lang = language if language in ["English", "Français"] else "English"

    st.title(labels["title"][lang])

    # User inputs
    water_flow = st.number_input(labels["water_flow"][lang], min_value=0.0)
    steam_pressure = st.slider(labels["steam_pressure"][lang], 0, 15, 1)
    steam_flow = st.number_input(labels["steam_flow"][lang], min_value=0.0)

    # Fuel type
    fuel_type = st.selectbox(labels["fuel_type"][lang], ["Gas", "LFO", "HFO"])

    # Input for fuel flow
    if fuel_type == "Gas":
        gas_flow_m3 = st.number_input(labels["gas_flow"][lang], min_value=0.0)
        fuel_flow = gas_flow_m3 * 0.717  # kg/h
        st.write(f"Converted Gas Flow: {gas_flow_m3:.2f} m³/h = {fuel_flow:.2f} kg/h")
    else:
        fuel_flow_liters = st.number_input(labels["fuel_flow"][lang], min_value=0.0)
        fuel_flow = fuel_flow_liters * 0.85  # kg/h

    # Calculate enthalpy
    enthalpy = get_enthalpy(steam_pressure)
    if enthalpy is None:
        st.error("Unsupported pressure / Pression non supportée.")
        return

    # Adjust calorific power based on makeup water temperature (fixed at 70°C)
    adjustment = adjust_calorific_power()
    calorific_power = CALORIFIC_POWER[fuel_type] * adjustment

    # Calculate the required fuel flow based on enthalpy
    required_fuel_flow = ((steam_flow * enthalpy) / calorific_power) if calorific_power > 0 else 0

    # Calculations
    total_energy_produced = (water_flow * enthalpy) if water_flow > 0 else 0
    energy_supplied = fuel_flow * calorific_power if fuel_flow > 0 else 0

    # Ensure calculations depend on adjusted values
    steam_water_efficiency = (steam_flow / water_flow) if water_flow > 0 else 0
    energy_fuel_efficiency = (total_energy_produced / energy_supplied) if energy_supplied > 0 else 0
    energy_produced = steam_flow * enthalpy if steam_flow > 0 else 0
    steam_fuel_efficiency = (energy_produced / energy_supplied) if energy_supplied > 0 else 0

    # Total boiler efficiency including purge
    total_efficiency_with_purge = (total_energy_produced / energy_supplied) * 100 if energy_supplied > 0 else 0

    # Boiler efficiency (purge not included)
    boiler_efficiency_without_purge = (energy_produced / energy_supplied) * 100 if energy_supplied > 0 else 0

    # Calculate purge rate
    purge_rate = (water_flow - steam_flow) / steam_flow if steam_flow > 0 else 0

    # Energy Lost (during purge)
    energy_lost_during_purge = total_efficiency_with_purge - boiler_efficiency_without_purge

    # Display results
    st.subheader(labels["results"][lang])
    st.write(f"Required fuel flow for {steam_flow} kg/h of steam: {required_fuel_flow:.2f} kg/h")
    st.write(f"Provided fuel flow: {fuel_flow:.2f} kg/h")
    st.write(f"{labels['energy_lost'][lang]}: {energy_lost_during_purge:.2f}%")

    # Check for incorrect efficiency
    efficiencies = {
        "Total Boiler Efficiency": total_efficiency_with_purge / 100,  # Convert to fraction
        "Boiler Efficiency (purge not included)": boiler_efficiency_without_purge / 100,  # Convert to fraction
    }

    # Create a DataFrame for better visualization
    df_efficiencies = pd.DataFrame(efficiencies.items(), columns=["Efficiency Type", "Value"])
    df_efficiencies["Value"] = df_efficiencies["Value"].apply(lambda x: f"{x:.2%}")  # Format as percentage
    st.table(df_efficiencies)

    # Plot pie charts in two columns
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))  # Create a 2x1 grid for pie charts

    for i, (efficiency_name, efficiency_value) in enumerate(efficiencies.items()):
        pie_data = [efficiency_value, 1 - efficiency_value]  # Efficiency and remaining
        axs[i].pie(pie_data, labels=[efficiency_name, 'Remaining'], autopct='%1.1f%%', startangle=90)
        axs[i].axis('equal')  # Equal aspect ratio ensures pie chart is circular
        axs[i].set_title(f'{efficiency_name} (%)')

    plt.tight_layout()  # Adjust layout to prevent overlap
    st.pyplot(fig)

    # Display message if total efficiency is below 90%
    if total_efficiency_with_purge < 90:
        st.warning(labels["contact_message"][lang])

if __name__ == "__main__":
    main()
    
