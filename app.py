import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration & Aesthetic Setup
st.set_page_config(
    page_title="VIPN Quantitative Pharmacology & Multi-Omics Platform", 
    page_icon="🧬", 
    layout="wide"
)

st.title("🧬 Pediatric VIPN Quantitative Pharmacology & Multi-Omics Platform")
st.write("### Advanced Decision Support System for Low-Resource Neuro-Oncology")
st.markdown("---")

# 2. Robust Model Loader with Mathematical Fallback Engine
@st.cache_resource
def load_baseline_engine():
    try:
        saved_bundle = joblib.load('vincristine_model.pkl')
        return saved_bundle['model'], False
    except Exception:
        # Fallback to an algorithmic PK/PD risk scoring matrix if file doesn't exist
        return None, True

clinical_model, is_fallback_active = load_baseline_engine()

if is_fallback_active:
    st.info("ℹ️ **System Note:** Running on the native *Deterministic Pharmacokinetics & Risk Matrix Engine* (External .pkl file unlinked).")

# 3. Sidebar Input Form - Core Patient Metrics
st.sidebar.header("🔬 Patient Core Metrics")

st.sidebar.subheader("🔹 Patient Biometrics")
age = st.sidebar.slider("Patient Age (Years)", 0.0, 18.0, 6.0, 0.5)
sex = st.sidebar.selectbox("Biological Sex", ["Male", "Female", "Unknown"])
weight = st.sidebar.number_input("Patient Weight (kg)", min_value=2.0, max_value=100.0, value=20.0, step=0.5)
height = st.sidebar.number_input("Patient Height (cm)", min_value=40.0, max_value=200.0, value=110.0, step=1.0)

# Calculate BSA using Mosteller Formula
bsa = np.sqrt((weight * height) / 3600)

st.sidebar.subheader("🔹 Vincristine Dosing Metrics")
prescribed_dose_per_m2 = st.sidebar.number_input("Prescribed Dose (mg/m²)", min_value=0.5, max_value=2.0, value=1.5, step=0.1)
actual_mg_administered = st.sidebar.number_input("Absolute Dose Administered (mg)", min_value=0.1, max_value=5.0, value=float(np.round(min(prescribed_dose_per_m2 * bsa, 2.0), 2)), step=0.1)
cumulative_cycles = st.sidebar.slider("Total Chemotherapy Cycles Received", min_value=1, max_value=12, value=3)

cumulative_exposure = actual_mg_administered * cumulative_cycles

