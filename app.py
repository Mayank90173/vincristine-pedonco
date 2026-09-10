import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. Page Configuration and Medical Header Setup
st.set_page_config(page_title="VIPN Clinical Predictor", page_icon="🩺", layout="centered")

st.title("🩺 Vincristine-Induced Neurotoxicity Predictor")
st.write("### Low-Resource Setting Bedside Risk Calculator")
st.markdown("---")

st.write("This interactive clinical decision tool estimates the real-world probability of **Vincristine-Induced Peripheral Neurotoxicity (VIPN)** in pediatric oncology patients using readily available bedside demographics.")

# 2. Safe Model Ingestion Pipeline
@st.cache_resource
def load_predictive_engine():
    return joblib.load('vincristine_model.pkl')

try:
    saved_bundle = load_predictive_engine()
    clinical_model = saved_bundle['model']
    expected_features = saved_bundle['features']
except Exception as e:
    st.error("⚠️ System Failure: Could not ingest the predictive engine. Please verify that 'vincristine_model.pkl' is present in the workspace.")
    st.stop()

# 3. Patient Clinical Input Sidebar Form
st.sidebar.header("📋 Patient Bedside Parameters")

age_input = st.sidebar.slider("Patient Age (Years)", min_value=0.0, max_value=18.0, value=6.0, step=0.5)
sex_input = st.sidebar.selectbox("Biological Sex", options=["Male", "Female", "Unknown"])
azole_input = st.sidebar.selectbox("Concomitant Azole Antifungals? (e.g., Fluconazole)", options=["No", "Yes"])

# Mapping interactive input choices into machine learning format
azole_flag = 1 if azole_input == "Yes" else 0
sex_male_flag = True if sex_input == "Male" else False
sex_unknown_flag = True if sex_input == "Unknown" else False

# Packaging inputs into a structured dataframe matching the exact training columns
patient_vector = pd.DataFrame([{
    'Age_Years': age_input,
    'Concomitant_Azole': azole_flag,
    'Sex_Male': sex_male_flag,
    'Sex_Unknown': sex_unknown_flag
}])

# 4. Prediction Execution and Risk Stratification
st.subheader("📊 Algorithmic Risk Profile Assessment")

if st.button("⚡ Compute Patient VIPN Risk Score"):
    # Calculate the continuous probability score using the baseline logistic coefficients
    risk_probabilities = clinical_model.predict_proba(patient_vector)[0]
    vipn_probability = risk_probabilities[1] * 100  # Extract target event percentage
    
    # Stratifying safety bounds for resource-limited clinical action paths
    if vipn_probability < 40.0:
        st.success(f"### Low Risk Stratum: {vipn_probability:.2f}% Probability")
        st.info("💡 **Clinical Recommendation:** Maintain standard protocol surveillance and routinely evaluate deep tendon reflex markers according to standard institutional oncology workflows.")
    elif 40.0 <= vipn_probability < 70.0:
        st.warning(f"### Moderate Risk Stratum: {vipn_probability:.2f}% Probability")
        st.info("💡 **Clinical Recommendation:** Escalate monitoring frequency. Conduct close clinical screening for early fine-motor deficits, sensory paresthesia, or foot drop prior to subsequent cycles.")
    else:
        st.error(f"### High Risk Stratum: {vipn_probability:.2f}% Probability")
        st.info("💡 **Clinical Recommendation:** High toxicity likelihood flagged. Alert the pediatric oncology board to discuss potential chemotherapeutic dosage modulations, strict risk-benefit reviews, or alternative antimicrobial regimens to replace strong CYP3A4 inhibitors like azole antifungals.")

st.markdown("---")
st.caption("⚠️ **Global Health Research Disclaimer:** This platform serves as an open-source clinical research prototype designed exclusively for low-resource educational benchmarking and architectural validation. It does NOT constitute an approved diagnostic system and must never bypass the independent direct judgment of qualified medical practitioners.")
