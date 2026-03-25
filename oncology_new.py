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

/* Radio buttons spacing */
.stRadio > div {
    gap: 10px;
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

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: 16px;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

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
# COLLAPSIBLE OVERVIEW
# -----------------------------
with st.expander("📘 About this tool"):
    st.markdown("""
This application delivers Next Best Actions (NBAs) to support pharmaceutical commercial, sales, market access, and medical field teams.

**Focus:**
- Lung cancer oncology in England

**Data Sources:**
- Call Notes, Sales, Activity Data
- NHS HCP & HCO data
- NICE Guidelines
- Treatment pathways
- Formulary data (Oxfordshire, NEL, NHS England)
""")

st.write("")

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form", clear_on_submit=False):

    st.subheader("💬 Ask a question")
    prompt = st.text_area("", placeholder="Type your question here...", height=120)

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
# PROCESS
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
    # RESPONSE CARD
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
# FOOTER
# -----------------------------
st.markdown("""
<hr style="margin-top: 3em; opacity:0.2;">
<p style="text-align:center; font-size: 0.85em; color: #9ca3af;">
© 2026 NBA Oncology | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
