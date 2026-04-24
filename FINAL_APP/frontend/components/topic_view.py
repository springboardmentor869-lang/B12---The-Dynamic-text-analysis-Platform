import streamlit as st
import pandas as pd

def render_topics(data):
    st.markdown("<h2 style='color: #F2A7B3; margin-bottom: 0.5rem;'>🧠 Topic Distribution</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #A0A0A0; margin-bottom: 1.5rem;'>Key themes and clusters identified across document segments</p>", unsafe_allow_html=True)

    topics_all = data.get("topics", {})
    chunks = data.get("chunks", [])
    
    if not topics_all:
        st.info("No topics identified.")
        return

    # 1. TOPIC LIST & DOMINANT TOPIC CALCULATION
    sorted_topics = sorted(topics_all.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    dominant_id, dominant_info = sorted_topics[0] if sorted_topics else (None, None)

    # Metrics Row
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Total Topics", len([t for t in topics_all.keys() if str(t) != "-1"]))
    with col_m2:
        outlier_count = topics_all.get("-1", {}).get("count", 0) or topics_all.get(-1, {}).get("count", 0)
        st.metric("Unmapped Segments", outlier_count)

    # 2. DOMINANT TOPIC CONTAINER
    if dominant_info and str(dominant_id) != "-1":
        label = dominant_info.get("label", f"Topic {dominant_id}")
        st.markdown(f"""
            <div style='background: linear-gradient(90deg, rgba(242, 167, 179, 0.15) 0%, rgba(242, 167, 179, 0.05) 100%); 
                        padding: 1.5rem; border-radius: 12px; border: 1px solid #F2A7B3; margin: 2rem 0;'>
                <h4 style='margin: 0; color: #F2A7B3; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;'>Dominant Theme Identified</h4>
                <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700; color: #EDEDED;'>{label}</p>
                <p style='margin: 0.2rem 0 0 0; color: #A0A0A0;'>This theme appears in {dominant_info.get("count", 0)} segments.</p>
            </div>
        """, unsafe_allow_html=True)

    # 3. DISTRIBUTION CHART
    st.markdown("<h3 style='color: #F2A7B3; margin-top: 2.5rem; font-size: 1.2rem;'>📊 Topic Volume</h3>", unsafe_allow_html=True)
    chart_data = []
    for tid, info in topics_all.items():
        if str(tid) == "-1": continue
        label = info.get("label", f"Topic {tid}")
        chart_data.append({"Topic": label, "Count": info.get("count", 0)})
    
    if chart_data:
        df = pd.DataFrame(chart_data)
        st.bar_chart(df.set_index("Topic"), color="#F2A7B3")

    # 5. DETAILED INSPECTION (EXPANDERS)
    st.markdown("<h3 style='color: #F2A7B3; margin-top: 2.5rem; font-size: 1.2rem;'>🔍 Segment Analysis</h3>", unsafe_allow_html=True)
    
    for tid_key, info in sorted_topics:
        tid = int(tid_key)
        label = info.get("label", f"Cluster {tid}")
        if tid == -1: label = "Outlier Content"
        
        raw_name = info.get("name", "")
        count = info.get("count", 0)
        keywords = raw_name.split("_")[1:] if "_" in raw_name else []
        
        with st.expander(f"{label} ({count} segments)"):
            if keywords:
                st.markdown(" ".join([f"<span style='background-color: #F2A7B322; color: #F2A7B3; padding: 2px 10px; border-radius: 15px; font-size: 0.75rem; margin-right: 5px; border: 1px solid rgba(242,167,179,0.3);'>#{w}</span>" for w in keywords[:10]]), unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            topic_chunks = [c["chunk"] for c in chunks if int(c.get("topic_id", -99)) == tid]
            
            for snippet in topic_chunks[:3]:
                st.markdown(f"""
                    <div style='background-color: rgba(255,255,255,0.02); padding: 0.8rem; border-radius: 8px; border-left: 2px solid #F2A7B3; margin-bottom: 0.5rem;'>
                        <p style='margin: 0; font-size: 0.85rem; font-style: italic; color: #CCCCCC;'>"... {snippet} ..."</p>
                    </div>
                """, unsafe_allow_html=True)