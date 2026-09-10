import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. Page Configuration & Layout
st.set_page_config(page_title="VIPN Quantitative Pharmacology Platform", page_icon="🧪", layout="wide")

st.title("🧪 Pediatric VIPN Quantitative Pharmacology Platform")
st.write("### Advanced Decision Support System for Low-Resource Neuro-Oncology")
st.markdown("---")

# Load baseline ML model architecture
try:
    saved_bundle = joblib.load('vincristine_model.pkl')
    clinical_model = saved_bundle['model']
except:
    st.error("Baseline engine missing. Ensure 'vincristine_model.pkl' is compiled.")
    st.stop()

# 2. Sidebar Input Form - Core Pharmacological Parameters
st.sidebar.header("🔬 Quantitative Variables")

st.sidebar.subheader("🔹 Patient Biometrics")
age = st.sidebar.slider("Patient Age (Years)", 0.0, 18.0, 6.0, 0.5)
sex = st.sidebar.selectbox("Biological Sex", ["Male", "Female", "Unknown"])
weight = st.sidebar.number_input("Patient Weight (kg)", min_value=2.0, max_value=100.0, value=20.0, step=0.5)
height = st.sidebar.number_input("Patient Height (cm)", min_value=40.0, max_value=200.0, value=110.0, step=1.0)

# Calculate BSA using Mosteller Formula (Standard in Pediatric Oncology)
bsa = np.sqrt((weight * height) / 3600)

st.sidebar.subheader("🔹 Vincristine Dosing Metrics")
prescribed_dose_per_m2 = st.sidebar.number_input("Prescribed Dose (mg/m²)", min_value=0.5, max_value=2.0, value=1.5, step=0.1)
actual_mg_administered = st.sidebar.number_input("Absolute Dose Administered (mg)", min_value=0.1, max_value=5.0, value=float(min(prescribed_dose_per_m2 * bsa, 2.0)), step=0.1)
cumulative_cycles = st.sidebar.slider("Total Chemotherapy Cycles Received", min_value=1, max_value=12, value=3)

# Calculating Cumulative Vincristine Exposure
cumulative_exposure = actual_mg_administered * cumulative_cycles

