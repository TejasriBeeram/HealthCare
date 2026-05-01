import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Oncology%20Task"

# Try secrets first, fallback
API_KEY = st.secrets.get("API_KEY", None)

# 👉 If no secrets, paste your key here
if not API_KEY:
    API_KEY = "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0"

if not API_KEY or API_KEY == "TfPcaLIqmQtm6rWSegetxXVYulQf8WY0":
    st.warning("⚠️ API key missing. Add it to enable API calls.")

st.set_page_config(
    page_title="NBA for Lung Cancer in England",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# RETRY SESSION (IMPORTANT)
# -----------------------------
def create_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,  # exponential delay: 2s, 4s, 8s
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

session = create_session()

# -----------------------------
# SESSION STATE
# -----------------------------
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "role" not in st.session_state:
    st.session_state.role = "Key Account Manager"

# -----------------------------
# SIMPLE UI
# -----------------------------
st.title("💬 NBA for Oncology")
st.caption("Next Best Actions for Healthcare")

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
# API CALL FUNCTION
# -----------------------------
def call_api(payload, headers):
    try:
        response = session.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=180   # ⏱ increased timeout
        )

        response.raise_for_status()
        return response.json(), None

    except requests.exceptions.Timeout:
        return None, "⏱️ Request timed out. Backend is slow. Try again."

    except requests.exceptions.ConnectionError:
        return None, "🌐 Connection error. Check network or API endpoint."

    except requests.exceptions.HTTPError as err:
        return None, f"⚠️ API returned error: {err}"

    except Exception as e:
        return None, f"❌ Unexpected error: {str(e)}"

# -----------------------------
# HANDLE SUBMIT
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question.")

    elif not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
        st.error("❌ Cannot call API. API key is missing.")

    else:
        with st.spinner("⏳ Analyzing oncology data... this may take up to a minute"):

            payload = [{
                "question_type": role,
                "prompt": prompt
            }]

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data, error = call_api(payload, headers)

            if error:
                reply = error
            else:
                # Safe parsing
                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("Customer_Story", str(data[0]))
                elif isinstance(data, dict):
                    reply = data.get("Customer_Story", str(data))
                else:
                    reply = str(data)

        # Output
        st.markdown("### 💡 Insight")
        st.write(reply)

        # Reset prompt
        st.session_state.prompt = ""

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("© 2026 NBA Oncology")
