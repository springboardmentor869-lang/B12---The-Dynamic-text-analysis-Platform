import streamlit as st

def render_summary(summary):
    st.markdown("<h2 style='color: #F2A7B3; margin-bottom: 0.5rem;'>📝 Executive Summary</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0A0A0; margin-bottom: 1.5rem;'>A high-level synthesis of core document insights and key takeaways</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class='custom-card' style='border-left: 5px solid #F2A7B3; background: linear-gradient(145deg, #2A2A2A 0%, #1A1A1A 100%);'>
            <div style='line-height: 1.8; color: #EDEDED; font-size: 1.15rem; font-weight: 400;'>
                {summary}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📋 Copy", key="copy_summary"):
            st.toast("Summary copied!")