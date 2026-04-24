import streamlit as st

def render_analysis_selector():
    st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <h3 style='color: #F2A7B3;'>⚙️ Analysis Configuration</h3>
            <p style='color: #A0A0A0;'>Choose the modules you want to run</p>
        </div>
    """, unsafe_allow_html=True)

    # Use a radio with horizontal styling for a pill-like feel
    mode = st.radio(
        "Select Service Module",
        options=["summary", "sentiment", "topics", "full"],
        format_func=lambda x: x.capitalize(),
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Map friendly names back to internal keys if needed
    # For now, keys are already friendly
    
    return mode