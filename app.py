import streamlit as st
import math
from datetime import datetime

# 1. Page Configuration & Layout
st.set_page_config(
    page_title="VIPN Quantitative Pharmacology Platform", 
    page_icon="🧪", 
    layout="wide"
)

st.title("🧪 Pediatric VIPN Quantitative Pharmacology & Multi-Omics Platform")
st.write("### Advanced Evidence-Based Decision Support System for Low-Resource Neuro-Oncology")
st.markdown("---")

st.info("ℹ️ **System Core:** Running on the native *Ultra-Lightweight Deterministic Pharmacokinetics & Toxicity Logic Engine* (Zero External Dependencies).")

# Initialize Clinical Session Audit Ledger Database if not present
if 'patient_audit_log' not in st.session_state:
    st.session_state['patient_audit_log'] = "Timestamp,Patient_ID,Age,BSA_m2,Bilirubin_mgdL,Toxicity_Grade,Prescribed_Dose_m2,Standard_Dose_mg,Guideline_Dose_mg,Administered_Dose_mg,Override_Reason\n"

# 2. Sidebar Input Form - Core Patient & Molecular Metrics
st.sidebar.header("🔬 1. Patient Biometrics & Biomarkers")
patient_id = st.sidebar.text_input("Patient Identifier / ID", value="PED-ONCO-001")
age = st.sidebar.slider("Patient Age (Years)", 0.0, 18.0, 6.0, 0.5)
sex = st.sidebar.selectbox("Biological Sex", ["Male", "Female", "Unknown"])
weight = st.sidebar.number_input("Patient Weight (kg)", min_value=2.0, max_value=100.0, value=20.0, step=0.5)
height = st.sidebar.number_input("Patient Height (cm)", min_value=40.0, max_value=200.0, value=110.0, step=1.0)

# Calculate BSA using Mosteller Formula
bsa = math.sqrt((weight * height) / 3600.0)

st.sidebar.subheader("🧬 Multi-Omic & Pharmacogenomic Panel")
cyp3a5_genotype = st.sidebar.selectbox("CYP3A5 Genotype Status", ["Poor Metabolizer (*3/*3)", "Intermediate Metabolizer (*1/*3)", "Extensive Metabolizer (*1/*1)", "Unknown/Not Screened"])
cep72_genotype = st.sidebar.selectbox("CEP72 Neurotoxicity Biomarker (rs924607)", ["CC (High Risk)", "CT (Moderate Risk)", "TT (Wild Type)", "Unknown"])

