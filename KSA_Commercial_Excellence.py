import streamlit as st
import requests

# API details
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes%20Task"
API_HEADERS = {
    "Authorization": "Bearer 00H4LCOLTH9Kem0cSKGBEDb8gkIxV3JK",
    "Content-Type": "application/json"
}

# Streamlit App
st.set_page_config(page_title="KSA Commercial Excellence", page_icon="💬", layout="wide")

# --- Custom Header ---
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png" width="150">
    </div>
    <h1 style="text-align: left; font-size: 2.2rem; margin-top: 0.5rem;">
        💬 KSA Commercial Excellence
    </h1>
    """,
    unsafe_allow_html=True
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar instructions
with st.sidebar:
    st.subheader("Instructions")
    st.write("""
    This chatbot connects to a healthcare commercial excellence API.

    Example prompt:
    - `King Abdulaziz Medical City (Riyadh - NGHA)`
    
    Select the role you want before sending your enquiry.
    """)

# Function to query API
def query_api(question_type, prompt):
    payload = [{"question_type": question_type, "prompt": prompt}]
    try:
        response = requests.post(API_URL, headers=API_HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("Customer_Story", "No response found.")
        else:
            return "Unexpected response format from API."
    except Exception as e:
        return f"Error: {str(e)}"

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# User input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Commercial enquiry:", "")

    question_type = st.radio(
        "Select role:",
        [
            "Sales Representative",
            "Market Access Specialist",
            "Medical Science Liaison (MSL)",
            "Marketing Expert"
        ],
        horizontal=False
    )

    submitted = st.form_submit_button("Send")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": f"[{question_type}] {user_input}"})
        bot_response = query_api(question_type, user_input)
        st.session_state.messages.append({"role": "bot", "content": f"**{question_type}:** {bot_response}"})
        st.rerun()
