import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_tejasri%20Task"
API_KEY = "1CQHpI3oOHloqEWhh1Exwp0AToE7qqJF"

st.set_page_config(
    page_title="NBA for Commercial Pharma",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# DARK MODE + FIXED TEXT + FIXED BUTTON
# -----------------------------
st.markdown("""
<style>

/* Global background and text */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f1116 !important;
    color: #e6e6e6 !important;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #ffffff !important;
}

/* Input container styling */
.stTextInput > div > div,
.stTextArea > div,
.stSelectbox > div,
.stRadio > div {
    background-color: #1a1c22 !important;
    border: 1px solid #333 !important;
    border-radius: 10px !important;
}

/* Text box input text (normal input) */
.stTextInput input {
    color: #fff !important;
}

/* TEXT AREA FIX — BLACK TEXT + WHITE BACKGROUND */
.stTextArea textarea {
    color: #000 !important;             /* Black text */
    background-color: #fff !important;  /* White background */
    border-radius: 10px !important;
}

/* Placeholder */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #888 !important;
}

/* Form container styling */
[data-testid="stForm"] {
    background-color: #16181d !important;
    padding: 20px !important;
    border-radius: 12px !important;
    border: 1px solid #2a2d34 !important;
}

/* FIX: Streamlit 1.30+ button */
button[data-testid="baseButton-primary"] {
    background-color: #3b82f6 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.6em 1.2em !important;
    border: none !important;
    font-weight: 500 !important;
}

button[data-testid="baseButton-primary"]:hover {
    background-color: #2563eb !important;
}

/* Info alert styling */
.stAlert {
    background-color: #1e2127 !important;
    color: #fff !important;
    border-left: 4px solid #3b82f6 !important;
}

hr {
    border-color: #333 !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:20px;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png"
             alt="Allot Logo" width="260">
        <br><br>
        <a href="https://www.allotltd.com/"
            style="text-decoration:none; font-size:22px; color:#3b82f6; font-weight:500;">
            www.allotltd.com
        </a>
    </div>
    <hr style="margin-top: 2em; opacity:0.3;">
    """,
    unsafe_allow_html=True
)

# -----------------------------
# PAGE TITLE
# -----------------------------
st.markdown("## 💬 **Next Best Action for Commercial Pharma**")
st.write("---")

# -----------------------------
# OVERVIEW
# -----------------------------
st.markdown(
    """
### 📘 Overview

This application offers the **Next Best Actions (NBAs)** for commercial, sales, market access, and medical pharmaceutical field teams. It focuses on the diabetes market in the Kingdom of Saudi Arabia(KSA). Analysis of client internal sales, CRM call notes, medical data, together with external in-market policy, healthcare data, recent medical publications, and future health conferences are governed by client specific business rules that control the output.

### ⚠️ Data Limitations
This demo only reflects **Saudi Arabia diabetes market data**, including:
- Sales data  
- HCP profiles  
- Call notes  
- Market summaries  
- Scientific publication data

### 💡 Sample Questions
- *Sales Representative:*  
  Analyse call notes data and generate NBA for high-potential prescribers of **Empagliflozin**.

- *Market Access Specialist:*  
  Generate NBAs to improve access for **Semaglutide** based on payer, formulary, and CRM data.

- *Medical Science Liaison (MSL):*  
  Identify follow-up requests or scientific questions from call notes.
"""
)

st.write("---")

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form", clear_on_submit=False):

    st.subheader("Enquiry:")
    prompt = st.text_area("", placeholder="Type your question here...", height=110)

    st.subheader("Select role:")
    role = st.radio(
        "",
        [
            "Sales Representative",
            "Market Access Specialist",
            "Medical Science Liaison (MSL)"
        ],
        index=0
    )

    submitted = st.form_submit_button("Send")

# -----------------------------
# PROCESS SUBMISSION
# -----------------------------
if submitted and prompt.strip():

    with st.spinner(f"Fetching response for **{role}**..."):
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

    st.write("---")
    st.subheader("Response:")
    st.info(reply)

elif submitted and not prompt.strip():
    st.warning("Please enter a question before sending.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
    <hr style="margin-top: 3em; opacity:0.3;">
    <p style="text-align:center; font-size: 0.9em; color: #777;">
        © 2025 KSA Commercial Excellence | Powered by Allot Ltd
    </p>
    """,
    unsafe_allow_html=True
)
