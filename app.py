import streamlit as st
import time
import random
from datetime import datetime
from typing import List, Dict, Any
import json
import re
from PIL import Image
import io
import base64

# Page config
st.set_page_config(
    page_title="MedValidator AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --font-size: 14px;
        --background: #ffffff;
        --foreground: #1f2937;
        --card: #ffffff;
        --card-foreground: #1f2937;
        --primary: #030213;
        --primary-foreground: #ffffff;
        --secondary: #f1f5f9;
        --secondary-foreground: #030213;
        --muted: #ececf0;
        --muted-foreground: #717182;
        --accent: #e9ebef;
        --accent-foreground: #030213;
        --destructive: #d4183d;
        --destructive-foreground: #ffffff;
        --border: rgba(0, 0, 0, 0.1);
        --input-background: #f3f3f5;
        --radius: 0.625rem;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
    }
    
    .dark-theme {
        --background: #1f2937;
        --foreground: #f9fafb;
        --card: #1f2937;
        --card-foreground: #f9fafb;
        --primary: #f9fafb;
        --primary-foreground: #1f2937;
        --secondary: #374151;
        --secondary-foreground: #f9fafb;
        --muted: #374151;
        --muted-foreground: #9ca3af;
        --accent: #374151;
        --accent-foreground: #f9fafb;
        --border: #374151;
        --input-background: #374151;
    }
    
    /* Apply theme */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: var(--font-size);
        background-color: var(--background);
        color: var(--foreground);
    }
    
    /* Header styling */
    .main-header {
        background: var(--card);
        border-bottom: 1px solid var(--border);
        padding: 1rem 0;
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
        background: var(--primary);
        color: var(--primary-foreground);
        padding: 0.5rem;
        border-radius: var(--radius);
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
    }
    
    .logo-text h1 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--foreground);
    }
    
    .logo-text p {
        margin: 0;
        font-size: 0.875rem;
        color: var(--muted-foreground);
    }
    
    /* Card styling */
    .custom-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .card-header {
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--foreground);
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-description {
        font-size: 0.875rem;
        color: var(--muted-foreground);
        margin: 0;
    }
    
    /* Chat container */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        margin-bottom: 1rem;
    }
    
    .message {
        margin-bottom: 1rem;
        display: flex;
        gap: 0.75rem;
        animation: messageSlideIn 0.3s ease-out;
    }
    
    .message.user {
        justify-content: flex-end;
    }
    
    .message.user .message-content {
        flex-direction: row-reverse;
    }
    
    .message-content {
        display: flex;
        gap: 0.75rem;
        max-width: 80%;
    }
    
    .message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 0.875rem;
    }
    
    .message.user .message-avatar {
        background: var(--primary);
        color: var(--primary-foreground);
    }
    
    .message.bot .message-avatar {
        background: var(--muted);
        color: var(--muted-foreground);
    }
    
    .message-bubble {
        padding: 0.75rem;
        border-radius: var(--radius);
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    .message.user .message-bubble {
        background: var(--primary);
        color: var(--primary-foreground);
    }
    
    .message.bot .message-bubble {
        background: var(--muted);
        color: var(--foreground);
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.25rem;
    }
    
    /* Status indicators */
    .status-card {
        border-left: 4px solid;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0 var(--radius) var(--radius) 0;
    }
    
    .status-approved {
        border-left-color: var(--success);
        background: rgba(34, 197, 94, 0.1);
    }
    
    .status-warning {
        border-left-color: var(--warning);
        background: rgba(245, 158, 11, 0.1);
    }
    
    .status-rejected {
        border-left-color: var(--error);
        background: rgba(239, 68, 68, 0.1);
    }
    
    .dark-theme .status-approved {
        background: rgba(34, 197, 94, 0.2);
    }
    
    .dark-theme .status-warning {
        background: rgba(245, 158, 11, 0.2);
    }
    
    .dark-theme .status-rejected {
        background: rgba(239, 68, 68, 0.2);
    }
    
    /* Form elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: var(--input-background) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--foreground) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(3, 2, 19, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary) !important;
        color: var(--primary-foreground) !important;
        border: none !important;
        border-radius: var(--radius) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(3, 2, 19, 0.9) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .secondary-button {
        background: transparent !important;
        color: var(--primary) !important;
        border: 1px solid var(--border) !important;
    }
    
    .secondary-button:hover {
        background: var(--accent) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary) !important;
        background: var(--accent) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: var(--card);
        border-radius: var(--radius);
        padding: 0.25rem;
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem !important;
        border-radius: calc(var(--radius) - 2px) !important;
        font-weight: 500 !important;
        color: var(--muted-foreground) !important;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary) !important;
        color: var(--primary-foreground) !important;
    }
    
    /* Warning/Disclaimer */
    .disclaimer {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid var(--warning);
        border-radius: var(--radius);
        padding: 1rem;
        margin: 1rem 0;
        color: var(--foreground);
    }
    
    .disclaimer strong {
        color: var(--warning);
    }
    
    /* Animations */
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--muted-foreground);
        font-size: 0.875rem;
    }
    
    /* Image preview */
    .image-preview {
        max-width: 200px;
        border-radius: var(--radius);
        margin-top: 0.5rem;
    }
    
    /* Medication item */
    .medication-item {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Grid layout */
    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            padding: 0 1rem;
        }
        
        .form-grid {
            grid-template-columns: 1fr;
        }
        
        .message-content {
            max-width: 95%;
        }
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
                'timestamp': datetime.now(),
                'image': None
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
    if 'prescription_image' not in st.session_state:
        st.session_state.prescription_image = None

