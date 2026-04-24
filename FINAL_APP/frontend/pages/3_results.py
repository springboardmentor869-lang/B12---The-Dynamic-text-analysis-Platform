import streamlit as st
from services.api_client import get_result
from utils.session import get_task

from components.summary_view import render_summary
from components.sentiment_view import render_sentiment
from components.topic_view import render_topics
from components.overview_view import render_overview

st.set_page_config(page_title="Dashboard | Document Intelligence", layout="wide", page_icon="📈")

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

st.markdown("<h1 style='color: #F2A7B3;'>Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #A0A0A0; margin-bottom: 2rem;'>Comprehensive intelligence report generated from your document</p>", unsafe_allow_html=True)

task_id = get_task()

if not task_id:
    st.error("No result found. Please start again.")
    if st.button("Return to Upload"):
        st.switch_page("pages/1_upload.py")
    st.stop()

with st.spinner("Retrieving analysis data..."):
    data = get_result(task_id)
    result = data.get("result", {})

if not result:
    st.warning("Analysis completed but no data was returned.")
    if st.button("Return to Upload"):
        st.switch_page("pages/1_upload.py")
    st.stop()

# -------- DASHBOARD LAYOUT -------- #

# Check if it's a "Full Analysis" for branding
is_full = "summary" in result and "sentiment" in result and "topics" in result

if is_full:
    st.markdown("""
        <div style='background-color: rgba(242, 167, 179, 0.1); border: 1px solid #F2A7B3; padding: 10px 20px; border-radius: 30px; display: inline-block; margin-bottom: 2rem;'>
            <span style='color: #F2A7B3; font-weight: 600; font-size: 0.9rem;'>✨ COMPLETE INTELLIGENCE REPORT ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)

# Top Bar / Overview
if isinstance(result, dict) and len(result.keys()) > 1:
    render_overview(result)
    st.markdown("<div style='margin-bottom: 4rem;'></div>", unsafe_allow_html=True)

# Main Content
if isinstance(result, dict):
    
    # 1. Summarization
    if "summary" in result:
        summary_data = result["summary"]
        text = summary_data.get("summary", "") if isinstance(summary_data, dict) else summary_data
        render_summary(text)
        st.markdown("<hr style='border: 0; height: 1px; background: linear-gradient(to right, transparent, rgba(242, 167, 179, 0.3), transparent); margin: 5rem 0;'>", unsafe_allow_html=True)

    # 2. Sentiment Analysis
    if "sentiment" in result:
        render_sentiment(result["sentiment"])
        st.markdown("<hr style='border: 0; height: 1px; background: linear-gradient(to right, transparent, rgba(242, 167, 179, 0.3), transparent); margin: 5rem 0;'>", unsafe_allow_html=True)
    
    # 3. Topic Modeling
    if "topics" in result:
        render_topics(result["topics"])

else:
    # Fallback for string results
    render_summary(result)

# Footer Actions
st.markdown("<div style='margin-top: 6rem;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; font-style: italic; font-size: 0.85rem;'>End of generated report • Document Intelligence v2.0</p>", unsafe_allow_html=True)
st.divider()

f_col1, f_col2 = st.columns([1,1])
with f_col1:
    if st.button("🔄 Restart Analysis", use_container_width=True):
        st.switch_page("pages/1_upload.py")
with f_col2:
    if st.button("🧹 Clear", use_container_width=True):
        st.write("Clearing cache...")
        st.switch_page("app.py")