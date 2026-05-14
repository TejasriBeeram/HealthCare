
import streamlit as st
import requests
import json
import re

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

if "generated_output" not in st.session_state:
    st.session_state.generated_output = None

if "nba_items" not in st.session_state:
    st.session_state.nba_items = []

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def extract_output(result):
    if isinstance(result, list):
        if len(result) > 0:
            first_item = result[0]
            if isinstance(first_item, dict):
                return (
                    first_item.get("Customer_Story")
                    or first_item.get("response")
                    or first_item.get("output")
                    or first_item.get("answer")
                    or first_item.get("content")
                    or first_item
                )
            return first_item
        return "No output returned."

    if isinstance(result, dict):
        return (
            result.get("Customer_Story")
            or result.get("response")
            or result.get("output")
            or result.get("answer")
            or result.get("content")
            or result
        )

    return result


def split_nba_items(output_text):
    """
    Splits generated output into selectable HCP/NBA sections.
    This works best if your Bedrock output uses headings like:
    HCP 1:, HCP 2:, NBA 1:, Recommendation 1:, etc.
    """

    if not isinstance(output_text, str):
        return [str(output_text)]

    pattern = r"(?=(?:HCP|NBA|Recommendation|Next Best Action)\s*\d+[:\.\-])"

    parts = re.split(pattern, output_text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) > 1:
        return parts

    # fallback: split by double line breaks
    fallback_parts = [p.strip() for p in output_text.split("\n\n") if p.strip()]

    if len(fallback_parts) > 1:
        return fallback_parts

    return [output_text]


def parse_emails(email_text):
    return [
        e.strip()
        for e in email_text.replace("\n", ",").split(",")
        if e.strip()
    ]


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
# CHAT STYLE PROMPT INPUT
# -----------------------------
user_prompt = st.text_area(
    "Ask your question",
    value=st.session_state.prompt,
    height=180,
    placeholder="Example: Generate 5 HCP next best actions for diabetes."
)

st.session_state.prompt = user_prompt

# -----------------------------
# GENERATE BUTTON
# -----------------------------
if st.button("Generate Output"):

    if not user_prompt.strip():
        st.warning("Please enter your prompt.")
        st.stop()

    generate_payload = {
        "mode": "generate",
        "question_type": st.session_state.role,
        "prompt": st.session_state.prompt
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        with st.spinner("Generating full output..."):
            response = requests.post(
                API_URL,
                headers=headers,
                json=generate_payload,
                timeout=180
            )

        if response.status_code == 200:
            try:
                result = response.json()
            except ValueError:
                result = response.text

            output = extract_output(result)

            st.session_state.generated_output = output
            st.session_state.nba_items = split_nba_items(output)

            st.success("Output generated successfully.")

        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please optimise the SnapLogic pipeline or increase timeout.")

    except Exception as e:
        st.error(f"Error: {e}")


# -----------------------------
# DISPLAY GENERATED OUTPUT
# -----------------------------
if st.session_state.generated_output:

    st.subheader("Generated Full Output")

    if isinstance(st.session_state.generated_output, str):
        st.markdown(st.session_state.generated_output, unsafe_allow_html=True)
    else:
        st.json(st.session_state.generated_output)

    st.divider()

    st.subheader("Send One Selected HCP/NBA by Email")

    nba_items = st.session_state.nba_items

    selected_index = st.selectbox(
        "Select one HCP/NBA to email",
        range(len(nba_items)),
        format_func=lambda i: f"Option {i + 1}"
    )

    selected_output = nba_items[selected_index]

    st.markdown("### Selected Content Preview")
    st.markdown(selected_output, unsafe_allow_html=True)

    emails = st.text_area(
        "Enter recipient email address(es)",
        placeholder="example1@email.com, example2@email.com\nor one email per line",
        height=100
    )

    if st.button("Send Selected Email"):

        if not emails.strip():
            st.warning("Please enter at least one recipient email address.")
            st.stop()

        email_list = parse_emails(emails)

        if not email_list:
            st.warning("Please enter valid email addresses.")
            st.stop()

        email_payload = {
            "mode": "send_email",
            "emails": email_list,
            "selected_output": selected_output
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            with st.spinner("Sending selected HCP/NBA email..."):
                email_response = requests.post(
                    API_URL,
                    headers=headers,
                    json=email_payload,
                    timeout=120
                )

            if email_response.status_code == 200:
                st.success(f"Selected HCP/NBA sent to {len(email_list)} email(s).")
            else:
                st.error(f"Email API Error: {email_response.status_code}")
                st.write(email_response.text)

        except requests.exceptions.Timeout:
            st.error("Email request timed out.")

        except Exception as e:
            st.error(f"Error: {e}")
