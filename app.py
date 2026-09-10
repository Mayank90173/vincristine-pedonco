import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. Page Configuration & Aesthetic Setup
st.set_page_config(page_title="VIPN Decision Support System", page_icon="🩺", layout="wide")

st.title("🩺 Pediatric VIPN Expert Clinical Decision Support System")
st.write("### Pharmacovigilance-Driven Risk Calculator & Evidence-Based Guidelines")
st.markdown("---")

# 2. Ingest the ML model safely
try:
    saved_bundle = joblib.load('vincristine_model.pkl')
    clinical_model = saved_bundle['model']
except:
    st.error("Model file missing. Please ensure 'vincristine_model.pkl' is generated.")
    st.stop()

# 3. Sidebar Input Form (Divided into Clinical Categories)
st.sidebar.header("📋 Patient Clinical Inputs")

st.sidebar.subheader("🔹 Demographics")
age_input = st.sidebar.slider("Patient Age (Years)", 0.0, 18.0, 6.0, 0.5)
sex_input = st.sidebar.selectbox("Biological Sex", ["Male", "Female", "Unknown"])

st.sidebar.subheader("🔹 Chemotherapy Dosing")
# standard vincristine pediatric dose is 1.5 mg/m2 capped at 2mg
vincristine_dose = st.sidebar.number_input("Current Vincristine Dose (mg/m²)", min_value=0.5, max_value=2.0, value=1.5, step=0.1)
cumulative_dose = st.sidebar.number_input("Cumulative Vincristine Dose received so far (mg)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)

st.sidebar.subheader("🔹 Co-Medications")
azole_input = st.sidebar.selectbox("Concomitant Azole Antifungals?", ["No", "Yes"])

# Layout setup: Split into two visual columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Algorithmic Risk Analytics")
    
    # Process Inputs for ML Model
    azole_flag = 1 if azole_input == "Yes" else 0
    sex_male_flag = True if sex_input == "Male" else False
    sex_unknown_flag = True if sex_input == "Unknown" else False

    patient_vector = pd.DataFrame([{
        'Age_Years': age_input,
        'Concomitant_Azole': azole_flag,
        'Sex_Male': sex_male_flag,
        'Sex_Unknown': sex_unknown_flag
    }])

    if st.button("⚡ Compute Patient VIPN Risk Profile"):
        risk_prob = clinical_model.predict_proba(patient_vector)[0][1] * 100
        
        # Risk Stratification based on statistical boundaries
        if risk_prob < 40.0:
            st.success(f"### Low Risk Stratum: {risk_prob:.2f}% Probability")
            st.metric(label="Risk Status", value="LOW RISK", delta="- Baseline Context")
        elif 40.0 <= risk_prob < 70.0:
            st.warning(f"### Moderate Risk Stratum: {risk_prob:.2f}% Probability")
            st.metric(label="Risk Status", value="MODERATE RISK", delta="+ Escalate Screening", delta_color="inverse")
        else:
            st.error(f"### High Risk Stratum: {risk_prob:.2f}% Probability")
            st.metric(label="Risk Status", value="HIGH RISK", delta="🚨 CRITICAL ALIGNMENT", delta_color="inverse")
            
        st.info("**Why these parameters matter:** Older pediatric cohorts show altered pharmacokinetics, and concurrent Azole administration blocks the **CYP3A4/5 liver enzyme system**, causing systemic accumulation of Vincristine and severe nerve injury.")

    # 🛑 SECTION A: POSSIBLE TOXICITIES & DIFFERENTIAL DIAGNOSIS (Min. 3 Possibilities)
    st.markdown("---")
    st.subheader("🕵️‍♂️ Possible Toxicities & Differential Diagnoses")
    st.write("When a child on Vincristine shows neuropathic symptoms, evaluate for at least **three distinct possibilities** before concluding it is purely VIPN:")
    
    st.markdown("""
    1.  **Vincristine-Induced Peripheral Neurotoxicity (VIPN):** Autonomic, sensory, or motor nerve damage directly caused by microtubule disruption. Resembles standard drug-induced axonopathy.
    2.  **Nutritional Neuropathy (Vitamin B12/Folate Deficiency):** Highly prevalent in resource-limited settings due to cancer-related cachexia or baseline malnutrition.
    3.  **Critical Illness Polyneuropathy (CIPN):** Occurs secondary to severe systemic infections, prolonged ICU stays, or episodes of pediatric sepsis common during neutropenia phases.
    """)

with col2:
    # 📚 SECTION B: EVIDENCE-BASED GUIDELINES & PATHOPHYSIOLOGY
    st.subheader("📚 Pathophysiology & Guidelines")
    
    with st.expander("🧬 Why is this Toxicity Occurring? (Mechanism)"):
        st.write("""
        *   **Microtubule Disruption:** Vincristine works by binding to tubulin, disrupting the mitotic spindle to kill cancer cells. However, nerves rely heavily on microtubules for axonal transport (moving nutrients down the long nerve cell). When disrupted, the axon starves and dies (axonopathy).
        *   **The Azole Interaction:** Vincristine is broken down in the body by the **CYP3A4/5** cytochrome P450 enzyme pathway in the liver. Azole antifungals (like *Fluconazole, Voriconazole*) are strong inhibitors of CYP3A4. When given together, the liver cannot process Vincristine, its blood concentration skyrockets, leading to severe neurotoxicity.
        """)
        
    with st.expander("📋 International Clinical Guidelines Alignment"):
        st.write("""
        According to international pediatric oncology consensus frameworks:
        *   **Standard Dosing:** The typical pediatric dose of Vincristine is **1.5 mg/m²** per cycle, which is strictly **capped at a maximum of 2.0 mg** total per dose to minimize sudden severe neurotoxicity.
        *   **Monitoring Protocol:** Perform systematic clinical evaluations (like the *Total Neuropathy Score* or *Pediatric Modified Balis Scale*) before each chemotherapy cycle to screen for early loss of deep tendon reflexes, paresthesia, or severe constipation.
        """)

    # 💊 SECTION C: ALTERNATIVE CLINICAL MANAGEMENT (Min. 3 Treatment Options)
    st.subheader("💊 Alternative Clinical Management Options")
    st.write("If high risk or active neurotoxicity is identified, consider these **three non-definitive clinical options**:")
    
    st.markdown("""
    *   **Option 1: Antimicrobial Stewardship (Drugged Alternatives):** Temporarily discontinue the concurrent strong CYP3A4-inhibiting azole. Switch to non-interacting antifungals such as **Liposomal Amphotericin B** or an **Echinocandin** (e.g., *Caspofungin*) if systemic fungal coverage is still mandatory.
    *   **Option 2: Chemotherapeutic Dose Adjustments:** Discuss with the pediatric oncology board regarding a **25% to 50% dose reduction** of Vincristine for subsequent cycles, or temporarily withholding a dose until neuropathic symptoms regress to Grade 1.
    *   **Option 3: Symptomatic Neuropathic Relief:** For children experiencing painful paresthesias or neuralgia, general medical consensus supports introducing non-sedating neuro-analgesics such as low-dose **Gabapentin** or **Pregabalin**, adjusted carefully for pediatric biometrics.
    """)

# 🚨 MANDATORY MEDICAL DISCLAIMER
st.markdown("---")
st.warning("⚠️ **General Medical Information Disclaimer:** This system provides general educational and research benchmarking information only. It is **NOT** a source of personalized medical advice or definitive diagnostic decisions. Clinicians must double-check physical drug labels, institutional guidelines, and complete patient clinical indicators before making prescription modifications.")
