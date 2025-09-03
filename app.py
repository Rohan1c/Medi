import streamlit as st
import time
import random
from datetime import datetime
from typing import List, Dict, Any
import json
from prescription_parser import parse_prescription_text
from validator import validate_prescription_data
from ocr_utils import extract_text_from_image, parse_prescription


# Page config
st.set_page_config(
    page_title="MedValidator AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
def load_css():
    st.markdown("""
    <style>
    .main-header {
        background-color: var(--background-color);
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        background-color: var(--accent-color);
        padding: 0.5rem;
        border-radius: 0.5rem;
        font-size: 1.5rem;
    }
    
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        background-color: var(--background-color);
        margin-bottom: 1rem;
    }
    
    .message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #2563eb;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background-color: var(--secondary-bg);
        color: var(--text-color);
        margin-right: auto;
    }
    
    .validation-card {
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: var(--background-color);
    }
    
    .status-approved {
        border-left: 4px solid #10b981;
        background-color: #f0fdf4;
    }
    
    .status-warning {
        border-left: 4px solid #f59e0b;
        background-color: #fffbeb;
    }
    
    .status-rejected {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
    }
    
    .theme-light {
        --background-color: #ffffff;
        --text-color: #1f2937;
        --border-color: #e5e7eb;
        --accent-color: #dbeafe;
        --secondary-bg: #f9fafb;
    }
    
    .theme-dark {
        --background-color: #1f2937;
        --text-color: #f9fafb;
        --border-color: #374151;
        --accent-color: #1e3a8a;
        --secondary-bg: #374151;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        border-radius: 0.5rem 0.5rem 0 0;
    }
    
    .prescription-form {
        background-color: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Apple system font */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
    }
    
    /* Warning styling */
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        color: #92400e;
    }
    
    /* Dark mode adjustments */
    .theme-dark .warning-box {
        background-color: #451a03;
        border-color: #92400e;
        color: #fbbf24;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                'id': '1',
                'type': 'bot',
                'content': "Hello! I'm your AI medical assistant. I'll help you understand your symptoms better. Please describe your main symptoms, and I'll ask follow-up questions to narrow down possible conditions.",
                'timestamp': datetime.now()
            }
        ]
    if 'current_symptoms' not in st.session_state:
        st.session_state.current_symptoms = []
    if 'diagnosis_stage' not in st.session_state:
        st.session_state.diagnosis_stage = 'initial'
    if 'prescription_data' not in st.session_state:
        st.session_state.prescription_data = {
            'diagnosis': '',
            'patient_info': {
                'age': '',
                'weight': '',
                'allergies': '',
                'conditions': ''
            },
            'prescriptions': [{'medication': '', 'dosage': '', 'frequency': '', 'duration': ''}]
        }
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

def render_header():
    theme_class = "theme-dark" if st.session_state.dark_mode else "theme-light"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("🩺 **MedValidator AI**")
        st.caption("AI-Powered Medical Assistant")
    
    with col3:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Toggle theme"):
            toggle_theme()
            st.rerun()

def diagnosis_chat():
    st.markdown("### AI Diagnosis Assistant")
    st.caption("Describe your symptoms and I'll help narrow down possible conditions")
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="message user-message">
                    {message['content']}<br>
                    <small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message bot-message">
                    🤖 {message['content']}<br>
                    <small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_area(
            "Describe your symptoms...",
            key="symptom_input",
            height=80,
            placeholder="e.g., I have been experiencing headaches and fever for 2 days"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    if send_button and user_input.strip():
        process_user_message(user_input.strip())
        st.rerun()
    
    # Warning notice
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Medical Disclaimer:</strong> This AI assistant provides informational support only and should not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.
    </div>
    """, unsafe_allow_html=True)

def process_user_message(user_input: str):
    # Add user message
    user_message = {
        'id': str(int(time.time() * 1000)),
        'type': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    }
    st.session_state.messages.append(user_message)
    
    # Process based on diagnosis stage
    if st.session_state.diagnosis_stage == 'initial':
        symptom = {
            'name': user_input,
            'severity': 5,
            'duration': 'recent'
        }
        st.session_state.current_symptoms = [symptom]
        st.session_state.diagnosis_stage = 'followup'
        
        # Generate follow-up question
        bot_response = generate_followup_question(st.session_state.current_symptoms)
        
    elif st.session_state.diagnosis_stage == 'followup':
        # Add more context
        symptom = {
            'name': user_input,
            'severity': 5,
            'duration': 'recent'
        }
        st.session_state.current_symptoms.append(symptom)
        
        if len(st.session_state.current_symptoms) >= 3:
            st.session_state.diagnosis_stage = 'diagnosis'
            bot_response = generate_diagnosis(st.session_state.current_symptoms)
        else:
            bot_response = generate_followup_question(st.session_state.current_symptoms)
    
    else:  # diagnosis stage
        if 'new' in user_input.lower() or 'start' in user_input.lower():
            st.session_state.diagnosis_stage = 'initial'
            st.session_state.current_symptoms = []
            bot_response = "Let's start a new consultation. Please describe your main symptoms."
        else:
            bot_response = "I can help you with symptom analysis. Type 'new consultation' to start over, or switch to the Prescription Checker tab if you need prescription validation."
    
    # Add bot response
    bot_message = {
        'id': str(int(time.time() * 1000) + 1),
        'type': 'bot',
        'content': bot_response,
        'timestamp': datetime.now()
    }
    st.session_state.messages.append(bot_message)

def generate_followup_question(symptoms: List[Dict]) -> str:
    questions = [
        "How long have you been experiencing these symptoms?",
        "On a scale of 1-10, how would you rate the severity of your symptoms?",
        "Do you have any fever or temperature changes?",
        "Have you experienced any nausea or vomiting?",
        "Are you taking any medications currently?",
        "Do you have any known allergies or medical conditions?",
        "Have you traveled recently or been exposed to anyone who was sick?"
    ]
    return random.choice(questions)

def generate_diagnosis(symptoms: List[Dict]) -> str:
    possible_diagnoses = [
        {
            'condition': "Upper Respiratory Infection",
            'confidence': "85%",
            'description': "Common cold or flu-like symptoms",
            'recommendations': [
                "Rest and stay hydrated",
                "Consider over-the-counter pain relievers",
                "Monitor symptoms for 7-10 days",
                "Seek medical attention if symptoms worsen"
            ]
        },
        {
            'condition': "Seasonal Allergies",
            'confidence': "70%",
            'description': "Allergic reaction to environmental factors",
            'recommendations': [
                "Avoid known allergens",
                "Consider antihistamines",
                "Use air purifiers indoors",
                "Consult an allergist if symptoms persist"
            ]
        },
        {
            'condition': "Mild Gastroenteritis",
            'confidence': "75%",
            'description': "Stomach flu or food-related illness",
            'recommendations': [
                "Stay hydrated with clear fluids",
                "Follow the BRAT diet (Bananas, Rice, Applesauce, Toast)",
                "Rest and avoid solid foods temporarily",
                "Seek medical care if symptoms persist over 3 days"
            ]
        }
    ]
    
    diagnosis = random.choice(possible_diagnoses)
    
    response = f"""Based on your symptoms, here's my assessment:

**Likely Condition:** {diagnosis['condition']}
**Confidence Level:** {diagnosis['confidence']}

**Description:** {diagnosis['description']}

**Recommendations:**
"""
    for rec in diagnosis['recommendations']:
        response += f"• {rec}\n"
    
    response += "\n⚠️ **Important:** This is an AI assessment only. Please consult with a healthcare professional for proper diagnosis and treatment.\n\nWould you like to start a new consultation or check a prescription?"
    
    return response

def prescription_checker():
    st.markdown("### Prescription Checker")
    st.caption("Validate prescriptions against patient information and diagnosis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Patient Information & Diagnosis")
        
        # Diagnosis input
        diagnosis = st.text_area(
            "Medical Diagnosis *",
            value=st.session_state.prescription_data['diagnosis'],
            height=100,
            placeholder="Enter the medical diagnosis..."
        )
        st.session_state.prescription_data['diagnosis'] = diagnosis
        
        # Patient info
        col_age, col_weight = st.columns(2)
        with col_age:
            age = st.text_input(
                "Age (years)",
                value=st.session_state.prescription_data['patient_info']['age'],
                placeholder="Years"
            )
            st.session_state.prescription_data['patient_info']['age'] = age
        
        with col_weight:
            weight = st.text_input(
                "Weight (kg)",
                value=st.session_state.prescription_data['patient_info']['weight'],
                placeholder="kg"
            )
            st.session_state.prescription_data['patient_info']['weight'] = weight
        
        allergies = st.text_input(
            "Known Allergies",
            value=st.session_state.prescription_data['patient_info']['allergies'],
            placeholder="e.g., Penicillin, Sulfa drugs"
        )
        st.session_state.prescription_data['patient_info']['allergies'] = allergies
        
        conditions = st.text_input(
            "Medical Conditions",
            value=st.session_state.prescription_data['patient_info']['conditions'],
            placeholder="e.g., Diabetes, Hypertension"
        )
        st.session_state.prescription_data['patient_info']['conditions'] = conditions
        
        # Prescriptions
        st.markdown("#### 💊 Prescribed Medications")
        
        for i, prescription in enumerate(st.session_state.prescription_data['prescriptions']):
            with st.expander(f"Medication {i + 1}", expanded=True):
                col_med, col_dose = st.columns(2)
                with col_med:
                    medication = st.text_input(
                        "Medication name",
                        value=prescription['medication'],
                        key=f"med_{i}",
                        placeholder="e.g., Amoxicillin"
                    )
                    st.session_state.prescription_data['prescriptions'][i]['medication'] = medication
                
                with col_dose:
                    dosage = st.text_input(
                        "Dosage",
                        value=prescription['dosage'],
                        key=f"dose_{i}",
                        placeholder="e.g., 500mg"
                    )
                    st.session_state.prescription_data['prescriptions'][i]['dosage'] = dosage
                
                col_freq, col_dur = st.columns(2)
                with col_freq:
                    frequency = st.text_input(
                        "Frequency",
                        value=prescription['frequency'],
                        key=f"freq_{i}",
                        placeholder="e.g., 2 times daily"
                    )
                    st.session_state.prescription_data['prescriptions'][i]['frequency'] = frequency
                
                with col_dur:
                    duration = st.text_input(
                        "Duration",
                        value=prescription['duration'],
                        key=f"dur_{i}",
                        placeholder="e.g., 7 days"
                    )
                    st.session_state.prescription_data['prescriptions'][i]['duration'] = duration
                
                if len(st.session_state.prescription_data['prescriptions']) > 1:
                    if st.button(f"Remove Medication {i + 1}", key=f"remove_{i}"):
                        st.session_state.prescription_data['prescriptions'].pop(i)
                        st.rerun()
        
        col_add, col_validate, col_reset = st.columns(3)
        
        with col_add:
            if st.button("+ Add Medication"):
                st.session_state.prescription_data['prescriptions'].append({
                    'medication': '', 'dosage': '', 'frequency': '', 'duration': ''
                })
                st.rerun()
        
        with col_validate:
            if st.button("Validate Prescription"):
                # Get free-text prescription from a text area
                user_text = st.text_area(
                    "Paste prescription here:", 
                    height=150, 
                    placeholder="e.g., Paracetamol 500mg twice a day for 7 days; Ibuprofen 200mg once daily for 5 days"
                )
                
                # Convert free-text into structured prescriptions
                parsed_prescriptions = parse_prescription_text(user_text)
                
                # Overwrite the structured prescriptions in session state
                st.session_state.prescription_data['prescriptions'] = parsed_prescriptions

                # ✅ Call validator with all arguments
                st.session_state.validation_result = validate_prescription_data(
                    st.session_state.prescription_data['diagnosis'],
                    st.session_state.prescription_data['patient_info'],
                    st.session_state.prescription_data['prescriptions']
                )

                st.rerun()
        
        with col_reset:
            if st.button("Reset"):
                st.session_state.prescription_data = {
                    'diagnosis': '',
                    'patient_info': {
                        'age': '',
                        'weight': '',
                        'allergies': '',
                        'conditions': ''
                    },
                    'prescriptions': [{'medication': '', 'dosage': '', 'frequency': '', 'duration': ''}]
                }
                st.session_state.validation_result = None
                st.rerun()

        # --- Image upload feature ---
        st.markdown("#### 📷 Upload Prescription Image")
        uploaded_file = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with open("temp_image.png", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Run OCR
            raw_text = extract_text_from_image("temp_image.png")
            st.text_area("Extracted OCR Text", raw_text, height=150)

            # Parse OCR results into structured prescriptions
            parsed_meds = parse_prescription(raw_text)
            st.session_state.prescription_data['prescriptions'] = [
                {"medication": med["name"], "dosage": f"{med['dosage']}{med['unit']}", "frequency": "", "duration": ""}
                for med in parsed_meds
            ]

            st.success("✅ Prescription data extracted from image! Now you can validate.")
        # --- End image upload feature ---
    
    with col2:
        st.markdown("#### 📋 Validation Results")
        
        if st.session_state.validation_result is None:
            st.info("Enter prescription details and click 'Validate Prescription' to see results")
        else:
            display_validation_results()

def validate_prescription_data(
    diagnosis: str,
    patient_info: Dict[str, str],
    prescriptions: List[Dict[str, str]]
) -> Dict:
    """
    Validates prescription data.
    
    Args:
        diagnosis: str, medical diagnosis
        patient_info: dict with 'age', 'weight', 'allergies', 'conditions'
        prescriptions: list of dicts with 'medication', 'dosage', 'frequency', 'duration'
    
    Returns:
        dict with overall status, item-level messages, and recommendations
    """
    result = {
        'overall': 'approved',
        'items': [],
        'recommendations': [
            'Verify patient allergies before dispensing',
            'Monitor patient for adverse reactions',
            'Ensure proper patient education on medication usage',
            'Schedule appropriate follow-up appointments'
        ]
    }

    age = patient_info.get('age', '')
    allergies = patient_info.get('allergies', '').lower()
    diagnosis_lower = diagnosis.lower()

    for i, prescription in enumerate(prescriptions):
        med = prescription.get('medication', '').strip()
        dose = prescription.get('dosage', '').strip()
        freq = prescription.get('frequency', '').strip()
        issues = []
        status = 'approved'

        if not med:
            issues.append("Medication name is required")
            status = 'rejected'

        if not dose:
            issues.append("Dosage is required")
            status = 'rejected'

        # Allergy check example
        if 'penicillin' in med.lower() and 'penicillin' in allergies:
            issues.append("ALLERGY ALERT: Patient is allergic to penicillin")
            status = 'rejected'

        # Age check example
        if age.isdigit() and int(age) < 16 and 'aspirin' in med.lower():
            issues.append("AGE WARNING: Aspirin not recommended for patients under 16")
            if status == 'approved':
                status = 'warning'

        # Frequency check example
        if 'ibuprofen' in med.lower() and '4 times' in freq.lower():
            issues.append("DOSAGE WARNING: High frequency for ibuprofen, monitor for GI effects")
            if status == 'approved':
                status = 'warning'

        # Diagnosis matching example
        if 'infection' in diagnosis_lower and not any(x in med.lower() for x in ['antibiotic', 'amoxicillin', 'penicillin']):
            issues.append("INFO: Consider antibiotic for bacterial infection")
            if status == 'approved':
                status = 'warning'

        if not issues:
            issues.append("Prescription appears appropriate for the given diagnosis")

        result['items'].append({
            'medication': med or f"Medication {i + 1}",
            'status': status,
            'message': '. '.join(issues)
        })

    # Determine overall status
    if any(item['status'] == 'rejected' for item in result['items']):
        result['overall'] = 'rejected'
    elif any(item['status'] == 'warning' for item in result['items']):
        result['overall'] = 'warning'

    return result


# Quick test
if __name__ == "__main__":
    patient = {'age': '15', 'weight': '50', 'allergies': 'Penicillin', 'conditions': ''}
    prescriptions = [
        {'medication': 'Amoxicillin', 'dosage': '500mg', 'frequency': 'twice daily', 'duration': '7 days'},
        {'medication': 'Aspirin', 'dosage': '100mg', 'frequency': 'once daily', 'duration': '5 days'}
    ]
    diagnosis = 'Bacterial infection'
    res = validate_prescription_data(diagnosis, patient, prescriptions)
    print(res)


def display_validation_results():
    result = st.session_state.validation_result
    
    # Overall status
    if result['overall'] == 'approved':
        st.success("✅ Prescription Approved - All medications appear safe and appropriate")
    elif result['overall'] == 'warning':
        st.warning("⚠️ Prescription Approved with Warnings - Some concerns identified, review recommended")
    else:
        st.error("❌ Prescription Requires Review - Critical issues found, do not dispense")
    
    # Individual medication results
    st.markdown("**Medication Analysis:**")
    
    for item in result['items']:
        if item['status'] == 'approved':
            st.success(f"✅ **{item['medication']}**\n\n{item['message']}")
        elif item['status'] == 'warning':
            st.warning(f"⚠️ **{item['medication']}**\n\n{item['message']}")
        else:
            st.error(f"❌ **{item['medication']}**\n\n{item['message']}")
    
    # Recommendations
    st.markdown("**General Recommendations:**")
    for rec in result['recommendations']:
        st.markdown(f"• {rec}")

def main():
    load_css()
    init_session_state()
    
    # Apply theme
    theme_class = "theme-dark" if st.session_state.dark_mode else "theme-light"
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
    
    # Header
    render_header()
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["🩺 Diagnosis Assistant", "📋 Prescription Checker"])
    
    with tab1:
        diagnosis_chat()
    
    with tab2:
        prescription_checker()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "⚠️ This is an AI assistant tool. Always consult with qualified healthcare professionals for medical advice."
        "</div>",
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
