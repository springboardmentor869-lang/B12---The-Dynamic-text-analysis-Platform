import streamlit as st

st.set_page_config(
    page_title="Document Intelligence Analyzer",
    page_icon="📄",
    layout="wide"
)

# Inject Custom CSS
try:
    with open("frontend/assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    # Fallback if path is different (sometimes streamlit runs from frontend dir)
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

# Hero Section
st.markdown("""
<div class="centered-text fade-in" style="margin-top: 5rem;">
    <h1 style="color: #F2A7B3 !important; text-shadow: 0 0 20px rgba(242, 167, 179, 0.3); font-size: 4rem;">Document Intelligence Analyzer</h1>
    <p class="subtitle">Upload your document and extract insights instantly with high-performance AI.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Begin Analysis"):
        st.switch_page("pages/1_upload.py")