st.sidebar.subheader("🔹 CYP3A4/5 Enzyme Inhibitors")
azole_selection = st.sidebar.selectbox(
    "Concurrent Azole Antifungal",
    options=["None", "Fluconazole (Weak/Moderate)", "Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]
)

# Multi-Omic Panel (Future Tier Expansion)
st.sidebar.subheader("🧬 Multi-Omic & Pharmacogenomic Layer (ASP Tier)")
cyp3a5_genotype = st.sidebar.selectbox("CYP3A5 Genotype Status", ["Poor Metabolizer (*3/*3)", "Intermediate Metabolizer (*1/*3)", "Extensive Metabolizer (*1/*1)", "Unknown/Not Screened"])
cep72_genotype = st.sidebar.selectbox("CEP72 Neurotoxicity Biomarker (rs924607)", ["CC (High Risk)", "CT (Moderate Risk)", "TT (Wild Type)", "Unknown"])

# 4. Processing Core Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Quantitative Risk Simulation & AI Advice")
    
    # Process Categorical Inputs
    azole_binary = 1 if azole_selection != "None" else 0
    sex_male = 1 if sex == "Male" else 0
    sex_unknown = 1 if sex == "Unknown" else 0
    
    final_pharmacological_risk = 0.0
    
    if st.button("⚡ Run Quantitative Risk Simulation"):
        if not is_fallback_active and clinical_model is not None:
            try:
                patient_vector = pd.DataFrame([{
                    'Age_Years': age,
                    'Concomitant_Azole': azole_binary,
                    'Sex_Male': sex_male,
                    'Sex_Unknown': sex_unknown
                }])
                baseline_prob = clinical_model.predict_proba(patient_vector)[0][1] * 100
            except Exception:
                # If model prediction columns mismatch, safely default to formulaic baseline
                baseline_prob = 15.0 * (2.5 if age > 10 else 1.0)
        else:
            base_risk = 15.0  
            age_factor = 2.5 if age > 10 else 1.0  
            baseline_prob = base_risk * age_factor
            
        # Potency Scaling Mechanics
        cyp3a4_inhibition_factor = 1.0
        if azole_selection == "Fluconazole (Weak/Moderate)":
            cyp3a4_inhibition_factor = 1.4  
        elif azole_selection in ["Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]:
            cyp3a4_inhibition_factor = 2.5  
            
        # Cumulative Dose Acceleration Factor (Threshold: 4.0mg)
        cumulative_risk_scalar = 1.0 + (max(0.0, cumulative_exposure - 4.0) * 0.20)
        
        # Incorporating the Multi-Omic Panel inside the calculations
        omic_modifier = 1.0
        if cyp3a5_genotype == "Poor Metabolizer (*3/*3)": omic_modifier += 0.35
        if cep72_genotype == "CC (High Risk)": omic_modifier += 0.50
        
        final_pharmacological_risk = min(baseline_prob * cyp3a4_inhibition_factor * cumulative_risk_scalar * omic_modifier, 99.5)
        
        # Save calculations into Session State
        st.session_state['calculated_risk'] = final_pharmacological_risk
        st.session_state['bsa'] = bsa
        st.session_state['cumulative_exposure'] = cumulative_exposure

    # Only render outcomes if the simulation has run once
    if 'calculated_risk' in st.session_state:
        risk_val = st.session_state['calculated_risk']
        bsa_val = st.session_state['bsa']
        cum_exp = st.session_state['cumulative_exposure']
        
        if risk_val < 35.0:
            st.success(f"### Low Risk Profile: {risk_val:.2f}% Probability")
        elif 35.0 <= risk_val < 70.0:
            st.warning(f"### Moderate Risk Profile: {risk_val:.2f}% Probability")
        else:
            st.error(f"### Critical/High Risk Profile: {risk_val:.2f}% Probability")
            
        st.write(f"**Calculated Body Surface Area (BSA):** `{bsa_val:.2f} m²`")
        st.write(f"**Total Cumulative Vincristine Burden:** `{cum_exp:.2f} mg`")
        
        # 5. AUTOMATED DOSAGE ADVICE ENGINE
        st.markdown("---")
        st.subheader("📋 Automated Clinical Guidance & Dosage Advice")
        
        advice_list = []
        
        if actual_mg_administered > 2.0:
            st.error("🚨 **CRITICAL OVERDOSE WARNING:** Absolute dose exceeds the universal pediatric safety ceiling of **2.0 mg per cycle**.")
            advice_list.append("CRITICAL: Immediately reduce absolute dose to 2.0 mg max cap to avoid irreversible axonal degeneration.")
        else:
            st.success("✅ **Dose Ceiling Check:** Absolute dose sits within the safe global pediatric threshold (< 2.0 mg).")
            
        if azole_selection in ["Voriconazole (Strong)", "Itraconazole (Strong)", "Posaconazole (Strong)"]:
            st.warning("⚠️ **Drug Interaction Warning:** Strong CYP3A4 inhibitors active. Vincristine clearance is restricted by >50%.")
            advice_list.append("STRONGLY RECOMMENDED: Emplace an empirical 25-50% dose reduction for Vincristine, or substitute azole with Liposomal Amphotericin B.")
        
        if cyp3a5_genotype == "Poor Metabolizer (*3/*3)":
            st.warning("🧬 **Pharmacogenomic Alert:** Patient possesses poor clearance alleles (*3/*3). Intrinsic neurotoxicity susceptibility is high.")
            advice_list.append("GENOMICS ADVICE: Monitor closely for early signs of foot drop and deep tendon reflex loss; consider preemptive dose titration.")

        if not advice_list:
            st.info("Standard therapeutic protocols apply. No acute interaction or dosage adjustments required.")
        else:
            for adv in advice_list:
                st.write(f"- {adv}")
                
        # 6. CLINICAL REPORT PDF GENERATION COMPONENT
        st.markdown("---")
        st.subheader("📄 Automated Clinical Documentation")
        
        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(name='TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1A365D'))
            normal_style = styles['Normal']
            
            story = []
            story.append(Paragraph("VIPN Quantitative Pharmacology Report", title_style))
            story.append(Spacer(1, 12))
            
            data = [
                ['Metric', 'Value'],
                ['Patient Age / BSA', f"{age} Yrs / {bsa_val:.2f} m²"],
                ['Calculated System Risk', f"{risk_val:.2f}%"],
                ['Administered Single Dose', f"{actual_mg_administered} mg"],
                ['Cumulative Exposure Burden', f"{cum_exp:.2f} mg"],
                ['Concomitant Azole State', azole_selection],
                ['Genomic Profile (CYP3A5/CEP72)', f"{cyp3a5_genotype} / {cep72_genotype}"]
            ]
            
            # Fixed empty attribute parameter syntax bug
            t = Table(data, colWidths=[200, 250])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F7FAFC'))
            ]))
            
            story.append(t)
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>Clinical Guidelines Applied:</b> Absolute single dose limits must never cross 2.0mg. Concomitant strong CYP3A4 inhibitors generate dynamic kinetic constraints requiring dosage adjustments.", normal_style))
            
