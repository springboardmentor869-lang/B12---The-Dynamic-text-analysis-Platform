import streamlit as st
import pandas as pd

def render_sentiment(data):
    st.markdown("<h2 style='color: #F2A7B3; margin-bottom: 0.5rem;'>🎭 Sentiment Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0A0A0; margin-bottom: 1.5rem;'>Emotional tone discovery and linguistic pattern identification</p>", unsafe_allow_html=True)

    # Metrics section in cards
    col1, col2, col3, col4 = st.columns(4)
    sentence_results = data.get("sentence_results", [])
    sentences_scanned = len(sentence_results)
    total_in_doc = data.get("total_sentences", sentences_scanned)

    with col1:
        st.metric("Positive", data.get("positive", 0))
    with col2:
        st.metric("Neutral", data.get("neutral", 0))
    with col3:
        st.metric("Negative", data.get("negative", 0))
    with col4:
        st.metric("Scanned", f"{sentences_scanned}/{total_in_doc}")

    # Verdict section
    verdict = data.get("overall_sentiment", "Neutral")
    verdict_color = "#4CAF50" if "positive" in verdict.lower() else "#F44336" if "negative" in verdict.lower() else "#9E9E9E"
    
    st.markdown(f"""
        <div style='background-color: {verdict_color}22; border-left: 5px solid {verdict_color}; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;'>
            <h4 style='margin: 0; color: {verdict_color};'>Analysis Verdict: {verdict.capitalize()}</h4>
            <p style='margin: 0.5rem 0 0 0; color: #EDEDED;'>The document exhibits a predominantly {verdict.lower()} tone based on linguistic patterns.</p>
        </div>
    """, unsafe_allow_html=True)

    # Details section
    st.markdown("<h3 style='color: #F2A7B3; margin-top: 2rem;'>📌 Sentence-Level Breakdown</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0A0A0; margin-bottom: 1rem;'>Showing highest confidence indicators</p>", unsafe_allow_html=True)

    # Show only top 15 sentences for clarity
    for item in sentence_results[:15]:
        label = item["label"]
        score = item["score"]
        sentence = item["sentence"]
        
        color = "#4CAF50" if "positive" in label.lower() else "#F44336" if "negative" in label.lower() else "#9E9E9E"
        badge_text = "Happy" if "positive" in label.lower() else "Sad" if "negative" in label.lower() else "Neutral"
        
        st.markdown(f"""
            <div style='background-color: #2A2A2A; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                    <span style='background-color: {color}33; color: {color}; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;'>{badge_text} ({score:.2f})</span>
                </div>
                <p style='margin: 0; color: #EDEDED; font-size: 0.95rem;'>{sentence}</p>
            </div>
        """, unsafe_allow_html=True)
    
    if len(sentence_results) > 15:
        st.markdown(f"<p style='text-align: center; color: #A0A0A0;'>... and {len(sentence_results) - 15} more sentences</p>", unsafe_allow_html=True)