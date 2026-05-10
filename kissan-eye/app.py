import streamlit as st
from src.pdf_loader import load_pdfs_from_folder, extract_text_from_images, truncate_context
from src.gemini_agent import KissanAgent
from src.tts_engine import speak, sanitize_for_speech
from PIL import Image
from dotenv import load_dotenv
import io
import os

# Load .env file for local development
load_dotenv()

API_KEY = (
    st.secrets.get("GEMINI_API_KEY")   # local dev
    or os.environ.get("GEMINI_API_KEY") # Cloud Run
    or ""
)

if not API_KEY:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Kissan-Eye | کسان آئی", page_icon="", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "diagnosis_result" not in st.session_state:
    st.session_state.diagnosis_result = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "resource_info" not in st.session_state:
    st.session_state.resource_info = None

if "pdf_context" not in st.session_state:
    with st.spinner(" Knowledge base load ho rahi hai..."):
        
        # Load text PDFs
        pdf_text, pdf_count, pdf_names = load_pdfs_from_folder(
            "data/pdfs/"
        )

        # Load image-based brochures via Gemini Vision OCR
        image_text = extract_text_from_images(
            "data/images/",
            api_key=API_KEY
        )

        # Combine both sources
        combined = pdf_text + "\n\n" + image_text
        st.session_state["pdf_context"] = truncate_context(combined)
        st.session_state["pdf_count"]   = pdf_count
        st.session_state["img_count"]   = image_text.count(
            "(image OCR)"
        )
        st.session_state["pdf_names"]   = pdf_names

# Sidebar knowledge base status
st.sidebar.metric(
    " Knowledge Base",
    f"{st.session_state['pdf_count']} PDFs + "
    f"{st.session_state['img_count']} Brochures",
    delta="Active"
)

# --- SIDEBAR ---
with st.sidebar:
    st.title(" Kissan-Eye")
    st.caption("KP Kisano ka AI Dost")
    
    uploaded_file = st.file_uploader(
        label="Fasal ki Tasweer Upload Karein", 
        type=["jpg", "jpeg", "png"], 
        key="crop_image"
    )
    
    user_desc = st.text_area(
        label="Masla Bataein (Roman Urdu mein)", 
        placeholder="Misal: Pattay peele ho rahe hain aur dhabbe hain...",
        height=100, 
        key="user_desc"
    )
    
    diagnose_btn = st.button(" Diagnosis Karein", key="diagnose_btn")
    
    st.divider()
    st.caption("Powered by Gemini Flash 2.5 + KP Govt Data")

# --- MAIN AREA ---
st.header("کسان آئی — Kissan-Eye")
st.subheader("Apni Fasal ki Tasweer Upload Karein, AI Diagnose Karega")

col1, col2 = st.columns([1, 1])

with col1:
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Fasal", use_container_width=True)
    else:
        st.info("← Tasweer upload karein")

# --- LOGIC ---
if diagnose_btn:
    if not uploaded_file:
        st.warning("Pehle tasweer upload karein!")
    else:
        with st.spinner("AI Soch raha hai... "):
            try:
                # 1. Use session state context
                pdf_context = st.session_state.get("pdf_context", "")
                
                # 2. Init Agent
                agent = KissanAgent(pdf_context=pdf_context)
                
                # 3. Read image bytes
                image_bytes = uploaded_file.getvalue()
                
                # 4. Diagnose
                result = agent.diagnose(image_bytes, user_desc)
                
                # Double-safety: sanitize before display AND before speech
                clean_result = sanitize_for_speech(result)
                st.session_state.diagnosis_result = clean_result
                
                # 5. TTS
                st.session_state.audio_bytes = speak(result)
                
                # Reset resource info on new diagnosis
                st.session_state.resource_info = None
                
            except Exception as e:
                st.error(f"Khata hui: {e}")

# --- DISPLAY RESULTS ---
with col2:
    if st.session_state.diagnosis_result:
        st.success("AI ka Jawab:")
        st.write(st.session_state.diagnosis_result)
        
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")
        else:
            st.warning(" Awaaz generate nahi ho saki.")
        
        st.divider()
        
        st.info("Kya aap chahte hain ke main qareeb-i zirai markaz dhundhun? (Type 'haan' below)")
        followup = st.text_input("Jawab likhein:", key="followup_input")
        
        if followup.lower() == "haan":
            try:
                agent = KissanAgent(pdf_context="")
                st.session_state.resource_info = agent.find_resource_center("Aap ka Masla")
            except Exception as e:
                st.error(f"Resource center dhundhne mein masla: {e}")
            
        if st.session_state.resource_info:
            st.info(st.session_state.resource_info)
    else:
        st.write("Results yahan dikhaye jayenge...")
