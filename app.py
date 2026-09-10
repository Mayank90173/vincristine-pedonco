import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="VIPN Clinical Predictor", page_icon="🩺", layout="centered")

st.title("🩺 Vincristine-Induced Neurotoxicity Predictor")
st.write("### Low-Resource Setting Bedside Risk Calculator")
st.markdown("---")

st.write("This interactive clinical decision tool estimates the real-world probability of **Vincristine-Induced Peripheral Neurotoxicity (VIPN)**.")

# 2. Check if model file exists to prevent white-screen crashes
model_filename = 'vincristine_model.pkl'

if not os.path.exists(model_filename):
    st.error(f"⚠️ Critical Error: '{model_filename}' not found in the current directory! Please run the last cell of your Jupyter Notebook to generate this file first.")
    st.stop()

# 3. Load Model safely
@st.cache_resource
def load_predictive_engine():
    return joblib.load(model_filename)

try:
    saved_bundle = load_predictive_engine()
    clinical_model = saved_bundle['model']
except Exception as e:
    st.error(f"⚠️ System Failure: Could not load the model file. Error details: {e}")
    st.stop()

# 4. Sidebar Inputs
st.sidebar.header("📋 Patient Bedside Parameters")
age_input = st.sidebar.slider("Patient Age (Years)", min_value=0.0, max_value=18.0, value=6.0, step=0.5)
sex_input = st.sidebar.selectbox("Biological Sex", options=["Male", "Female", "Unknown"])
azole_input = st.sidebar.selectbox("Concomitant Azole Antifungals?", options=["No", "Yes"])

azole_flag = 1 if azole_input == "Yes" else 0
sex_male_flag = True if sex_input == "Male" else False
sex_unknown_flag = True if sex_input == "Unknown" else False

patient_vector = pd.DataFrame([{
    'Age_Years': age_input,
    'Concomitant_Azole': azole_flag,
    'Sex_Male': sex_male_flag,
    'Sex_Unknown': sex_unknown_flag
}])

# 5. Prediction Execution
st.subheader("📊 Algorithmic Risk Profile Assessment")

if st.button("⚡ Compute Patient VIPN Risk Score"):
    try:
        risk_probabilities = clinical_model.predict_proba(patient_vector)[0]
        # Extraction of the probability of class 1 (Toxicity)
        vipn_probability = risk_probabilities[1] * 100 
        
        if vipn_probability < 40.0:
            st.success(f"### Low Risk Stratum: {vipn_probability:.2f}% Probability")
            st.info("💡 Standard monitoring recommended.")
        elif 40.0 <= vipn_probability < 70.0:
            st.warning(f"### Moderate Risk Stratum: {vipn_probability:.2f}% Probability")
            st.info("💡 Escalate surveillance frequency.")
        else:
            st.error(f"### High Risk Stratum: {vipn_probability:.2f}% Probability")
            st.info("💡 High toxicity likelihood flagged. Alert clinical board.")
    except Exception as e:
        st.error(f"Calculation Error: {e}")

st.markdown("---")
st.caption("⚠️ **Research Disclaimer:** Open-source medical research prototype.")
