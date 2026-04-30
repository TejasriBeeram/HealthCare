import streamlit as st
import requests

# -----------------------------
# CONFIGURATION (Triggered Task)
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"
API_KEY = st.secrets.get("API_KEY", "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0")

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
# UI (UNCHANGED - KEEP YOUR DESIGN)
# -----------------------------
st.title("💬 NBA for Oncology")

prompt = st.text_area(
    "Ask your question",
    value=st.session_state.prompt,
    height=120
)

roles = [
    "Key Account Manager",
    "Market Access Representative",
    "Medical Science Liaison (MSL)",
    "Commercial Director"
]

role = st.radio("Select Role", roles)

# -----------------------------
# SUBMIT
# -----------------------------
if st.button("🚀 Get Insight"):

    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Submitting request to SnapLogic..."):

            payload = [{
                "question_type": role,
                "prompt": prompt
            }]

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                # 🔥 IMPORTANT: short timeout ONLY for trigger
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                # -----------------------------
                # DO NOT RELY ON RESPONSE CONTENT
                # -----------------------------
                st.success("✅ Request successfully submitted!")

                st.write("Status Code:", response.status_code)

                # Try to show response IF available (optional)
                try:
                    data = response.json()
                    st.info("Response received (if available):")
                    st.json(data)
                except:
                    if response.text:
                        st.text("Raw Response:")
                        st.text(response.text)
                    else:
                        st.info("No response body (expected for Triggered Task).")

                st.warning("⏳ Processing is asynchronous. Check SnapLogic pipeline execution for results.")

            except requests.exceptions.Timeout:
                st.success("✅ Request likely submitted (timeout is expected for Triggered Tasks).")
                st.info("⏳ Check SnapLogic dashboard for pipeline execution results.")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {str(e)}")
