import streamlit as st

def render_overview(data):
    st.markdown("""
        <div style='display: flex; gap: 1rem; align-items: center; margin-bottom: 2rem;'>
            <div style='background-color: #F2A7B3; width: 5px; height: 30px; border-radius: 5px;'></div>
            <h3 style='margin: 0; color: #EDEDED;'>Executive Intelligence Overview</h3>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    
    if "summary" in data:
        with cols[0]:
            st.markdown("""
                <div style='background-color: #2A2A2A; padding: 1rem; border-radius: 10px; border: 1px solid rgba(242, 167, 179, 0.1); text-align: center;'>
                    <span style='font-size: 1.5rem;'>📄</span>
                    <p style='margin: 0.5rem 0 0 0; font-weight: 600; color: #F2A7B3;'>Summary</p>
                    <p style='margin: 0; font-size: 0.8rem; color: #A0A0A0;'>Extracted</p>
                </div>
            """, unsafe_allow_html=True)

    if "sentiment" in data:
        with cols[1]:
            st.markdown("""
                <div style='background-color: #2A2A2A; padding: 1rem; border-radius: 10px; border: 1px solid rgba(242, 167, 179, 0.1); text-align: center;'>
                    <span style='font-size: 1.5rem;'>🎭</span>
                    <p style='margin: 0.5rem 0 0 0; font-weight: 600; color: #F2A7B3;'>Sentiment</p>
                    <p style='margin: 0; font-size: 0.8rem; color: #A0A0A0;'>Mapped</p>
                </div>
            """, unsafe_allow_html=True)

    if "topics" in data:
        with cols[2]:
            st.markdown("""
                <div style='background-color: #2A2A2A; padding: 1rem; border-radius: 10px; border: 1px solid rgba(242, 167, 179, 0.1); text-align: center;'>
                    <span style='font-size: 1.5rem;'>🧠</span>
                    <p style='margin: 0.5rem 0 0 0; font-weight: 600; color: #F2A7B3;'>Topics</p>
                    <p style='margin: 0; font-size: 0.8rem; color: #A0A0A0;'>Clustered</p>
                </div>
            """, unsafe_allow_html=True)