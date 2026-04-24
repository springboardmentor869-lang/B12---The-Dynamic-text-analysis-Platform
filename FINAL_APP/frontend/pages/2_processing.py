import streamlit as st
import time
from components.loader import render_loader
from services.api_client import get_status
from utils.session import get_task

st.set_page_config(page_title="Processing | Document Intelligence", layout="centered", page_icon="⚙️")

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

st.markdown("<h1 style='text-align: center; color: #F2A7B3;'>Analysis Pipeline</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0A0A0; margin-bottom: 3rem;'>Executing linguistic models and extracting structural insights...</p>", unsafe_allow_html=True)

task_id = get_task()

if not task_id:
    st.error("No active task identified. Please return to the source selection page.")
    if st.button("Return to Upload"):
        st.switch_page("pages/1_upload.py")
    st.stop()

# Layout for centering
col1, mid, col2 = st.columns([1, 3, 1])
with mid:
    progress_bar, status_text = render_loader()

    while True:
        try:
            status = get_status(task_id)
        except:
            time.sleep(2)
            continue

        if status["status"] == "completed":
            progress_bar.progress(100)
            status_text.success("Analysis Complete")
            time.sleep(1)
            st.switch_page("pages/3_results.py")
            break
        elif status["status"] == "error":
            progress_bar.progress(100)
            status_text.error(f"Analysis Failed: {status.get('error', 'Critical status mismatch')}")
            if st.button("Try Again"):
                st.switch_page("pages/1_upload.py")
            st.stop()

        progress_msg = status.get("progress_msg", "Initializing modules...")
        progress_pct = status.get("progress_pct", 0)
        
        progress_bar.progress(max(progress_pct, 5))
        status_text.markdown(f"<div style='text-align: center; color: #A0A0A0;'>{progress_msg}</div>", unsafe_allow_html=True)

        time.sleep(2)