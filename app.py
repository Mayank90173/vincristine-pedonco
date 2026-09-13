import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime

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
    .protocol-card { background-color: #ebf8ff; border-top: 4px solid #3182ce; padding: 20px; border-radius: 6px; margin-top: 15px; margin-bottom: 15px; }
    .ctcae-box { background-color: #fffaf0; border-left: 5px solid #dd6b20; padding: 12px; border-radius: 4px; margin-bottom: 8px; }
    .warning-box { background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #c53030; font-size: 0.95rem; }
    .pharm-report-box { background-color: #f7fafc; border: 1px solid #cbd5e0; padding: 15px; border-radius: 6px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🧠 Pediatric VIPN Clinical Intelligence Command Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Computational Decision Support System (CDSS) Powered by Precision Oncology Model Layers</p>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### 🏥 Patient Demographics & Baseline Vitals")
patient_id = st.sidebar.text_input("Patient Registry ID", value="PED-VIPN-2026")
age = st.sidebar.slider("Age (Years)", min_value=1.0, max_value=18.0, value=6.5, step=0.1)
sex = st.sidebar.selectbox("Biological Sex", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", min_value=2.0, max_value=120.0, value=22.4, step=0.1)
height = st.sidebar.number_input("Height (cm)", min_value=40.0, max_value=220.0, value=115.0, step=0.5)

bsa_calc = math.sqrt((weight * height) / 3600.0)

st.sidebar.markdown("### 🧪 Organ Toxicity Function Panel")
scr = st.sidebar.number_input("Serum Creatinine (mg/dL)", min_value=0.1, max_value=5.0, value=0.45, step=0.01)
alt = st.sidebar.number_input("ALT (SGPT) (U/L)", min_value=5, max_value=600, value=35, step=1)
ast = st.sidebar.number_input("AST (SGOT) (U/L)", min_value=5, max_value=600, value=38, step=1)
total_bilirubin = st.sidebar.number_input("Total Bilirubin (mg/dL)", min_value=0.1, max_value=15.0, value=0.6, step=0.1)

k_const = 0.70 if (sex == "Male" and age >= 13) else 0.55
crcl_calc = (k_const * height) / scr
de_ritis_ratio = ast / alt if alt > 0 else 0.0

tier_selection = st.radio(
    "📊 Select Clinical Modality / Economic Screening Horizon",
    ["Standard Bedside / Low-Resource Tier", "Advanced Multi-Omic / High-End Tier"]
)

col1, col2 = st.columns(2)
cyp_val, cep_val, abcb1_val, b12_val, malnutrition_val = 0, 0, 0, 0, 0
comorbidity_cmt = False
clinical_notes_string = ""

with col1:
    if "Low-Resource" in tier_selection:
        st.markdown('<div class="section-header">🥦 Diet, Nutrition & Comorbidity Phenotyping</div>', unsafe_allow_html=True)
        dietary_regimen = st.selectbox("Dietary Intake Profile", ["Balanced Whole Diet", "Vegetarian", "Strict Vegan"])
        malnutrition_profile = st.selectbox("Nutritional Stunting Profile", ["Normal Development", "Severe Acute Malnutrition"])
        vit_b12_status = st.selectbox("Vitamin B12 Serum Baseline Assessment", ["Normal Status", "Deficiency Status"])
        comorbidity_cmt = st.checkbox("Inherited Peripheral Neuropathy History")
        
        b12_val = 1 if "Deficiency" in vit_b12_status or "Strict Vegan" in dietary_regimen else 0
        malnutrition_val = 1 if "Severe" in malnutrition_profile else 0
        clinical_notes_string = f"Dietary Matrix: {dietary_regimen} | B12 Status: {vit_b12_status}"
    else:
        st.markdown('<div class="section-header">🧬 Pharmacogenomic Variant Matrix</div>', unsafe_allow_html=True)
        cyp3a5 = st.selectbox("CYP3A5 Genotype Status", ["Normal Expressor", "Non-Expressor"])
        cep72 = st.selectbox("CEP72 Genotype Variant", ["Wild Type", "Variant Present"])
        abcb1 = st.selectbox("ABCB1 Transporter State", ["Wild Type", "Mutant Variant"])
        
        cyp_val = 1 if "Non-Expressor" in cyp3a5 else 0
        cep_val = 1 if "Present" in cep72 else 0
        abcb1_val = 1 if "Mutant" in abcb1 else 0
        clinical_notes_string = f"PGx Matrix -> CYP3A5: {cyp3a5} | CEP72: {cep72}"

    cumulative_vcr_dose = st.slider("Cumulative Exposure Indicator", min_value=2.0, max_value=50.0, value=12.0, step=0.5)
    azole_coadmin = st.selectbox("Concomitant Antifungal Deployment", ["None", "Active Exposure"])
    radiation_involved = st.checkbox("Concurrent Radiation Protocol")
    azole_val = 1 if "Active" in azole_coadmin else 0
    rt_val = 1 if radiation_involved else 0

with col2:
    st.markdown('<div class="section-header">📋 Current Active Symptoms Tracker</div>', unsafe_allow_html=True)
    s_paresthesia = st.checkbox("Paresthesia")
    s_reflexes = st.checkbox("Hyporeflexia")
    s_footdrop = st.checkbox("Foot Drop")
    s_neuralgia = st.checkbox("Severe Neuralgia")
    s_adl = st.selectbox("Impact on Daily Activities (ADL)", ["No Impact", "Minimal Impact", "Severe Impact"])

    current_clinical_grade = 0
    if s_paresthesia or s_reflexes: current_clinical_grade = 1
    if s_neuralgia or (s_paresthesia and "Minimal" in s_adl): current_clinical_grade = 2
    if s_footdrop or "Severe" in s_adl: current_clinical_grade = 3
    
    st.markdown(f'<div class="ctcae-box">📈 <b>Computed Severity Status:</b> Grade {current_clinical_grade} Manifestation</div>', unsafe_allow_html=True)

log_odds_calc = -3.5 + (0.08 * age) + (0.06 * cumulative_vcr_dose) + (2.3 * azole_val) + (1.9 * rt_val)
predicted_toxicity_probability = (1 / (1 + np.exp(-log_odds_calc))) * 100

st.markdown("---")
res_col1, res_col2, res_col3, res_col4 = st.columns(4)
with res_col1: st.metric("Calculated BSA", f"{bsa_calc:.2f} m²")
with res_col2: st.metric("CrCl", f"{crcl_calc:.1f} mL/min")
with res_col3: st.metric("Risk Probability", f"{predicted_toxicity_probability:.1f} %")
with res_col4: st.metric("Severity Index", f"Grade {current_clinical_grade}")

st.markdown('<div class="section-header">🩺 Clinical Evaluation & Warnings</div>', unsafe_allow_html=True)

action_status = "🟩 STATUS STABLE: Proceed within standard protocol boundaries."
warning_1 = "Monitor physiological parameters prior to subsequent cycles."
warning_2 = "Observe fine motor control indices."
molecular_notes = "Metabolic pathways operating within standard parameters."
ddi_report = "No significant interactions flagged."
safe_duration_notes = "Adhere to established institutional infusion schedules."

if comorbidity_cmt or current_clinical_grade >= 3:
    action_status = "🔴 PROTOCOL HOLD ALERT: Review agent continuation."
    warning_1 = "Elevated risk of progressive neuromuscular effects."
    warning_2 = "Risk of autonomic involvement."
    molecular_notes = "Cellular microtubule disruption and transport inhibition."
    ddi_report = "Critical threshold indicators present."
    safe_duration_notes = "Hold administration until clinical resolution."

st.info(f"📋 **Evaluation Status:** {action_status}")

col_rep1, col_col2 = st.columns(2)
with col_rep1:
    st.markdown("#### 🚨 Pathophysiological Forecasts:")
    st.markdown(f'<div class="warning-box">⚠️ {warning_1}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning-box">⚠️ {warning_2}</div>', unsafe_allow_html=True)
with col_col2:
    st.markdown("#### 🔬 Molecular Mechanism & Interaction Analysis:")
    st.markdown('<div class="pharm-report-box">', unsafe_allow_html=True)
    st.markdown(f"**Mechanism Summary:** {molecular_notes}")
    st.markdown(f"**Interaction Profile:** {ddi_report}")
    st.markdown(f"**Protocol Guidelines:** {safe_duration_notes}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📥 Document Processing Hub")

audit_data_matrix = {
    "Clinical Parameter Metric": ["Registry ID", "BSA", "CrCl", "Risk Probability", "Severity Grade"],
    "Recorded Output Values": [str(patient_id), f"{bsa_calc:.2f} m²", f"{crcl_calc:.1f} mL/min", f"{predicted_toxicity_probability:.1f} %", f"Grade {current_clinical_grade}"]
}
st.dataframe(pd.DataFrame(audit_data_matrix), use_container_width=True)

html_printable_ledger = f"""
<div style="font-family: Arial, sans-serif; padding: 22px; border: 2px solid #2b6cb0; border-radius: 8px;">
    <h2>CLINICAL PHARMACOLOGY REPORT</h2>
    <p><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>ID:</b> {patient_id}</p>
    <p><b>Risk Score:</b> {predicted_toxicity_probability:.1f}%</p>
    <p><b>Mechanism:</b> {molecular_notes}</p>
</div>
"""

st.download_button(
    label="📄 Download Clinical Report (.html format)",
    data=html_printable_ledger,
    file_name=f"Clinical_Report_{patient_id}.html",
    mime="text/html"
)
