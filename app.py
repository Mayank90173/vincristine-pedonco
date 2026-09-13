import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# 1. PAGE ARCHITECTURE & CLINICAL INSTITUTIONAL THEME
# ==============================================================================
st.set_page_config(
    page_title="VIPN Precision Command Dashboard", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a365d; font-weight: 800; margin-bottom: 2px; }
    .sub-title { font-family: 'Arial', sans-serif; color: #2f855a; font-weight: 600; font-size: 1.15rem; margin-bottom: 20px; }
    .section-header { color: #2b6cb0; font-weight: 700; font-size: 1.25rem; margin-top: 25px; margin-bottom: 12px; border-left: 6px solid #319795; padding-left: 12px; }
    .ctcae-box { background-color: #fffaf0; border-left: 5px solid #dd6b20; padding: 12px; border-radius: 4px; margin-bottom: 8px; }
    .warning-box { background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #c53030; font-size: 0.95rem; }
    .pharm-report-box { background-color: #f7fafc; border: 1px solid #cbd5e0; padding: 15px; border-radius: 6px; margin-top: 10px; }
    .medicolegal-banner { background-color: #f0fdf4; border-left: 5px solid #16a34a; color: #166534; padding: 12px; border-radius: 4px; margin-bottom: 15px; font-size: 0.9rem; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🧠 Pediatric VIPN Clinical Intelligence Command Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced Quantitative Pharmacology Decision Support Engine for Low-Resource Bedside vs High-End Precision Neuro-Oncology</p>', unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# MEDICOLEGAL PROTECTION HUB (DR. MAYANK VIRMANI TRACK LOGIC)
# ==============================================================================
st.markdown('<div class="medicolegal-banner">🛡️ <b>MEDICOLEGAL DISCLAIMER:</b> This prototype computational model layer is developed by Dr. Mayank Virmani strictly for educational advancement, baseline learning evaluation tracking, and research validation benchmarking in digital health health systems. It does not constitute formal clinical medical advice or independent peer-reviewed dosing authorization. All treatment calibrations must be verified with active primary institutional oncology protocols.</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. SIDEBAR DEMOGRAPHICS & CRITICAL HEPATIC/RENAL LAB PANELS
# ==============================================================================
st.sidebar.markdown("### 🏥 Patient Demographics & Vitals")
patient_id = st.sidebar.text_input("Patient Registry ID", value="PED-VIPN-2026")
age = st.sidebar.slider("Age (Years)", min_value=1.0, max_value=18.0, value=6.5, step=0.1)
sex = st.sidebar.selectbox("Biological Sex", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", min_value=2.0, max_value=120.0, value=22.4, step=0.1)
height = st.sidebar.number_input("Height (cm)", min_value=40.0, max_value=220.0, value=115.0, step=0.5)

bsa_calc = math.sqrt((weight * height) / 3600.0)

st.sidebar.markdown("### 🧪 Organ Function Lab Metrics")
scr = st.sidebar.number_input("Serum Creatinine (mg/dL)", min_value=0.1, max_value=5.0, value=0.45, step=0.01)
alt = st.sidebar.number_input("ALT (SGPT) (U/L)", min_value=5, max_value=600, value=35, step=1)
ast = st.sidebar.number_input("AST (SGOT) (U/L)", min_value=5, max_value=600, value=38, step=1)
total_bilirubin = st.sidebar.number_input("Total Bilirubin (mg/dL)", min_value=0.1, max_value=15.0, value=0.6, step=0.1)

k_const = 0.70 if (sex == "Male" and age >= 13) else 0.55
crcl_calc = (k_const * height) / scr
de_ritis_ratio = ast / alt if alt > 0 else 0.0

standard_calculated_dose = bsa_calc * 1.5
guideline_baseline_dose = 2.0 if standard_calculated_dose > 2.0 else standard_calculated_dose

# ==============================================================================
# 3. MULTI-TIER MODALITY SELECTION WINDOW
# ==============================================================================
tier_selection = st.radio(
    "📊 Select Clinical Modality / Economic Screening Horizon",
    ["Standard Bedside / Low-Resource Tier (No Genetic Testing Afforded)", 
     "Advanced Multi-Omic / High-End Tier (Full Pharmacogenomic Panel Enabled)"]
)

col1, col2 = st.columns(2)

cyp_val, cep_val, abcb1_val, b12_val, malnutrition_val = 0, 0, 0, 0, 0
comorbidity_cmt = False
clinical_notes_string = ""

with col1:
    if "Low-Resource" in tier_selection:
        st.markdown('<div class="section-header">🥦 Diet, Nutrition & Comorbidity Phenotyping</div>', unsafe_allow_html=True)
        dietary_regimen = st.selectbox("Dietary Intake Profile (Nutritional Factor)", ["Balanced Whole Diet Enriched", "Vegetarian / Low Animal Protein", "Strict Vegan (No Cobalamin)"])
        malnutrition_profile = st.selectbox("Nutritional Stunting Profile", ["Normal Development", "Severe Acute Malnutrition (SAM / Muscle Wasting)"])
        vit_b12_status = st.selectbox("Vitamin B12 Serum Baseline Assessment", ["Normal Status (>200 pg/mL)", "Severe Vitamin B12 Deficiency (<200 pg/mL)"])
        comorbidity_cmt = st.checkbox("Inherited Peripheral Neuropathy History (CMT Disease Profile)")
        
        b12_val = 1 if "Severe" in vit_b12_status or "Strict Vegan" in dietary_regimen else 0
        malnutrition_val = 1 if "Severe Acute" in malnutrition_profile else 0
        clinical_notes_string = f"Dietary Matrix: {dietary_regimen} | B12 Status: {vit_b12_status}"
    else:
        st.markdown('<div class="section-header">🧬 High-End Pharmacogenomic (PGx) Variant Matrix</div>', unsafe_allow_html=True)
        cyp3a5 = st.selectbox("CYP3A5 Genotype Status (Clearance Kinetics)", ["Expressor (*1/*1 or *1/*3) - Normal", "Non-Expressor (*3/*3) - Severe Clearance Delay"])
        cep72 = st.selectbox("CEP72 Genotype Variant (rs924607 Susceptibility)", ["Wild Type / Heterozygous", "Homozygous Mutant (rs924607 TT) - Extreme Vulnerability"])
        abcb1 = st.selectbox("ABCB1 Transporter State (rs1045642 Efflux Capacity)", ["Wild Type (Normal Drug Pumping)", "Mutant Variant (TT) - Intracellular Accumulation Risk"])
        
        cyp_val = 1 if "Non-Expressor" in cyp3a5 else 0
        cep_val = 1 if "Homozygous Mutant" in cep72 else 0
        abcb1_val = 1 if "Mutant" in abcb1 else 0
        clinical_notes_string = f"PGx -> CYP3A5: {cyp3a5} | CEP72: {cep72}"

    st.markdown('<div class="section-header">💊 Treatment Protocol & DDI Sync</div>', unsafe_allow_html=True)
    cumulative_vcr_dose = st.slider("Current Cumulative Vincristine Exposure (mg/m²)", min_value=2.0, max_value=50.0, value=12.0, step=0.5)
    azole_coadmin = st.selectbox("Concomitant Azole Antifungal Deployment", ["None / Safe Alternative", "Active Azole Exposure (Voriconazole, Itraconazole, Fluconazole)"])
    radiation_involved = st.checkbox("Concurrent Localized / Cranio-Spinal Radiation Protocol active")
    azole_val = 1 if "Active" in azole_coadmin else 0
    rt_val = 1 if radiation_involved else 0

# ==============================================================================
# 4. CURRENT ACTIVE SYMPTOMS TRACKER (NCI-CTCAE v5.0 STANDARDS CHECKLIST)
# ==============================================================================
with col2:
    st.markdown('<div class="section-header">📋 Current Active Symptoms Tracker (NCI-CTCAE v5.0)</div>', unsafe_allow_html=True)
    s_paresthesia = st.checkbox("Paresthesia (Numbness, tingling, burning sensation in hands/feet)")
    s_reflexes = st.checkbox("Hyporeflexia / Loss of deep tendon reflexes (Ankle jerk absent)")
    s_footdrop = st.checkbox("Foot Drop / Altered motor gait velocity or dragging limbs")
    s_neuralgia = st.checkbox("Severe Autonomic Neuralgia / Debilitating jaw or abdominal pain")
    s_adl = st.selectbox("Impact on Daily Activities (ADL)", ["No Impact", "Minimal Impact (Can dress/feed self)", "Severe Impact (Assistance required for basic ADL)"])

    current_clinical_grade = 0
    if s_paresthesia or s_reflexes: current_clinical_grade = 1
    if s_neuralgia or (s_paresthesia and "Minimal" in s_adl): current_clinical_grade = 2
    if s_footdrop or "Severe" in s_adl: current_clinical_grade = 3
    
    st.markdown(f'<div class="ctcae-box">📈 <b>Computed Severity Status:</b> CTCAE v5.0 Grade {current_clinical_grade} Peripheral Neuropathy</div>', unsafe_allow_html=True)

# ==============================================================================
# 5. ALGORITHMIC RISK PREDICTION MODEL ENGINE
# ==============================================================================
log_odds_calc = -3.5 + (0.08 * age) + (0.06 * cumulative_vcr_dose) + (2.3 * azole_val) + (1.9 * rt_val)

if "Low-Resource" in tier_selection:
    log_odds_calc += (2.6 * b12_val) + (1.5 * malnutrition_val)
else:
    log_odds_calc += (1.4 * cyp_val) + (2.8 * cep_val) + (1.8 * abcb1_val)

if comorbidity_cmt: log_odds_calc += 5.0
if alt > 120 or ast > 120: log_odds_calc += 2.2
if total_bilirubin > 1.5: log_odds_calc += 2.5

predicted_toxicity_probability = (1 / (1 + np.exp(-log_odds_calc))) * 100

# ==============================================================================
# 6. OUTPUT VALIDATION PANEL & DOSING ENGINE INTERFACE
# ==============================================================================
st.markdown("---")
res_col1, res_col2, res_col3, res_col4 = st.columns(4)

with res_col1:
    st.metric(label="Calculated Patient BSA", value=f"{bsa_calc:.2f} m²")
with res_col2:
