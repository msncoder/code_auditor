import streamlit as st
import os
import time
from pipeline import pipeline_app

# -----------------------------
# 0. Page Config & Custom CSS
# -----------------------------
st.set_page_config(page_title="AI Code Auditor", page_icon="💻", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4 { color: #E2E8F0; font-family: 'Inter', sans-serif; }
    .step-box {
        padding: 15px; 
        border-radius: 8px; 
        text-align: center; 
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .pending { background-color: #1A202C; color: #718096; border: 1px solid #2D3748; }
    .running { background-color: #2B6CB022; color: #63B3ED; border: 1px solid #3182CE; box-shadow: 0 0 15px rgba(49, 130, 206, 0.3); }
    .completed { background-color: #22543D22; color: #68D391; border: 1px solid #38A169; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# 1. UI Header & Sidebar
# -----------------------------
st.markdown("<h1>💻 Autonomous Code Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #A0AEC0; font-size: 18px;'>Three-stage AI pipeline to scan, refactor, and document your code seamlessly.</p>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.markdown("### 📝 Code Input")
    
    # A messy code snippet to test the pipeline
    default_code = """from fastapi import FastAPI
from sqlalchemy import create_engine
import psycopg2

app = FastAPI()
db = create_engine('postgresql://user:pass@localhost/db')

@app.get('/users')
def get_users(id: int):
    # bad practice: raw query with f-string (SQL injection risk)
    query = f"SELECT * FROM users WHERE id = {id}"
    conn = db.connect()
    res = conn.execute(query)
    return {"data": [dict(row) for row in res]}
"""
    
    user_input = st.text_area("Paste Raw Code Here:", value=default_code, height=350)
    start_btn = st.button("🚀 Execute Audit", use_container_width=True, type="primary")
    
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ GOOGLE_API_KEY is missing in .env")

# -----------------------------
# 2. Pipeline Execution Logic
# -----------------------------
def render_steps(s1, s2, s3):
    cols = st.columns(3)
    classes = {"pending": "pending", "running": "running", "completed": "completed"}
    with cols[0]:
        st.markdown(f"<div class='step-box {classes[s1]}'>1️⃣ Scanner Agent<br><small>{s1.title()}</small></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='step-box {classes[s2]}'>2️⃣ Refactor Agent<br><small>{s2.title()}</small></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='step-box {classes[s3]}'>3️⃣ Docs Agent<br><small>{s3.title()}</small></div>", unsafe_allow_html=True)

if start_btn and user_input.strip():
    st.markdown("### 🔄 Workflow Tracker")
    tracker = st.empty()
    tracker.container().write(render_steps("running", "pending", "pending"))
    
    st.divider()
    st.markdown("### 📊 Pipeline Outputs")
    
    # Vertical Top-to-Bottom Layout
    box1 = st.empty()
    box2 = st.empty()
    box3 = st.empty()
    
    with st.spinner("Pipeline is running..."):
        for event in pipeline_app.stream({"raw_code": user_input}):
            for node_name, state in event.items():
                time.sleep(0.5) 
                
                if node_name == "scanner":
                    tracker.empty()
                    with tracker.container(): render_steps("completed", "running", "pending")
                    with box1.container():
                        st.markdown("#### 🛡️ Stage 1: Security & Audit Report")
                        st.error(state["audit_report"])
                        
                elif node_name == "refactor":
                    tracker.empty()
                    with tracker.container(): render_steps("completed", "completed", "running")
                    with box2.container():
                        st.markdown("#### 🛠️ Stage 2: Refactored & Optimized Code")
                        st.code(state["optimized_code"], language="python")
                        
                elif node_name == "doc":
                    tracker.empty()
                    with tracker.container(): render_steps("completed", "completed", "completed")
                    with box3.container():
                        st.markdown("#### 📄 Stage 3: Auto-Generated Documentation")
                        st.success(state["documentation"])

    st.toast("✅ Code Audit Completed Successfully!")

elif start_btn:
    st.sidebar.warning("Please paste some code first!")
else:
    st.info("👈 Paste your code in the sidebar and run the pipeline.")
    tracker = st.empty()
    with tracker.container():
        render_steps("pending", "pending", "pending")