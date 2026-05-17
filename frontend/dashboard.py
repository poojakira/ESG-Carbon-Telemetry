import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import joblib
import os
from datetime import datetime

st.set_page_config(
    page_title="EcoTrack Enterprise Pro | Industrial Sustainability ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Corrected Paths for the Workspace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "backend", "data", "dpp_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "backend", "data", "model.pkl")
SECURITY_MODEL_PATH = os.path.join(BASE_DIR, "backend", "data", "security_model.pkl")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

import sys

if st.runtime.scriptrunner.get_script_run_ctx() is None:
    # Bare execution – avoid running the UI logic altogether
    print("Dashboard script executed outside of Streamlit.\n" \
          "Please start with `streamlit run dashboard.py` to launch the app.")
    sys.exit(0)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    
    :root {
        --primary: #10B981;
        --secondary: #3B82F6;
        --accent: #F59E0B;
        --background: #020617;
        --surface: rgba(15, 23, 42, 0.6);
        --text: #F8FAFC;
    }

    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        color: var(--text);
        background-color: var(--background);
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, rgba(16, 185, 129, 0.15), transparent),
                    radial-gradient(circle at 0% 100%, rgba(59, 130, 246, 0.1), transparent);
    }

    h1, h2, h3 { 
        font-family: 'Outfit', sans-serif !important; 
        letter-spacing: -0.03em;
    }

    /* Glassmorphism Evolution */
    div[data-testid="metric-container"], .stDataFrame, .stPlotlyChart, div[data-testid="stExpander"] {
        background: var(--surface) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--surface);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #94A3B8;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(16, 185, 129, 0.2) !important;
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* Terminal Font for Ledger */
    .ledger-hash {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94A3B8;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.1);
        color: var(--primary);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid var(--primary);
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

import requests

if 'token' not in st.session_state:
    st.session_state.token = None

def login_ui():
    with st.sidebar:
        st.markdown("### 🔐 Nexus Authentication")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Unlock Terminal"):
            try:
                r = requests.post(f"{BACKEND_URL}/api/v1/auth/login", data={"username": user, "password": pwd})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.success("Access Granted.")
                    st.rerun()
                else:
                    st.error("Invalid Credentials.")
            except Exception as e:
                st.error("Backend unavailable.")

if not st.session_state.token:
    st.title("EcoTrack Enterprise")
    st.info("Industrial Data Nexus Initializing... **Authentication Required**")
    login_ui()
    st.stop()

@st.cache_data(ttl=10)
def fetch_api_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        metrics = requests.get(f"{BACKEND_URL}/api/v1/metrics", headers=headers, timeout=5).json()
        trends = requests.get(f"{BACKEND_URL}/api/v1/analytics/trends", headers=headers, timeout=5).json()
        audit = requests.get(f"{BACKEND_URL}/api/v1/ledger/audit-log", headers=headers, timeout=5).json()
        recs = requests.get(f"{BACKEND_URL}/api/v1/recommendations", headers=headers, timeout=5).json()
        ledger_csv = requests.get(f"{BACKEND_URL}/api/v1/ledger/export", headers=headers, timeout=5).text
        from io import StringIO
        df = pd.read_csv(StringIO(ledger_csv))
        return df, metrics, trends, audit, recs
    except Exception as e:
        st.error(f"Data synchronization failed: {e}")
        return pd.DataFrame(), None, None, [], None

df, api_metrics, api_trends, api_audit, api_recs = fetch_api_data(st.session_state.token)



c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(f"# EcoTrack <span style='color:{'#10B981'}'></span>", unsafe_allow_html=True)
    st.caption(f"Enterprise Data Nexus v8.0.0 | High-Throughput Streaming Active")
with c2:
    if st.button("🔴 Terminate Session"):
        st.session_state.token = None
        st.rerun()

t1, t2, t3, t4, t5 = st.tabs(["📊 Executive Command", "⛓️ Merkle Ledger", "🛡️ AI Security", "🤖 MLOps Terminal", "💡 Action Center"])

