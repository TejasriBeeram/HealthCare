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
# EMAIL INPUT
# -----------------------------
email = st.text_input(
    "Enter recipient email address"
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
if st.button("Generate Output and Send Email"):

    # -----------------------------
    # VALIDATIONS
    # -----------------------------
    if not user_prompt.strip():
        st.warning("Please enter your prompt.")
        st.stop()

    if not email.strip():
        st.warning("Please enter recipient email address.")
        st.stop()

    # -----------------------------
    # PAYLOAD
    # -----------------------------
    payload = {
        "question_type": st.session_state.role,
        "prompt": st.session_state.prompt,
        "email": email
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # -----------------------------
    # API CALL
    # -----------------------------
    try:
        with st.spinner("Generating output and sending email..."):

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

            result = response.json()

            st.success("Output generated and email sent successfully.")

            # -----------------------------
            # HANDLE LIST RESPONSE
            # -----------------------------
            if isinstance(result, list):

                if len(result) > 0:

                    first_item = result[0]

                    if isinstance(first_item, dict):

                        output = (
                            first_item.get("response")
                            or first_item.get("output")
                            or first_item.get("answer")
                            or first_item.get("content")
                            or first_item
                        )

                    else:
                        output = first_item

                else:
                    output = "No output returned."

            # -----------------------------
            # HANDLE DICTIONARY RESPONSE
            # -----------------------------
            elif isinstance(result, dict):

                output = (
                    result.get("response")
                    or result.get("output")
                    or result.get("answer")
                    or result.get("content")
                    or result
                )

            # -----------------------------
            # HANDLE STRING RESPONSE
            # -----------------------------
            else:
                output = result

            # -----------------------------
            # DISPLAY OUTPUT
            # -----------------------------
            st.subheader("Generated Output")

            if isinstance(output, dict):
                st.json(output)

            elif isinstance(output, list):
                st.json(output)

            else:
                st.markdown(str(output))

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
            "Request timed out. "
            "Please increase timeout or optimise the SnapLogic pipeline."
        )

    # -----------------------------
    # GENERAL ERROR
    # -----------------------------
    except Exception as e:

        st.error(f"Error: {e}")
