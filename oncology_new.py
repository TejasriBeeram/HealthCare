import streamlit as st
import requests

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"

# सुरक्षित तरीका (Streamlit secrets)
API_KEY = st.secrets.get("API_KEY", "")

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
    <p>Next Best Actions for Healthcare</p>
</div>
""", unsafe_allow_html=True)

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

    st.subheader("👤 Select your role")

    roles = [
        "Key Account Manager",
        "Market Access Representative",
        "Medical Science Liaison (MSL)",
        "Commercial Director"
    ]

    # Safe index handling
    role_index = roles.index(st.session_state.role) if st.session_state.role in roles else 0
    role = st.radio("", roles, index=role_index)

    submitted = st.form_submit_button("🚀 Get Insight")

# -----------------------------
# API CALL
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question before sending.")
    elif not API_KEY:
        st.error("API key is missing. Please configure it in Streamlit secrets.")
    else:
        with st.spinner("🔍 Analysing oncology data..."):

            payload = [{"question_type": role, "prompt": prompt}]
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

                try:
                    data = response.json()
                except Exception:
                    data = {}

                # Safer parsing
                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("Customer_Story", "No insight returned.")
                else:
                    reply = f"Unexpected API response format: {data}"

            except requests.exceptions.Timeout:
                reply = "⚠️ Request timed out. Please try again."
            except requests.exceptions.RequestException as e:
                reply = f"⚠️ API Error: {str(e)}"
            except Exception as e:
                reply = f"⚠️ Unexpected Error: {str(e)}"

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

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr style="margin-top: 3em; opacity:0.2;">
<p style="text-align:center; font-size: 0.85em; color: #9ca3af;">
© 2026 NBA Oncology | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