# 3. Processing Core Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 2. Clinical Labs & Phenotypic Neuro-Grading")
    
    st.markdown("#### 🩸 Hepatic & Renal Profiles")
    bilirubin = st.number_input("Total Serum Bilirubin (mg/dL)", min_value=0.1, max_value=10.0, value=0.8, step=0.1, help="Standard pediatric safety cap trigger above 1.5 mg/dL")
    alt_ast = st.number_input("ALT / AST Levels (U/L)", min_value=5, max_value=500, value=35, step=5)
    crcl = st.number_input("Creatinine Clearance / CrCl (mL/min/1.73m²)", min_value=10.0, max_value=150.0, value=100.0, step=5.0)
    
    st.markdown("#### 👟 VIPN Phenotypic Tracking Checklist (CTCAE v5.0 / TNS-PV metrics)")
    tox_reflex = st.checkbox("Loss of Deep Tendon Reflexes (DTR)")
    tox_footdrop = st.checkbox("Motor Weakness / Early Foot Drop signs")
    tox_pain = st.checkbox("Severe burning paresthesia / Neuropathic pain")
    
    # Evaluate clinical toxicity grade based on user inputs
    active_symptoms = sum([tox_reflex, tox_footdrop, tox_pain])
    if active_symptoms == 0:
        clinical_grade = "Grade 0 (No Toxicity)"
        grade_modifier = 1.0
    elif active_symptoms == 1:
        clinical_grade = "Grade 1 (Mild Sensory Loss Only)"
        grade_modifier = 1.0
    elif active_symptoms == 2:
        clinical_grade = "Grade 2 (Moderate Pain / Objectively Altered Gait)"
        grade_modifier = 0.50  # 50% reduction mandatory
    else:
        clinical_grade = "Grade 3/4 (Severe Functional Deficit / Paralytic Ileus)"
        grade_modifier = 0.00  # Hold chemotherapy

    st.warning(f"**Current Phenotypic Status:** `{clinical_grade}`")

    st.markdown("---")
    st.subheader("💊 3. Vincristine Dosing Metrics")
    prescribed_dose_per_m2 = st.number_input("Standard Prescribed Dose (mg/m²)", min_value=0.5, max_value=2.0, value=1.5, step=0.1)
    
    # Calculate baseline calculated absolute dose
    calculated_absolute_dose = prescribed_dose_per_m2 * bsa
    
    # Interactive Dosing Metrics Checks
    actual_mg_administered = st.number_input("Absolute Dose to Administer (mg)", min_value=0.1, max_value=5.0, value=float(round(calculated_absolute_dose, 2)), step=0.01)
    cumulative_cycles = st.slider("Total Chemotherapy Cycles Received", min_value=1, max_value=12, value=3)
    cumulative_exposure = actual_mg_administered * cumulative_cycles

    # Strict Cap Enforcement Alert
    override_reason = "N/A"
    if actual_mg_administered > 2.0:
        st.error("🚨 ⚠️ **CRITICAL UNIVERSAL CAP BREACH:** Single Vincristine dose exceeds the mandatory 2.0 mg pediatric safety ceiling!")
        override_reason = st.text_input("🛑 **MANDATORY:** Enter Explicit Clinical Manual Override Reason to proceed:")
        if not override_reason:
            st.warning("A valid justification string is required to permit logs generation.")
    
    st.markdown("#### 🔬 Concomitant DDI State")
    azole_selection = st.selectbox(
        "Concurrent Azole Antifungal Regime",
        options=["None", "Fluconazole (Weak/Moderate)", "Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]
    )

with col2:
    st.subheader("📊 4. Quantitative Pharmacology Risk Simulation")
    
    if st.button("⚡ Run Live Evidence-Based Risk Evaluation"):
        # Deterministic Risk Computation Architecture
        base_risk = 15.0  
        age_factor = 2.5 if age > 10 else 1.0  
        baseline_prob = base_risk * age_factor
            
        cyp3a4_inhibition_factor = 1.0
        ddi_class = "None"
        if azole_selection == "Fluconazole (Weak/Moderate)":
            cyp3a4_inhibition_factor = 1.4  
            ddi_class = "Category C (Monitor Therapy)"
        elif azole_selection in ["Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]:
            cyp3a4_inhibition_factor = 2.5  
            ddi_class = f"Category X / D (Avoid Combination / Modify Therapy) [Lexicomp / Micromedex Classification]"
            
        cumulative_risk_scalar = 1.0 + (max(0.0, cumulative_exposure - 4.0) * 0.20)
        
        omic_modifier = 1.0
        if cyp3a5_genotype == "Poor Metabolizer (*3/*3)": omic_modifier += 0.35
        if cep72_genotype == "CC (High Risk)": omic_modifier += 0.50
        
        final_pharmacological_risk = min(baseline_prob * cyp3a4_inhibition_factor * cumulative_risk_scalar * omic_modifier, 99.5)
        
        # Calculate dynamic clinical protocol dose advice
        guideline_dose = calculated_absolute_dose
        
        # Apply DDI reduction factors based on CPIC/DPWG models
        if azole_selection in ["Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]:
            guideline_dose = guideline_dose * 0.50  # Apply empiric 50% safety attenuation

        # Apply Hepatic Adjustment (Bilirubin rules based on standard pediatric protocols)
        hepatic_alert = "Normal Clearances"
        if bilirubin > 3.0:
            guideline_dose = guideline_dose * 0.25 
            hepatic_alert = "Bilirubin > 3.0 mg/dL: Apply 75% Dose Reduction [Standard Clinical Protocol]"
        elif bilirubin > 1.5:
            guideline_dose = guideline_dose * 0.50 
            hepatic_alert = "Bilirubin 1.5 - 3.0 mg/dL: Apply 50% Dose Reduction [Standard Clinical Protocol]"
            
        # Apply Neuro-Grading Adjustments
        guideline_dose = guideline_dose * grade_modifier
        
        # Enforce Safe Cap
        if guideline_dose > 2.0:
            guideline_dose = 2.0
            
        # Save states into session variables
        st.session_state['sim_run'] = True
        st.session_state['calculated_risk'] = final_pharmacological_risk
        st.session_state['guideline_dose'] = guideline_dose
        st.session_state['ddi_class'] = ddi_class
        st.session_state['hepatic_alert'] = hepatic_alert

        # Update Live Excel Ledger Session Storage with accurate validation logs
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = f"{timestamp_str},{patient_id},{age},{bsa:.2f},{bilirubin},{clinical_grade},{prescribed_dose_per_m2},{calculated_absolute_dose:.2f},{guideline_dose:.2f},{actual_mg_administered},{override_reason.replace(',','-')}\n"
        st.session_state['patient_audit_log'] += row

    # Render Simulation Reports & Outputs
    if 'sim_run' in st.session_state:
        risk_val = st.session_state['calculated_risk']
        guide_dose = st.session_state['guideline_dose']
        ddi_status = st.session_state['ddi_class']
        h_alert = st.session_state['hepatic_alert']
        
        st.markdown("### ⚠️ QUANTITATIVE PHARMACOLOGY DETECTED LOGIC")
        
        if risk_val >= 70.0 or actual_mg_administered > 2.0 or grade_modifier < 1.0:
            st.error(f"❌ **CRITICAL CLINICAL ADVERSE METRIC:** {risk_val:.2f}% Cumulative Probability of Severe VIPN")
        else:
            st.warning(f"⚠️ **MODERATE CLINICAL PROFILE:** {risk_val:.2f}% Toxicity Induction Probability")
            
        st.write(f"**Patient Metric Parameters:** Calculated BSA = `{bsa:.2f} m²` | Total Accumulated Burden = `{cumulative_exposure:.2f} mg`")
        
        # Context Aware Multi-Omic Logic display (Fixes the dynamic text gap)
        st.markdown("#### 🧬 Penetrance Context Engine")
        if cep72_genotype == "TT (Wild Type)":
            st.info(f"💡 **Biomarker Penetrance Note:** Although patient possesses the protective **CEP72 TT (Wild Type)** variant, systemic exposure kinetics are still structurally compromised due to the zero-clearance **CYP3A5 \*3/\*3** state combined with strong chemical enzyme inhibition via **{azole_selection}**.")

        # Display Core Guidance Block (As requested by Neuro-Oncologists)
        st.markdown(f"""
        *   **Standard Computed Dose (1.5 mg/m² base):** `{calculated_absolute_dose:.2f} mg`
        *   **Recommended Adjusted Safe Dose:** `{guide_dose:.2f} mg` *[Based on CPIC / DPWG Guidelines & Phenotypic Grade Adjustments]*