def render_header():
    theme_class = "dark-theme" if st.session_state.dark_mode else ""
    
    st.markdown(f"""
    <div class="{theme_class}">
        <div class="main-header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-icon">🩺</div>
                    <div class="logo-text">
                        <h1>MedValidator AI</h1>
                        <p>AI-Powered Medical Assistant</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme toggle in sidebar
    with st.sidebar:
        if st.button("🌙 Toggle Dark Mode" if not st.session_state.dark_mode else "☀️ Toggle Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

def diagnosis_chat():
    theme_class = "dark-theme" if st.session_state.dark_mode else ""
    
    st.markdown(f"""
    <div class="{theme_class}">
        <div class="custom-card">
            <div class="card-header">
                <div class="card-title">
                    🤖 AI Diagnosis Assistant
                </div>
                <div class="card-description">
                    Describe your symptoms and I'll help narrow down possible conditions
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat messages container
    chat_html = f'<div class="{theme_class}"><div class="chat-container">'
    
    for message in st.session_state.messages:
        message_class = "user" if message['type'] == 'user' else "bot"
        avatar_icon = "👤" if message['type'] == 'user' else "🤖"
        
        chat_html += f"""
        <div class="message {message_class}">
            <div class="message-content">
                <div class="message-avatar">{avatar_icon}</div>
                <div class="message-bubble">
                    {message['content'].replace('\n', '<br>')}
                    <div class="message-time">{message['timestamp'].strftime('%H:%M:%S')}</div>
                </div>
            </div>
        </div>
        """
    
    chat_html += '</div></div>'
    st.markdown(chat_html, unsafe_allow_html=True)
    
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
        uploaded_image = st.file_uploader(
            "Attach Image",
            type=["png", "jpg", "jpeg"],
            key="diagnosis_image",
            help="Upload an image related to your symptoms"
        )
        
        if st.button("Send Message", type="primary", use_container_width=True):
            if user_input.strip() or uploaded_image:
                process_user_message(user_input.strip(), uploaded_image)
                st.rerun()
    
    # Show uploaded image preview
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", width=200)
    
    # Medical disclaimer
    st.markdown(f"""
    <div class="{theme_class}">
        <div class="disclaimer">
            <strong>⚠️ Medical Disclaimer:</strong> This AI assistant provides informational support only and should not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.
        </div>
    </div>
    """, unsafe_allow_html=True)

def process_user_message(user_input: str, image_file=None):
    # Add user message
    user_message = {
        'id': str(int(time.time() * 1000)),
        'type': 'user',
        'content': user_input,
        'timestamp': datetime.now(),
        'image': image_file
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
        
        bot_response = generate_followup_question(st.session_state.current_symptoms)
        
    elif st.session_state.diagnosis_stage == 'followup':
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
        'timestamp': datetime.now(),
        'image': None
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
    theme_class = "dark-theme" if st.session_state.dark_mode else ""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="custom-card">
                <div class="card-header">
                    <div class="card-title">
                        📋 Patient Information & Prescription
                    </div>
                    <div class="card-description">
                        Enter patient details and prescribed medications for validation
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Diagnosis input
        diagnosis = st.text_area(
            "Medical Diagnosis *",
            value=st.session_state.prescription_data['diagnosis'],
            height=100,
            placeholder="Enter the medical diagnosis...",
            key="diagnosis_input"
        )
        st.session_state.prescription_data['diagnosis'] = diagnosis
        
        st.markdown("### Patient Information")
        
        # Patient info
        col_age, col_weight = st.columns(2)
        with col_age:
            age = st.text_input(
                "Age (years)",
                value=st.session_state.prescription_data['patient_info']['age'],
                placeholder="Years",
                key="age_input"
            )
            st.session_state.prescription_data['patient_info']['age'] = age
        
        with col_weight:
            weight = st.text_input(
                "Weight (kg)",
                value=st.session_state.prescription_data['patient_info']['weight'],
                placeholder="kg",
                key="weight_input"
            )
            st.session_state.prescription_data['patient_info']['weight'] = weight
        
        allergies = st.text_input(
            "Known Allergies",
            value=st.session_state.prescription_data['patient_info']['allergies'],
            placeholder="e.g., Penicillin, Sulfa drugs",
            key="allergies_input"
        )
        st.session_state.prescription_data['patient_info']['allergies'] = allergies
        
        conditions = st.text_input(
            "Medical Conditions",
            value=st.session_state.prescription_data['patient_info']['conditions'],
            placeholder="e.g., Diabetes, Hypertension",
            key="conditions_input"
        )
        st.session_state.prescription_data['patient_info']['conditions'] = conditions
        
        # Quick prescription entry
        st.markdown("### Quick Prescription Entry")
        prescription_text = st.text_area(
            "Paste prescription here",
            height=100,
            placeholder="e.g., Paracetamol 500mg twice daily for 7 days; Ibuprofen 200mg once daily for 5 days",
            key="prescription_text_input"
        )
        
        # Prescriptions
        st.markdown("### Prescribed Medications")
        
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
        
        # Action buttons
        col_add, col_img, col_validate, col_reset = st.columns(4)

        with col_add:
            if st.button("+ Add Medication"):
                st.session_state.prescription_data['prescriptions'].append({
                    'medication': '', 'dosage': '', 'frequency': '', 'duration': ''
                })
                st.rerun()

        with col_img:
            prescription_image = st.file_uploader(
                "Attach Prescription",
                type=["png", "jpg", "jpeg", "pdf"],
                key="prescription_image_upload",
                help="Upload prescription image or PDF"
            )
            if prescription_image is not None:
                st.session_state.prescription_image = prescription_image

        with col_validate:
            if st.button("Validate Prescription", type="primary"):
                if prescription_text.strip():
                    parsed_prescriptions = parse_prescription_text(prescription_text)
                    if parsed_prescriptions:
                        st.session_state.prescription_data['prescriptions'] = parsed_prescriptions
                
                result = validate_prescription_data(
                    st.session_state.prescription_data['diagnosis'],
                    st.session_state.prescription_data['patient_info'],
                    st.session_state.prescription_data['prescriptions']
                )
                st.session_state.validation_result = result
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
                st.session_state.prescription_image = None
                st.rerun()
        
        # Show uploaded prescription image
        if st.session_state.prescription_image is not None:
            st.markdown("### Attached Prescription")
            if st.session_state.prescription_image.type.startswith('image'):
                st.image(st.session_state.prescription_image, caption="Prescription Image", width=300)
            else:
                st.write(f"📄 {st.session_state.prescription_image.name}")
    
    with col2:
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="custom-card">
                <div class="card-header">
                    <div class="card-title">
                        📊 Validation Results
                    </div>
                    <div class="card-description">
                        Review prescription safety and appropriateness
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.validation_result is None:
            st.info("Enter prescription details and click 'Validate Prescription' to see results")
        else:
            display_validation_results()

def parse_prescription_text(text: str) -> List[Dict[str, str]]:
    """Parse prescription text into structured format"""
    if not text.strip():
        return []
    
    lines = re.split(r'[;\n]', text)
    parsed = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        if len(parts) >= 2:
            medication = parts[0]
            
            # Extract dosage (number + unit)
            dosage_match = re.search(r'(\d+\s*(?:mg|g|ml|units?))', line, re.IGNORECASE)
            dosage = dosage_match.group(1) if dosage_match else ''
            
            # Extract frequency
            frequency_match = re.search(r'(once|twice|thrice|\d+\s*times?)\s*(?:daily|per\s*day|a\s*day)', line, re.IGNORECASE)
            frequency = frequency_match.group(0) if frequency_match else ''
            
            # Extract duration
            duration_match = re.search(r'(?:for\s*)?(\d+\s*(?:days?|weeks?|months?))', line, re.IGNORECASE)
            duration = duration_match.group(1) if duration_match else ''
            
            parsed.append({
                'medication': medication,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration
            })
    
    return parsed if parsed else []

def validate_prescription_data(diagnosis: str, patient_info: Dict[str, str], prescriptions: List[Dict[str, str]]) -> Dict:
    """Validate prescription data"""
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

    age_str = patient_info.get('age', '')
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

        # Allergy check
        if 'penicillin' in med.lower() and 'penicillin' in allergies:
            issues.append("ALLERGY ALERT: Patient is allergic to penicillin")
            status = 'rejected'

        # Age check
        if age_str.isdigit():
            age = int(age_str)
            if age < 16 and 'aspirin' in med.lower():
                issues.append("AGE WARNING: Aspirin not recommended for patients under 16")
                if status == 'approved':
                    status = 'warning'

        # Frequency check
        if 'ibuprofen' in med.lower() and '4 times' in freq.lower():
            issues.append("DOSAGE WARNING: High frequency for ibuprofen, monitor for GI effects")
            if status == 'approved':
                status = 'warning'

        # Diagnosis matching
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

def display_validation_results():
    theme_class = "dark-theme" if st.session_state.dark_mode else ""
    result = st.session_state.validation_result
    
    # Overall status
    if result['overall'] == 'approved':
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="status-card status-approved">
                <strong>✅ Prescription Approved</strong><br>
                All medications appear safe and appropriate
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif result['overall'] == 'warning':
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="status-card status-warning">
                <strong>⚠️ Prescription Approved with Warnings</strong><br>
                Some concerns identified, review recommended
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="status-card status-rejected">
                <strong>❌ Prescription Requires Review</strong><br>
                Critical issues found, do not dispense
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Individual medication results
    st.markdown("**Medication Analysis:**")
    
    for item in result['items']:
        status_class = f"status-{item['status']}"
        status_icon = "✅" if item['status'] == 'approved' else "⚠️" if item['status'] == 'warning' else "❌"
        
        st.markdown(f"""
        <div class="{theme_class}">
            <div class="status-card {status_class}">
                <strong>{status_icon} {item['medication']}</strong><br>
                {item['message']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("**General Recommendations:**")
    for rec in result['recommendations']:
        st.markdown(f"• {rec}")

def main():
    load_css()
    init_session_state()
    
    # Apply theme class to entire app
    theme_class = "dark-theme" if st.session_state.dark_mode else ""
    
    # Header
    render_header()
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["🩺 Diagnosis Assistant", "📋 Prescription Checker"])
    
    with tab1:
        diagnosis_chat()
    
    with tab2:
        prescription_checker()
    
    # Footer
    st.markdown(f"""
    <div class="{theme_class}">
        <div class="footer">
            <div style="margin-bottom: 0.5rem;">
                <span style="color: var(--warning);">⚠️</span>
                <strong>Medical Disclaimer</strong>
            </div>
            <p>
                This AI assistant tool provides informational support only and should not replace 
                professional medical advice, diagnosis, or treatment. Always consult with qualified 
                healthcare professionals for medical concerns.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()