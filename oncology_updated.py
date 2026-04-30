import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"
API_KEY = st.secrets.get("API_KEY", "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0"

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

.quick-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
}

.quick-sub {
    color: #000000;
    font-size: 18px;
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

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-top:20px;">
    <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png" width="240">
    <br><br>
    <a href="https://www.allotltd.com/" style="text-decoration:none; font-size:20px; color:#2563eb;">
        www.allotltd.com
    </a>
</div>
<hr style="margin-top: 2em; opacity:0.3;">
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div style="text-align:center; padding:30px 20px;
background: linear-gradient(90deg, #2563eb, #1e40af);
border-radius:16px; color:white; margin-bottom:20px;">
    <h1>💬 NBA for Oncology</h1>
    <p>Next Best Actions for Healthcare</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# OVERVIEW
# -----------------------------
st.markdown("### 📘 Overview")
st.markdown("""
This application delivers Next Best Actions (NBAs) for oncology teams in England.
It uses internal + external healthcare datasets combined with NICE guidance.
""")

# -----------------------------
# DATA SLOT (YOUR DATA PLUG-IN AREA)
# -----------------------------
with st.expander("🧠 Data Integration (Your Custom Data Area)"):
    st.info("This is where you can later plug your own datasets (CSV, DB, APIs).")
    st.write("Current system uses SnapLogic API only.")

# -----------------------------
# SAMPLE QUESTIONS
# -----------------------------
with st.expander("💡 Sample Questions"):

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Key Account Manager")
        if st.button("📈 Top accounts"):
            st.session_state.prompt = "What are top-performing accounts?"
            st.session_state.role = "Key Account Manager"

        if st.button("🧬 High potential HCPs"):
            st.session_state.prompt = "Which HCPs have high potential but low engagement?"
            st.session_state.role = "Key Account Manager"

    with col2:
        st.markdown("### Commercial Director")
        if st.button("📘 NICE alignment"):
            st.session_state.prompt = "Which HCPs are not aligned with NICE guidelines?"
            st.session_state.role = "Commercial Director"

        if st.button("🏥 London hospitals"):
            st.session_state.prompt = "Give me about London hospital key account?"
            st.session_state.role = "Commercial Director"

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):

    st.subheader("💬 Ask a question")

    prompt = st.text_area(
        "",
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

    role = st.radio("👤 Select your role", roles,
                    index=roles.index(st.session_state.role))

    submitted = st.form_submit_button("🚀 Get Insight")

# -----------------------------
# API CALL
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question.")
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
                response.raise_for_status()
                data = response.json()

                # -----------------------------
                # SAFE RESPONSE PARSING
                # -----------------------------
                if isinstance(data, list) and "Customer_Story" in data[0]:
                    reply = data[0]["Customer_Story"]
                elif isinstance(data, dict):
                    reply = data.get("Customer_Story", str(data))
                else:
                    reply = str(data)

            except Exception as e:
                reply = f"Error calling API: {str(e)}"

        # reset prompt after submit
        st.session_state.prompt = ""

        # -----------------------------
        # OUTPUT (MARKDOWN SAFE)
        # -----------------------------
        st.markdown("### 💡 Insight")
        st.markdown(
            f"""
            <div style="
                background:#ffffff;
                padding:20px;
                border-radius:14px;
                border:1px solid #e5e7eb;
                box-shadow:0 4px 12px rgba(0,0,0,0.04);
            ">
            {reply}
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr style="margin-top: 3em; opacity:0.2;">
<p style="text-align:center; font-size: 0.85em; color: #9ca3af;">
© 2026 NBA Oncology | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
