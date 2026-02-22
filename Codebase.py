import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from CoolProp.CoolProp import PropsSI

# Page Layout
st.set_page_config(page_title="AD-HTC Power Cycle", layout="wide")

st.title("⚡ AD-HTC Fuel-Enhanced Gas Power Cycle")
st.markdown("---")

# --- UI/UX: INPUT PARAMETERS ---
st.sidebar.header("⚙️ Input Parameters")

# Gas Cycle Inputs (Brayton)
st.sidebar.subheader("Gas Cycle (Fluid: Air)")
P1 = st.sidebar.number_input("Inlet Pressure (P1) [Pa]", value=101325)
T1 = st.sidebar.number_input("Inlet Temp (T1) [K]", value=300)
PR = st.sidebar.slider("Pressure Ratio (r_p)", 1.2, 20.0, 10.0)
TIT = st.sidebar.number_input("Turbine Inlet Temp (TIT) [K]", value=1200)

# HTC Steam Cycle Inputs (Rankine-based)
st.sidebar.subheader("HTC Steam Cycle (Fluid: Water)")
P_low = st.sidebar.number_input("Condenser/Reactor Pressure [Pa]", value=100000)
P_high = st.sidebar.number_input("Boiler Pressure [Pa]", value=2000000)
T_steam = st.sidebar.number_input("Steam Temp [K]", value=550)

# --- SCHEMATIC DISPLAY ---
st.subheader("System Schematic")
try:
    # Make sure your image file is named 'schematic.png' in the same folder
    st.image("schematic.png", caption="AD-HTC Fuel-Enhanced Gas Power Cycle Schematic", use_container_width=True)
except:
    st.warning("⚠️ 'schematic.png' not found. Please place your screenshot in the folder and rename it.")

# --- THE 'ANALYZE' BUTTON ---
if st.button("🔍 Analyze Cycle"):
    col1, col2 = st.columns(2)
    
    try:
        # 1. GAS CYCLE CALCULATIONS (T-s)
        s1 = PropsSI('S', 'P', P1, 'T', T1, 'Air')
        h1 = PropsSI('H', 'P', P1, 'T', T1, 'Air')
        
        P2 = P1 * PR
        s2 = s1 
        T2 = PropsSI('T', 'P', P2, 'S', s2, 'Air')
        h2 = PropsSI('H', 'P', P2, 'S', s2, 'Air')
        
        P3 = P2
        s3 = PropsSI('S', 'P', P3, 'T', TIT, 'Air')
        h3 = PropsSI('H', 'P', P3, 'T', TIT, 'Air')
        
        P4 = P1
        s4 = s3
        T4 = PropsSI('T', 'P', P4, 'S', s4, 'Air')
        h4 = PropsSI('H', 'P', P4, 'S', s4, 'Air')

        w_comp = h2 - h1
        w_turb = h3 - h4
        q_in = h3 - h2
        thermal_eff = (w_turb - w_comp) / q_in if q_in != 0 else 0

        # 2. STEAM CYCLE CALCULATIONS (h-s)
        hA = PropsSI('H', 'P', P_low, 'Q', 0, 'Water')
        sA = PropsSI('S', 'P', P_low, 'Q', 0, 'Water')
        hB = PropsSI('H', 'P', P_high, 'T', T_steam, 'Water')
        sB = PropsSI('S', 'P', P_high, 'T', T_steam, 'Water')

        with col1:
            st.subheader("Gas Cycle: T-s Chart")
            fig1, ax1 = plt.subplots()
            ax1.plot([s1, s2, s3, s4, s1], [T1, T2, TIT, T4, T1], 'r-o', label='Gas Cycle Path')
            ax1.set_xlabel("Entropy (s) [J/kg·K]")
            ax1.set_ylabel("Temperature (T) [K]")
            ax1.legend()
            ax1.grid(True)
            st.pyplot(fig1)

        with col2:
            st.subheader("HTC Steam Cycle: h-s Chart")
            fig2, ax2 = plt.subplots()
            ax2.plot([sA, sB], [hA, hB], 'b-o', label='Boiler Process')
            ax2.set_xlabel("Entropy (s) [J/kg·K]")
            ax2.set_ylabel("Enthalpy (h) [J/kg]")
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

        st.success("✅ Analysis Complete.")
        
        st.subheader("📋 Performance Report")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        metrics_col1.metric("Thermal Efficiency", f"{round(thermal_eff * 100, 2)}%")
        metrics_col2.metric("Net Work Output", f"{round((w_turb - w_comp)/1000, 2)} kJ/kg")
        metrics_col3.metric("Heat Input (Gas)", f"{round(q_in/1000, 2)} kJ/kg")

    except Exception as e:
        error_msg = str(e)
        st.error("### ⚠️ Thermodynamic Limit Reached")
        
        # Translation of technical errors into human language
        if "out of range" in error_msg or "Tmax" in error_msg:
            st.warning("**The values you entered result in a state that doesn't exist in the model.**")
            st.write("""
                **Why?** You likely set the pressure too low while the temperature is high. 
                In physics, thin air at high heat exceeds the temperature limits ($3000\text{ K}$) of our simulation tables.
            """)
            st.info("💡 **Solution:** Set P1 to **101325 Pa** and TIT to **1100 K** to reset.")
        else:
            st.error(f"Something went wrong: {error_msg}")
            
        with st.expander("Show Technical Detail"):
            st.write(e)