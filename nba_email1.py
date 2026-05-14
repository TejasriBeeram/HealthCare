import streamlit as st
import requests
import re

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v6%20Task"
API_KEY = "rdYvA7JMefys1fqzMnakjxvHuVVAhOBe"

st.set_page_config(
    page_title="Commercial Pharma",
    page_icon="💬",
    layout="wide"
)

# -----------------------------
# SESSION STATE
# -----------------------------
if "full_report" not in st.session_state:
    st.session_state.full_report = ""

# -----------------------------
# FUNCTIONS
# -----------------------------
def clean_html(text):

    text = str(text)

    text = text.replace("```html", "")
    text = text.replace("```", "")

    return text.strip()


def extract_output(result):

    if isinstance(result, list) and len(result) > 0:

        first_item = result[0]

        if isinstance(first_item, dict):

            return (
                first_item.get("Customer_Story")
                or first_item.get("response")
                or first_item.get("output")
                or first_item.get("answer")
                or first_item.get("content")
                or str(first_item)
            )

        return str(first_item)

    elif isinstance(result, dict):

        return (
            result.get("Customer_Story")
            or result.get("response")
            or result.get("output")
            or result.get("answer")
            or result.get("content")
            or str(result)
        )

    return str(result)


def extract_section(report, keyword):

    report = clean_html(report)

    # Split by HTML headings
    sections = re.split(
        r"(?=<h1|<h2|<h3)",
        report,
        flags=re.IGNORECASE
    )

    for section in sections:

        if keyword.lower() in section.lower():

            return section

    # Fallback
    return f"""
    <h2>Section Not Found</h2>
    <p>No matching section found for:
    <b>{keyword}</b></p>
    <p>Please try another keyword.</p>
    """


def call_snaplogic(payload):

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=600
    )

    if response.status_code != 200:

        st.error(f"API Error: {response.status_code}")
        st.write(response.text)

        return None

    try:

        result = response.json()

    except:

        result = response.text

    return extract_output(result)

# -----------------------------
# UI
# -----------------------------
st.title("Commercial Pharma Assistant")

# -----------------------------
# ROLE
# -----------------------------
role = st.selectbox(
    "Select Role",
    [
        "Sales Representative",
        "Market Access Specialist",
        "Medical Science Liaison (MSL)"
    ]
)

# -----------------------------
# EMAILS
# -----------------------------
emails = st.text_area(
    "Enter recipient email addresses",
    placeholder="abc@test.com, xyz@test.com",
    height=100
)

# -----------------------------
# PROMPT
# -----------------------------
user_prompt = st.text_area(
    "Enter your prompt",
    height=200
)

# -----------------------------
# GENERATE REPORT
# -----------------------------
if st.button("Generate Full Report"):

    if not user_prompt.strip():

        st.warning("Please enter your prompt.")
        st.stop()

    payload = {
        "question_type": role,
        "prompt": user_prompt
    }

    try:

        with st.spinner("Generating full report..."):

            output = call_snaplogic(payload)

        if output:

            output = clean_html(output)

            st.session_state.full_report = output

            st.success("Report generated successfully.")

    except requests.exceptions.Timeout:

        st.error(
            "Request timed out after 10 minutes."
        )

    except Exception as e:

        st.error(str(e))

# -----------------------------
# DISPLAY REPORT
# -----------------------------
if st.session_state.full_report:

    st.subheader("Generated Report")

    st.markdown(
        st.session_state.full_report,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------
    # SECTION TO SEND
    # -----------------------------
    selected_section = st.text_input(
        "Which section do you want to send?",
        placeholder="Example: Khalid OR Scoring Methodology"
    )

    if selected_section:

        selected_content = extract_section(
            st.session_state.full_report,
            selected_section
        )

        st.subheader("Selected Section Preview")

        st.markdown(
            selected_content,
            unsafe_allow_html=True
        )

        # -----------------------------
        # SEND EMAIL BUTTON
        # -----------------------------
        if st.button("Send Selected Section Email"):

            email_list = [
                e.strip()
                for e in emails.replace("\n", ",").split(",")
                if e.strip()
            ]

            if not email_list:

                st.warning(
                    "Please enter recipient email addresses."
                )

                st.stop()

            # IMPORTANT:
            # Reuse existing SnapLogic pipeline
            # by sending selected section as prompt
            payload = {
                "question_type": role,
                "prompt": f"""
Return ONLY the below selected report section.

Do not add extra sections.
Do not return the full report.

Return clean HTML email content only.

Do not use Markdown.
Do not use #, ##, **.
Do not use ```html.
Do not use code blocks.

SELECTED REPORT SECTION:

{selected_content}
""",
                "emails": email_list
            }

            try:

                with st.spinner(
                    "Sending selected section email..."
                ):

                    response = requests.post(
                        API_URL,
                        headers={
                            "Authorization": f"Bearer {API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=600
                    )

                if response.status_code == 200:

                    st.success(
                        f"Selected section sent to {len(email_list)} email(s)."
                    )

                else:

                    st.error(
                        f"API Error: {response.status_code}"
                    )

                    st.write(response.text)

            except requests.exceptions.Timeout:

                st.error(
                    "Request timed out after 10 minutes."
                )

            except Exception as e:

                st.error(str(e))
