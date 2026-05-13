import streamlit as st
import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v6%20Task"
API_KEY = "rdYvA7JMefys1fqzMnakjxvHuVVAhOBe"

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
# PAGE TITLE
# -----------------------------
st.title("Commercial Pharma Assistant")

# -----------------------------
# ROLE DROPDOWN
# -----------------------------
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

# -----------------------------
# MULTIPLE EMAIL INPUT
# -----------------------------
emails = st.text_area(
    "Enter recipient email addresses",
    placeholder="example1@email.com, example2@email.com\nor enter one email per line",
    height=100
)

# -----------------------------
# PROMPT INPUT
# -----------------------------
user_prompt = st.text_area(
    "Enter your prompt",
    value=st.session_state.prompt,
    height=180
)

st.session_state.prompt = user_prompt

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
if st.button("Generate Output and Send Emails"):

    # -----------------------------
    # VALIDATIONS
    # -----------------------------
    if not user_prompt.strip():
        st.warning("Please enter your prompt.")
        st.stop()

    if not emails.strip():
        st.warning("Please enter at least one recipient email address.")
        st.stop()

    email_list = [
        e.strip()
        for e in emails.replace("\n", ",").split(",")
        if e.strip()
    ]

    if not email_list:
        st.warning("Please enter valid email addresses.")
        st.stop()

    # -----------------------------
    # PAYLOAD
    # -----------------------------
    payload = {
        "question_type": st.session_state.role,
        "prompt": st.session_state.prompt,
        "emails": email_list
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # -----------------------------
    # API CALL
    # -----------------------------
    try:
        with st.spinner("Generating output and sending emails..."):

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=180
            )

        # -----------------------------
        # SUCCESS RESPONSE
        # -----------------------------
        if response.status_code == 200:

            st.success(f"Output generated and sent to {len(email_list)} email(s).")

            try:
                result = response.json()
            except ValueError:
                result = response.text

            # -----------------------------
            # EXTRACT OUTPUT PROPERLY
            # -----------------------------
            output = None

            if isinstance(result, list):
                if len(result) > 0:
                    first_item = result[0]

                    if isinstance(first_item, dict):
                        output = (
                            first_item.get("Customer_Story")
                            or first_item.get("response")
                            or first_item.get("output")
                            or first_item.get("answer")
                            or first_item.get("content")
                            or first_item
                        )
                    else:
                        output = first_item
                else:
                    output = "No output returned."

            elif isinstance(result, dict):
                output = (
                    result.get("Customer_Story")
                    or result.get("response")
                    or result.get("output")
                    or result.get("answer")
                    or result.get("content")
                    or result
                )

            else:
                output = result

            # -----------------------------
            # DISPLAY OUTPUT PROPERLY
            # -----------------------------
            st.subheader("Generated Output")

            if isinstance(output, str):
                st.markdown(output, unsafe_allow_html=True)

            elif isinstance(output, dict):
                st.json(output)

            elif isinstance(output, list):
                st.json(output)

            else:
                st.write(output)

        # -----------------------------
        # API ERROR
        # -----------------------------
        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    # -----------------------------
    # TIMEOUT ERROR
    # -----------------------------
    except requests.exceptions.Timeout:
        st.error(
            "Request timed out. Please increase timeout or optimise the SnapLogic pipeline."
        )

    # -----------------------------
    # GENERAL ERROR
    # -----------------------------
    except Exception as e:
        st.error(f"Error: {e}")
