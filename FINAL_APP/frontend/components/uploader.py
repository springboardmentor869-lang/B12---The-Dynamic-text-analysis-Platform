import streamlit as st

def render_uploader():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3 style='color: #F2A7B3;'>📂 Source Document</h3>
            <p style='color: #A0A0A0;'>Drag and drop your file below</p>
        </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader(
        "Upload source document",
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )
    
    if file:
        st.success(f"**Selected:** {file.name}")
        
    return file