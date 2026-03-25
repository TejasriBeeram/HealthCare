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
# MODERN UI CSS
# -----------------------------
st.markdown("""
<style>

/* Background */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
    color: #111827;
    font-family: 'Inter', sans-serif;
}

/* Center layout */
.block-container {
    max-width: 700px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Form Card */
[data-testid="stForm"] {
    background: #ffffff;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

/* Inputs */
.stTextArea textarea {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Button */
button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 10px;
    padding: 0.7em 1.4em;
    font-weight: 600;
    border: none;
    transition: all 0.2s ease;
}

button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}

/* Quick buttons */
button[kind="secondary"] {
    border-radius: 10px !important;
    border: 1px solid #e5e7eb !important;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# ALLOT HEADER (RESTORED)
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:20px;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png"
             alt="Allot Logo" width="240">
        <br><br>
        <a href="https://www.allotltd.com/"
            style="text-decoration:none; font-size:20px; color:#2563eb; font-weight:500;">
            www.allotltd.com
        </a>
    </div>
    <hr style="margin-top: 2em; opacity:0.3;">
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HERO HEADER
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
    <h1 style="margin-bottom:5px;">💬 NBA for Oncology</h1>
    <p style="opacity:0.9;">Next Best Actions for England Healthcare</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# OVERVIEW (UNCHANGED, JUST COLLAPSIBLE)
# -----------------------------
with st.expander("📘 Overview"):
    st.markdown("""
This application delivers Next Best Actions (NBAs) to support pharmaceutical commercial, sales, market access, and medical field teams.

### Data Scope
- Call Notes Data – Internal  
- Sales Data – Internal  
- Call Activity Data – Internal  
- HCO & HCP Data – NHS sources  
- Healthcare System Assessment Data – Internal and external  
- NICE Guidelines  
- Treatment Pathways  
- Formulary Data  
""")

# -----------------------------
# SAMPLE QUESTIONS (NEW)
# -----------------------------
st.markdown("### 💡 Quick Questions")

col1, col2 = st.columns(2)

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

with col1:
    if st.button("📊 Top-performing accounts"):
        st.session_state.prompt = "What are the top-performing accounts, and what behaviours are driving success?"

    if st.button("📉 Low engagement HCPs"):
        st.session_state.prompt = "Which HCPs show high patient potential but low engagement?"

with col2:
    if st.button("🏥 Formulary uptake issues"):
        st.session_state.prompt = "Which regions show delayed formulary uptake despite NICE guidance?"

    if st.button("🧪 NICE alignment"):
        st.session_state.prompt = "Which HCPs show low alignment with NICE guidelines?"

st.write("")

# -----------------------------
# INPUT FORM (UNCHANGED LOGIC)
# -----------------------------
with st.form("chat_form", clear_on_submit=False):

    st.subheader("💬 Ask a question")
    prompt = st.text_area(
        "",
        value=st.session_state.get("prompt", ""),
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
        index=0
    )

    submitted = st.form_submit_button("🚀 Get Insight")

# -----------------------------
# PROCESS SUBMISSION (UNCHANGED)
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

    # -----------------------------
    # RESPONSE CARD (IMPROVED UI)
    # -----------------------------
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
        <p style="line-height:1.6; font-size:15px;">
            {reply}
        </p>
    </div>
    """, unsafe_allow_html=True)

elif submitted and not prompt.strip():
    st.warning("Please enter a question before sending.")

# -----------------------------
# FOOTER (UNCHANGED)
# -----------------------------
st.markdown("""
<hr style="margin-top: 3em; opacity:0.2;">
<p style="text-align:center; font-size: 0.85em; color: #9ca3af;">
© 2026 NBA Oncology | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
