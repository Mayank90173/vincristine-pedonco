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

# Custom Institutional CSS styling for a Clinical Environment
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f8; }
    .main-title { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e3d59; font-weight: 700; margin-bottom: 5px; }
    .sub-title { font-family: 'Arial', sans-serif; color: #17b978; font-weight: 500; font-size: 1.25rem; margin-bottom: 25px; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #1e3d59; }
    .critical-card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🧪 Pediatric VIPN Quantitative Pharmacology & Multi-Omics Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced Bench-to-Bedside Decision Support Engine for Low-Resource Precision Neuro-Oncology</p>', unsafe_allow_html=True)
st.markdown("---")

st.info("ℹ️ **Deterministic Core Engine V2.1:** Utilizing standard Mosteller body parameters, real-time CPIC/DPWG dynamic drug clearance metrics, and phenotypic CTCAE v5.0 inputs without external diagnostic dependency loops.")

# Initialize Session State Audit Ledger Database if not present
if 'patient_audit_log' not in st.session_state:
    st.session_state['patient_audit_log'] = pd.DataFrame(columns=[
        'Timestamp', 'Patient_ID', 'Age_Y', 'BSA_m2', 'Bilirubin_mgdL', 
        'CYP3A5_Status', 'CEP72_Status', 'CTCAE_Grade', 'Standard_Dose_mg', 
        'Guideline_Dose_mg', 'Administered_Dose_mg', 'Toxicity_Risk_Pct', 'Override_Justification'
    ])

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
st.sidebar.caption("Low-resource proxies or direct molecular profiling variants")
cyp3a5_genotype = st.sidebar.selectbox(
    "CYP3A5 Genotype Status (Core Clearance)", 
    ["Poor Metabolizer (*3/*3) - Elevated Exposure Risk", 
     "Intermediate Metabolizer (*1/*3)", 
     "Extensive Metabolizer (*1/*1) - Standard Clearance", 
     "Unknown / Not Screened"]
)
cep72_genotype = st.sidebar.selectbox(
    "CEP72 Neurotoxicity Biomarker (rs924607)", 
    ["CC (High Pharmacodynamic Risk)", 
     "CT (Moderate Vulnerability)", 
     "TT (Wild Type / Standard Baseline)", 
     "Unknown / Genomic Profile Not Available"]
)

# ==============================================================================
# 3. CLINICAL PHENOTYPIC MONITORING & DOSING PARAMETERS
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 3. Real-World Clinical Labs & Phenotypic Neuro-Grading")
    
    with st.expander("🩸 Hepatic & Renal Metabolic Profiles", expanded=True):
        bilirubin = st.number_input("Total Serum Bilirubin (mg/dL)", min_value=0.1, max_value=15.0, value=0.7, step=0.1, help="Standard pediatric safety cap trigger above 1.5 mg/dL")
        alt_ast = st.number_input("Serum ALT / AST Transaminases (U/L)", min_value=5, max_value=800, value=38, step=1)
        crcl = st.number_input("Creatinine Clearance / CrCl (mL/min/1.73m²)", min_value=5.0, max_value=180.0, value=98.5, step=0.5)
    
    with st.expander("👟 VIPN Phenotypic Sensation Checklist (CTCAE v5.0 Metrics)", expanded=True):
        st.caption("Select observed toxic manifestation loops during physical examination:")
        tox_reflex = st.checkbox("Loss of Deep Tendon Reflexes (DTR) / Achilles Hyporeflexia")
        tox_footdrop = st.checkbox("Objective Motor Weakness / Early Foot Drop / Gait Disturbances")
        tox_pain = st.checkbox("Severe burning paresthesia / Distal neuropathic pain clusters")
        tox_constipation = st.checkbox("Severe autonomic constipation / Sub-acute paralytic ileus patterns")
    
    # Quantitative Phenotypic Grading Engine
    active_symptoms = sum([tox_reflex, tox_footdrop, tox_pain, tox_constipation])
    if active_symptoms == 0:
        clinical_grade = "Grade 0 (No Manifested Neurotoxicity)"
        grade_modifier = 1.0
    elif active_symptoms == 1:
        clinical_grade = "Grade 1 (Mild Paresthesia / Reflex Loss Only - No Loss of Function)"
        grade_modifier = 1.0
    elif active_symptoms == 2:
        clinical_grade = "Grade 2 (Moderate Pain / Altered Gait / Functional Interference)"
        grade_modifier = 0.50  # 50% Dose Reduction Mandatory across pediatric models
    else:
        clinical_grade = "Grade 3/4 (Severe Functional Deficit / Paralytic Ileus / Drop Foot)"
        grade_modifier = 0.00  # Strict Chemotherapy Clinical Hold Engine Triggered

    if grade_modifier == 1.0:
        st.success(f"**Phenotypic Target:** `{clinical_grade}`")
    elif grade_modifier == 0.5:
        st.warning(f"**Phenotypic Action Required:** `{clinical_grade}` → 50% Attenuation Active.")
    else:
        st.error(f"**🛑 CRITICAL HOLD ACTION:** `{clinical_grade}` → Immediate clinical suspension of micro-tubule inhibitors recommended.")

    st.markdown("---")
    st.markdown("### 💊 4. Chemotherapy Administration Profiles")
    prescribed_dose_per_m2 = st.number_input("Standard Prescribed Base Protocol Dose (mg/m²)", min_value=0.1, max_value=2.5, value=1.5, step=0.1)
    
    # Calculate baseline un-adjusted absolute dose
    calculated_absolute_dose = prescribed_dose_per_m2 * bsa
    
    actual_mg_administered = st.number_input("Target Absolute Dose to Administer (mg)", min_value=0.01, max_value=6.0, value=float(round(calculated_absolute_dose, 2)), step=0.01)
    cumulative_cycles = st.slider("Total Cumulative Treatment Cycles Received", min_value=1, max_value=24, value=4)
    cumulative_exposure = actual_mg_administered * cumulative_cycles

    # Strict Pediatric 2.0mg Absolute Cap Enforcement Alert Logic
    override_reason = "N/A"
    is_capped = False
    if actual_mg_administered > 2.0:
        is_capped = True
        st.error("🚨 ⚠️ **CRITICAL CAP BREACH:** Single Vincristine dose exceeds the mandatory 2.0 mg absolute safety ceiling for pediatric patients!")
        override_reason = st.text_input("🛑 **MANDATORY DOCUMENTATION:** Enter Explicit Clinical Justification / Manual Override Reason to continue:")
    
    st.markdown("#### 🔬 Concomitant Drug-Drug Interaction (DDI) Metrics")
    azole_selection = st.selectbox(
        "Concurrent Azole Antifungal Prophylaxis",
        options=["None", "Fluconazole (Weak/Moderate CYP3A4 Inhibitor)", "Voriconazole (Strong CYP3A4 Inhibitor)", "Itraconazole (Strong CYP3A4 Inhibitor)", "Posaconazole (Strong CYP3A4 Inhibitor)"]
    )

# ==============================================================================
# 4. QUANTITATIVE PHARMACOLOGY SIMULATION & OUTCOMES DATA ENGINE
# ==============================================================================
with col2:
    st.markdown("### 📊 5. Multi-Omic & Pharmacological Risk Simulation")
    
    # Interactive Trigger Button
    run_sim = st.button("⚡ Execute Live Evidence-Based Risk Evaluation")
    
    if run_sim:
        if is_capped and not override_reason:
            st.error("❌ **Execution Blocked:** Cannot compute validation logs or dose adjustments without explicit manual override justification string input.")
        else:
            with st.spinner("Processing pharmacokinetic clearance constants and patient data loops..."):
                # --------------------------------------------------------------
                # CLINICAL DETERMINISTIC RISK MODEL ARCHITECTURE
                # --------------------------------------------------------------
                base_prob = 12.5  # Core background toxicity frequency percentage
                
                # Age-dependent metric scaling
                age_factor = 2.2 if age > 9.5 else 1.0
                prob_calc = base_prob * age_factor
                
                # CYP3A4 Drug Interaction Scaling Constants
                cyp3a4_inhibition = 1.0
                ddi_class = "Category A: No Active DDI Mapped"
                if azole_selection == "Fluconazole (Weak/Moderate CYP3A4 Inhibitor)":
                    cyp3a4_inhibition = 1.45
                    ddi_class = "Category C: Monitor Chemotherapy Safety"
                elif azole_selection in ["Voriconazole (Strong CYP3A4 Inhibitor)", "Itraconazole (Strong CYP3A4 Inhibitor)", "Posaconazole (Strong CYP3A4 Inhibitor)"]:
                    cyp3a4_inhibition = 2.80
