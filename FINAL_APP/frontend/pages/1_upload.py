import streamlit as st
from components.uploader import render_uploader
from components.analysis_selector import render_analysis_selector
from services.api_client import send_file
from utils.session import set_task

st.set_page_config(page_title="Submission | Document Intelligence", layout="wide", page_icon="📂")

# Inject Custom CSS
try:
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

st.markdown("<h1 style='text-align: center; color: #F2A7B3;'>Submission Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0A0A0; margin-bottom: 3rem;'>Prepare your document for advanced linguistic processing</p>", unsafe_allow_html=True)

container = st.container()

with container:
    col1, mid, col2 = st.columns([1, 2, 1])
    with mid:
        file = render_uploader()
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        mode = render_analysis_selector()
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        if st.button("Analyze Document"):
            if not file:
                st.warning("Please upload a file first")
            else:
                with st.status("Initializing Analysis Node...", expanded=True) as status:
                    st.write("Uploading document to secure analysis pipeline...")
                    task_id = send_file(file, mode)
                    st.write("Resource allocated. Task ID assigned.")
                    set_task(task_id)
                    status.update(label="Upload successful!", state="complete", expanded=False)
                
                st.switch_page("pages/2_processing.py")