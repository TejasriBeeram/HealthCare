import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"

# Try secrets first, fallback to manual key
API_KEY = st.secrets.get("API_KEY", None)

# 👉 PUT YOUR API KEY HERE if you don’t use secrets
if not API_KEY:
    API_KEY = "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0"

# If still missing, warn user but don't crash
if not API_KEY or API_KEY == "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0":
    st.warning("⚠️ API key is missing. Please add it to run API calls.")

st.set_page_config(
    page_title="NBA for Oncology in England",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# SESSION STATE
# -----------------------------
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "role" not in st.session_state:
    st.session_state.role = "Key Account Manager"

# -----------------------------
# UI STYLES
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
    color: #111827;
    font-family: 'Inter', sans-serif;
}
.block-container {
    max-width: 700px;
    padding-top: 2rem;
}
button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div style="text-align:center;">
    <h1>💬 NBA for Oncology</h1>
    <p>Next Best Actions for Healthcare</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):

    prompt = st.text_area(
        "Ask your question",
        value=st.session_state.prompt,
        placeholder="Type your question here...",
        height=120
    )

    roles = [
        "Key Account Manager",
        "Market Access Representative",
        "Medical Science Liaison (MSL)",
        "Commercial Director"
    ]

    role = st.radio(
        "Select your role",
        roles,
        index=roles.index(st.session_state.role)
    )

    submitted = st.form_submit_button("🚀 Get Insight")

# -----------------------------
# API CALL
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question.")

    elif not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
        st.error("❌ Cannot call API. API key is missing.")

    else:
        with st.spinner("Analyzing oncology data..."):

            payload = [{
                "question_type": role,
                "prompt": prompt
            }]

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code != 200:
                    raise Exception(f"{response.status_code}: {response.text}")

                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("Customer_Story", str(data[0]))
                elif isinstance(data, dict):
                    reply = data.get("Customer_Story", str(data))
                else:
                    reply = str(data)

            except Exception as e:
                reply = f"❌ API Error: {str(e)}"

        st.markdown("### 💡 Insight")
        st.write(reply)

        # reset prompt
        st.session_state.prompt = ""

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr>
<p style="text-align:center; font-size: 0.8em;">
© 2026 NBA Oncology
</p>
""", unsafe_allow_html=True)
