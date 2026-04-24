import streamlit as st

def set_task(task_id):
    st.session_state["task_id"] = task_id

def get_task():
    return st.session_state.get("task_id")