with t1:
    if api_metrics:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Net Carbon Liability", f"{api_metrics['total_co2']:.1f} kg")
        m2.metric("Avg Intensity", f"{api_metrics['avg_intensity']:.2f}")
        m3.metric("Active Regions", str(len(api_metrics.get('region_breakdown', {}))))
        m4.metric("Status", "CONNECTED")

    st.divider()
    
    if not df.empty:
        fig = px.area(df, x='Timestamp', y='total_lifecycle_carbon_footprint', 
                      title="Real-Time Carbon Velocity",
                      color_discrete_sequence=['#10B981'],
                      template='plotly_dark')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

with t2:
    st.markdown("### 🧬 Cryptographic Chain Verification")
    colA, colB = st.columns([1, 2])
    
    with colA:
        if st.button("🛡️ Execute Full Ledger Audit"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{BACKEND_URL}/api/v1/ledger/verify-chain", headers=headers).json()
            if res['status'] == "SECURE":
                 st.success("💎 ALL BLOCKS VALIDATED")
                 st.json(res)
            else:
                 st.error("🚨 INTEGRITY BREACH DETECTED")

    with colB:
        st.markdown("**Recent Audit Batches**")
        if api_audit:
            for entry in api_audit[:3]:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:4px solid #10B981;'>
                    <span style='font-size:0.8rem; opacity:0.6;'>Batch ID: {entry['batch_id']} | Operator: {entry['operator']}</span><br/>
                    <code style='color:#10B981; font-size:0.7rem;'>Root: {entry['merkle_root'][:32]}...</code>
                </div>
                """, unsafe_allow_html=True)

    st.dataframe(df[['Timestamp', 'Product_ID', 'SKU_Name', 'total_lifecycle_carbon_footprint', 'Hash']].tail(50), use_container_width=True)

with t3:
    st.markdown("### 🚨 Threat Intelligence")
    anomalies = df[df['is_anomaly'] == 1]
    if not anomalies.empty:
        st.error(f"Detected {len(anomalies)} Security Anomalies in Current Ledger.")
        st.dataframe(anomalies, use_container_width=True)
    else:
        st.success("No anomalies detected. AI Guardian is STABLE.")

with t4:
    st.markdown("### ⚙️ MLOps Operational Node")
    st.info("Automated Retraining & Drift Monitoring active for `MLEngine-v3`")
    
    if api_trends:
        st.markdown("#### Feature Distribution Drift")
        # Simplified view for UI
        st.write("Data drift detection not yet implemented — requires baseline distribution from production data.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Vendor Performance**")
            st.json(api_trends['vendor_performance'])
        with c2:
            st.markdown("**Category Dynamics**")
            st.json(api_trends['category_trends'])

with t5:
    st.markdown("### 💡 Sustainability Action Center")
    if api_recs:
        st.markdown(f"**Overall Sustainability Index**: `{api_recs['overall_sustainability_index']}/100`")
        
        # Action Grid
        for rec in api_recs['recommendations']:
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{rec['action']}**")
                    st.caption(f"Category: {rec['category']} | ID: {rec['id']}")
                with c2:
                    st.markdown(f"Impact: **{int(rec['impact_score']*100)}%**")
                    st.progress(rec['impact_score'])
                with c3:
                    st.markdown(f"Est. Savings: **{rec['savings_est_kg']} kg**")
                    st.markdown(f"<span class='status-badge'>{rec['complexity']} Complexity</span>", unsafe_allow_html=True)
                st.divider()
    else:
        st.warning("Insufficient telemetry for optimization analysis.")

st.sidebar.divider()
st.sidebar.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.7rem;'>
    EcoTrack v1.0.0
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    # When Streamlit executes a script it does so under __main__.  The
    # early exit above will have already handled bare execution, so this
    # block is mostly harmless and can serve as a gentle reminder if
    # someone accidentally runs the file twice.
    print("Note: launch the user interface with `streamlit run dashboard.py`")
