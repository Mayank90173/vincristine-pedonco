import streamlit as st
import math
import pandas as pd
import io
from datetime import datetime

# ==============================================================================
# 1. PAGE ARCHITECTURE & SKIN CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="VIPN Quantitative Pharmacology Platform", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional styling rules
st.markdown("""
    <style>
    .main-title { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e3d59; font-weight: 700; margin-bottom: 5px; }
    .sub-title { font-family: 'Arial', sans-serif; color: #17b978; font-weight: 500; font-size: 1.25rem; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🧪 Pediatric VIPN Quantitative Pharmacology & Multi-Omics Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced Bench-to-Bedside Decision Support Engine for Low-Resource Precision Neuro-Oncology</p>', unsafe_allow_html=True)
st.markdown("---")

# Initialize Session State Audit Ledger Database if not present
if 'patient_audit_log' not in st.session_state:
    st.session_state['patient_audit_log'] = pd.DataFrame(columns=[
        'Timestamp', 'Patient_ID', 'Age_Y', 'BSA_m2', 'Bilirubin_mgdL', 
        'CYP3A5_Status', 'CEP72_Status', 'CTCAE_Grade', 'Standard_Dose_mg', 
        'Guideline_Dose_mg', 'Administered_Dose_mg', 'Toxicity_Risk_Pct', 'Override_Justification'
    ])

# Initialize processing triggers to enforce persistent UI states
if 'simulation_executed' not in st.session_state:
    st.session_state['simulation_executed'] = False
if 'final_risk' not in st.session_state:
    st.session_state['final_risk'] = 0.0
if 'guideline_dose_val' not in st.session_state:
    st.session_state['guideline_dose_val'] = 0.0
if 'hepatic_alert_str' not in st.session_state:
    st.session_state['hepatic_alert_str'] = ""
if 'ddi_class_str' not in st.session_state:
    st.session_state['ddi_class_str'] = ""
if 'full_report_text' not in st.session_state:
    st.session_state['full_report_text'] = ""

# ==============================================================================
# 2. SIDEBAR PARAMETER INPUT INTERFACE (DEMOGRAPHICS & PGx BIOMARKERS)
# ==============================================================================
st.sidebar.markdown("### 🔬 1. Patient Demographics & Biometrics")
patient_id = st.sidebar.text_input("Patient Unique Identifier / ID", value="PED-NEURO-098")
age = st.sidebar.slider("Patient Age (Years)", min_value=0.1, max_value=18.0, value=6.5, step=0.1)
sex = st.sidebar.selectbox("Biological Sex Assignment", ["Male", "Female", "Intersex/Unknown"])
weight = st.sidebar.number_input("Patient Weight (kg)", min_value=1.5, max_value=120.0, value=22.4, step=0.1)
height = st.sidebar.number_input("Patient Height (cm)", min_value=35.0, max_value=220.0, value=115.0, step=0.5)

# Calculate Body Surface Area (BSA) via Mosteller Formula
bsa = math.sqrt((weight * height) / 3600.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧬 2. Multi-Omic & Pharmacogenomic Panel")
cyp3a5_genotype = st.sidebar.selectbox(
    "CYP3A5 Genotype Status (Core Clearance)", 
    ["Extensive Metabolizer (*1/*1) - Standard Clearance",
     "Poor Metabolizer (*3/*3) - Elevated Exposure Risk", 
     "Intermediate Metabolizer (*1/*3)", 
     "Unknown / Not Screened"]
)
cep72_genotype = st.sidebar.selectbox(
    "CEP72 Neurotoxicity Biomarker (rs924607)", 
    ["CT (Moderate Vulnerability)",
     "CC (High Pharmacodynamic Risk)", 
     "TT (Wild Type / Standard Baseline)", 
     "Unknown"]
)

# ==============================================================================
# 3. CLINICAL PHENOTYPIC MONITORING & DOSING PARAMETERS
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 3. Real-World Clinical Labs & Phenotypic Neuro-Grading")
    
    with st.expander("🩸 Hepatic & Renal Metabolic Profiles", expanded=True):
        bilirubin = st.number_input("Total Serum Bilirubin (mg/dL)", min_value=0.1, max_value=15.0, value=3.9, step=0.1)
        alt_ast = st.number_input("Serum ALT / AST Transaminases (U/L)", min_value=5, max_value=800, value=381, step=1)
        crcl = st.number_input("Creatinine Clearance / CrCl (mL/min/1.73m²)", min_value=5.0, max_value=200.0, value=134.0, step=0.5)
    
    with st.expander("👟 VIPN Phenotypic Checklist (CTCAE v5.0 Metrics)", expanded=True):
        tox_reflex = st.checkbox("Loss of Deep Tendon Reflexes (DTR) / Achilles Hyporeflexia", value=True)
        tox_footdrop = st.checkbox("Objective Motor Weakness / Early Foot Drop / Gait Disturbances", value=True)
        tox_pain = st.checkbox("Severe burning paresthesia / Distal neuropathic pain clusters", value=False)
        tox_constipation = st.checkbox("Severe autonomic constipation / Paralytic ileus patterns", value=False)
    
    # Quantitative Phenotypic Grading Engine
    active_symptoms = sum([tox_reflex, tox_footdrop, tox_pain, tox_constipation])
    if active_symptoms == 0:
        clinical_grade = "Grade 0 (No Manifested Neurotoxicity)"
        grade_modifier = 1.0
    elif active_symptoms == 1:
        clinical_grade = "Grade 1 (Mild Paresthesia / Reflex Loss Only)"
        grade_modifier = 1.0
    elif active_symptoms == 2:
        clinical_grade = "Grade 2 (Moderate Pain / Altered Functional Gait)"
        grade_modifier = 0.50  
    else:
        clinical_grade = "Grade 3/4 (Severe Deficit / Hold Therapy Required)"
        grade_modifier = 0.00  

    st.warning(f"**Phenotypic Target Status:** `{clinical_grade}`")

    st.markdown("---")
    st.markdown("### 💊 4. Chemotherapy Administration Profiles")
    prescribed_dose_per_m2 = st.number_input("Standard Prescribed Base Protocol Dose (mg/m²)", min_value=0.1, max_value=2.5, value=1.5, step=0.1)
    
    calculated_absolute_dose = prescribed_dose_per_m2 * bsa
    actual_mg_administered = st.number_input("Target Absolute Dose to Administer (mg)", min_value=0.01, max_value=6.0, value=1.60, step=0.01)
    cumulative_cycles = st.slider("Total Cumulative Treatment Cycles Received", min_value=1, max_value=24, value=22)
    cumulative_exposure = actual_mg_administered * cumulative_cycles

    override_reason = "N/A"
    is_capped = False
    if actual_mg_administered > 2.0:
        is_capped = True
        st.error("🚨 ⚠️ **CRITICAL CAP BREACH:** Single Vincristine dose exceeds the mandatory 2.0 mg absolute safety ceiling!")
        override_reason = st.text_input("🛑 **MANDATORY DOCUMENTATION:** Enter Manual Override Reason to continue:")
    
    st.markdown("#### 🔬 Concomitant Drug-Drug Interaction (DDI) Metrics")
    azole_selection = st.selectbox(
        "Concurrent Azole Antifungal Prophylaxis",
        options=["Fluconazole (Weak/Moderate CYP3A4 Inhibitor)", "None", "Voriconazole (Strong CYP3A4 Inhibitor)", "Itraconazole (Strong CYP3A4 Inhibitor)", "Posaconazole (Strong CYP3A4 Inhibitor)"]
    )

# ==============================================================================
# 4. QUANTITATIVE PHARMACOLOGY SIMULATION & PERSISTENT RENDER
# ==============================================================================
with col2:
    st.markdown("### 📊 5. Multi-Omic & Pharmacological Risk Simulation")
    
    run_sim = st.button("⚡ Execute Live Evidence-Based Risk Evaluation")
    
    if run_sim:
        if is_capped and (not override_reason or override_reason == "N/A"):
            st.error("❌ **Execution Blocked:** Manual override justification string required.")
        else:
            # Mathematical Processing Architecture calculations
            base_prob = 12.5  
            age_factor = 2.2 if age > 9.5 else 1.0
            prob_calc = base_prob * age_factor
            
            cyp3a4_inhibition = 1.0
            ddi_class = "Category A: No Active DDI Mapped"
            if "Fluconazole" in azole_selection:
                cyp3a4_inhibition = 1.45
                ddi_class = "Category C: Monitor Chemotherapy Safety"
            elif azole_selection in ["Voriconazole (Strong CYP3A4 Inhibitor)", "Itraconazole (Strong CYP3A4 Inhibitor)", "Posaconazole (Strong CYP3A4 Inhibitor)"]:
                cyp3a4_inhibition = 2.80
                ddi_class = "Category X/D: Avoid Combination"
            
            cumulative_scalar = 1.0 + (max(0.0, cumulative_exposure - 3.5) * 0.18)
            
            omic_modifier = 1.0
            if "Poor Metabolizer" in cyp3a5_genotype: omic_modifier += 0.40
            if "CC" in cep72_genotype: omic_modifier += 0.60
            elif "CT" in cep72_genotype: omic_modifier += 0.25
            
            st.session_state['final_risk'] = min(prob_calc * cyp3a4_inhibition * cumulative_scalar * omic_modifier, 99.7)
            
            # Guideline Adjustments Engine Calculations
            g_dose = calculated_absolute_dose
            if "Fluconazole" not in azole_selection and azole_selection != "None":
                g_dose = g_dose * 0.50
            
            st.session_state['hepatic_alert_str'] = "Unadjusted (Normal Hepatic Metrics)"
            if bilirubin > 3.0:
                g_dose = g_dose * 0.25
                st.session_state['hepatic_alert_str'] = "Bilirubin > 3.0 mg/dL: Apply 75% Dose Reduction [NCCN Pathway]"
            elif bilirubin > 1.5:
                g_dose = g_dose * 0.50
                st.session_state['hepatic_alert_str'] = "Bilirubin 1.5 - 3.0 mg/dL: Apply 50% Dose Reduction [NCCN Pathway]"
            
            g_dose = g_dose * grade_modifier
            if g_dose > 2.0:
                g_dose = 2.0
                
            st.session_state['guideline_dose_val'] = g_dose
            st.session_state['ddi_class_str'] = ddi_class
            st.session_state['simulation_executed'] = True
            
