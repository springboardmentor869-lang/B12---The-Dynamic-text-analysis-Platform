import streamlit as st

def render_loader():
    # Progress bar and status text container
    st.markdown("""
        <div style='margin-bottom: 1rem;'>
            <p style='color: #F2A7B3; font-weight: 500;' id='status-label'>Analyzing your document...</p>
        </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    return progress_bar, status_text