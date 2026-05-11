import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v6%20Task"
API_KEY = "PROhgIoeBKE5pokEZmM3xHAlWUZs8sxD"

st.set_page_config(
    page_title="Commercial Pharma",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# SESSION STATE
# -----------------------------
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "role" not in st.session_state:
    st.session_state.role = "Sales Representative"

# -----------------------------
# UI
# -----------------------------
st.title("Commercial Pharma Assistant")

role = st.selectbox(
    "Select Role",
    [
        "Sales Representative",
        "Market Access Specialist",
        "Medical Science Liaison (MSL)"
    ],
    index=0
)

st.session_state.role = role

email = st.text_input("Enter recipient email address")

user_prompt = st.text_area(
    "Enter your prompt",
    value=st.session_state.prompt,
    height=150
)

st.session_state.prompt = user_prompt

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
if st.button("Generate Output and Send Email"):

    if not user_prompt.strip():
        st.warning("Please enter your prompt.")
        st.stop()

    if not email.strip():
        st.warning("Please enter recipient email address.")
        st.stop()

    payload = {
        "question_type": st.session_state.role,
        "prompt": st.session_state.prompt,
        "email": email
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with st.spinner("Generating output and sending email..."):
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=180
            )

        if response.status_code == 200:
            result = response.json()

            st.success("Output generated and email sent successfully.")

            output = (
                result.get("response")
                or result.get("output")
                or result.get("answer")
                or result
            )

            st.subheader("Generated Output")

            if isinstance(output, dict):
                st.json(output)
            else:
                st.markdown(str(output))

        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please increase timeout or optimise the SnapLogic pipeline.")

    except Exception as e:
        st.error(f"Error: {e}")