st.sidebar.subheader("🔹 CYP3A4/5 Enzyme Inhibitors")
azole_selection = st.sidebar.selectbox(
    "Concurrent Azole Antifungal",
    options=["None", "Fluconazole (Weak/Moderate)", "Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]
)

# 3. Processing Core Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Pharmacokinetic & Statistical Risk Modeling")
    
    # Map input parameters back to baseline ML architecture
    azole_binary = 1 if azole_selection != "None" else 0
    sex_male = True if sex == "Male" else False
    sex_unknown = True if sex == "Unknown" else False
    
    patient_vector = pd.DataFrame([{
        'Age_Years': age,
        'Concomitant_Azole': azole_binary,
        'Sex_Male': sex_male,
        'Sex_Unknown': sex_unknown
    }])
    
    if st.button("⚡ Run Quantitative Risk Simulation"):
        # Get baseline statistical risk from openFDA distribution
        baseline_prob = clinical_model.predict_proba(patient_vector)[0][1] * 100
        
        # Pharmacology Scaling Mechanics (Multiplying risk based on drug potency)
        cyp3a4_inhibition_factor = 1.0
        if azole_selection == "Fluconazole (Weak/Moderate)":
            cyp3a4_inhibition_factor = 1.4  # 40% increase in plasma exposure (AUC)
        elif azole_selection in ["Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]:
            cyp3a4_inhibition_factor = 2.2  # Over 2x systemic clearance restriction
            
        # Cumulative Dose Acceleration Factor
        # Risk accelerates after crossing 4.0mg total cumulative dose threshold
        cumulative_risk_scalar = 1.0 + (max(0.0, cumulative_exposure - 4.0) * 0.15)
        
        # Capping calculated mathematical risk logically at 98%
        final_pharmacological_risk = min(baseline_prob * cyp3a4_inhibition_factor * cumulative_risk_scalar, 98.0)
        
        # Display Results
        if final_pharmacological_risk < 40.0:
            st.success(f"### Low Risk Profile: {final_pharmacological_risk:.2f}% Probability")
        elif 40.0 <= final_pharmacological_risk < 75.0:
            st.warning(f"### Moderate Risk Profile: {final_pharmacological_risk:.2f}% Probability")
        else:
            st.error(f"### High Risk Profile: {final_pharmacological_risk:.2f}% Probability")
            
        # Operational Real-Time Biometric Feedback
        st.write(f"**Calculated Body Surface Area (BSA):** `{bsa:.2f} m²`")
        st.write(f"**Total Cumulative Vincristine Burden:** `{cumulative_exposure:.2f} mg`")
        
        # Check for Dosing Guideline Breaches
        if actual_mg_administered > 2.0:
            st.markdown("🚨 **CRITICAL WARNING:** Dose exceeds the universal pediatric safety cap of **2.0 mg per cycle**. Severe axonal degeneration risk is highly elevated.")

    st.markdown("---")
    st.subheader("🕵️‍♂️ Differential Diagnosis Protocol")
    st.write("Evaluate for at least **three distinct possibilities** before concluding symptoms are purely VIPN:")
    st.markdown("""
    *   **Vincristine-Induced Peripheral Neurotoxicity (VIPN):** Microtubule-mediated structural damage to sensory/motor axons.
    *   **Nutritional Axonopathy:** Folate or Vitamin B12 depletion exacerbated by low-resource dietary constraints or cachexia.
    *   **Critical Illness Polyneuropathy (CIPN):** Degeneration triggered by severe neutropenic sepsis and prolonged systemic stress.
    """)

with col2:
    st.subheader("📚 Molecular Pharmacology & Clinical Guidelines")
    
    with st.expander("🧬 CYP3A4 Enzyme Inhibition Mechanism"):
        st.write("""
        *   **Metabolic Pathway:** Vincristine is a substrate primarily cleared by hepatic cytochrome P450 **CYP3A4 and CYP3A5** enzymes.
        *   **Competitive Inhibition:** Concomitant Azoles bind competitively to the iron atom of the CYP3A4 heme group, blocking Vincristine clearance.
        *   **Systemic Accumulation:** This enzyme block increases the area under the curve (AUC) and plasma half-life of Vincristine, starving peripheral nerve axons of vital structural proteins by halting tubulin polymerization.
        """)
        
    with st.expander("📋 Evidence-Based Dosing Standards"):
        st.write("""
        *   **Pediatric Baseline:** Standard oncology protocols mandate **1.5 mg/m²** per dose.
        *   **Toxicity Ceiling:** To mitigate severe motor deficits (like foot drop or paralytic ileus), single doses must be **capped at a maximum of 2.0 mg**, irrespective of BSA calculation.
        """)
        
    st.subheader("💊 Alternative Non-Interacting Management Options")
    st.write("Consider these **three distinct treatment options** if toxicity thresholds are breached:")
    st.markdown("""
    1.  **Antimicrobial Switch (Non-Interacting Therapeutics):** Substitute the azole antifungal with **Liposomal Amphotericin B** or an echinocandin (e.g., **Caspofungin**), which bypass the hepatic CYP3A4 clearance pathway.
    2.  **Chemotherapy Dose Tailoring:** Apply a **25% to 50% dose modification** to subsequent Vincristine cycles or delay infusion until neuro-symptoms regress to baseline Grade 1.
    3.  **Neuro-Analgesic Intervention:** Introduce low-dose **Gabapentin or Pregabalin** to manage severe neuropathic pain or burning paresthesias, carefully adjusted for pediatric renal clearance.
    """)

st.markdown("---")
st.warning("⚠️ **General Medical Information Disclaimer:** This software provides general research benchmarking statistics. It is **NOT** a source of personalized medical advice. Clinicians must verify physical drug labels, check local protocols, and review comprehensive indicators before making treatment changes.")
