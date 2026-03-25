import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"
API_KEY = "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0"

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
# MODERN UI CSS
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
    padding-bottom: 2rem;
}

/* QUICK QUESTIONS */
.quick-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* ✅ FIXED ROLE TEXT */
.quick-sub {
    color: #000000;   /* Force black */
    font-size: 18px;  /* Increased size */
    font-weight: 700;
    margin-bottom: 8px;
}

.quick-card button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 14px;
    background: #f9fafb;
    font-weight: 600;
    text-align: left;
}

.quick-card button:hover {
    background: #eef2ff;
}

[data-testid="stForm"] {
    background: #ffffff;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.stTextArea textarea {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
    padding: 12px !important;
    font-size: 15px !important;
}

button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
    padding: 0.7em 1.4em;
    font-weight: 600;
    border: none;
}

button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-top:20px;">
    <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png" width="240">
    <br><br>
    <a href="https://www.allotltd.com/"
        style="text-decoration:none; font-size:20px; color:#2563eb;">
        www.allotltd.com
    </a>
</div>
<hr style="margin-top: 2em; opacity:0.3;">
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div style="
    text-align:center;
    padding:30px 20px;
    background: linear-gradient(90deg, #2563eb, #1e40af);
    border-radius:16px;
    color:white;
    margin-bottom:20px;
">
    <h1>💬 NBA for Oncology</h1>
    <p>Next Best Actions for England Healthcare</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# QUICK QUESTIONS
# -----------------------------
st.markdown('<div class="quick-title">💡 Quick Questions</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="quick-sub">Key Account Manager</div>', unsafe_allow_html=True)
    if st.button("📊 Top-performing accounts", key="q1"):
        st.session_state.prompt = "What are the top-performing accounts and what behaviours are driving success?"
        st.session_state.role = "Key Account Manager"

    if st.button("📊 High patient potential", key="q2"):
        st.session_state.prompt = "Which HCPs or HCOs show high patient potential but low engagement based on call activity and sales data?"
        st.session_state.role = "Key Account Manager"

    st.markdown('<div class="quick-sub">Medical Science Liaison (MSL)</div>', unsafe_allow_html=True)
    if st.button("📉 Low engagement HCPs", key="q3"):
        st.session_state.prompt = "Which HCPs show high patient potential but low engagement?"
        st.session_state.role = "Medical Science Liaison (MSL)"

with col2:
    st.markdown('<div class="quick-sub">Market Access Representative</div>', unsafe_allow_html=True)
    if st.button("🏥 Formulary uptake issues", key="q4"):
        st.session_state.prompt = "Which regions show delayed formulary uptake despite NICE guidance?"
        st.session_state.role = "Market Access Representative"

    st.markdown('<div class="quick-sub">Commercial Director</div>', unsafe_allow_html=True)
    if st.button("🧪 NICE alignment", key="q5"):
        st.session_state.prompt = "Which HCPs show low alignment with NICE guidelines?"
        st.session_state.role = "Commercial Director"

st.write("")

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form", clear_on_submit=False):

    st.subheader("💬 Ask a question")

    prompt = st.text_area(
        "",
        value=st.session_state.prompt,
        placeholder="Type your question here...",
        height=120
    )

    st.subheader("👤 Select your role")

    role = st.radio(
        "",
        [
            "Key Account Manager",
            "Market Access Representative",
            "Medical Science Liaison (MSL)",
            "Commercial Director"
        ],
        index=[
            "Key Account Manager",
            "Market Access Representative",
            "Medical Science Liaison (MSL)",
            "Commercial Director"
        ].index(st.session_state.role)
    )

    submitted = st.form_submit_button("🚀 Get Insight")

# -----------------------------
# API CALL
# -----------------------------
if submitted and prompt.strip():

    with st.spinner("🔍 Analysing oncology data..."):

        payload = [{"question_type": role, "prompt": prompt}]
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and "Customer_Story" in data[0]:
                reply = data[0]["Customer_Story"]
            else:
                reply = f"Unexpected API response format: {data}"

        except Exception as e:
            reply = f"⚠️ Error: {e}"

    st.markdown("### 💡 Insight")

    st.markdown(f"""
    <div style="
        background:#ffffff;
        padding:20px;
        border-radius:14px;
        border:1px solid #e5e7eb;
        box-shadow:0 4px 12px rgba(0,0,0,0.04);
        margin-top:10px;
    ">
        <p style="line-height:1.6;">
            {reply}
        </p>
    </div>
    """, unsafe_allow_html=True)

elif submitted and not prompt.strip():
    st.warning("Please enter a question before sending.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr style="margin-top: 3em; opacity:0.2;">
<p style="text-align:center; font-size: 0.85em; color: #9ca3af;">
© 2026 NBA Oncology | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
