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
    Splits generated output into selectable blocks using real headings.
    Example dropdown labels:
    Tier 1: Highest-Priority HCP Targets
    Tier 2: Medium-Priority HCP Targets
    Step 2: NBA Strategy
    Recommendation 1: ...
    """

    if not isinstance(output_text, str):
        return [
            {
                "title": "Generated Output",
                "content": str(output_text)
            }
        ]

    # Match section headings
    pattern = r"(?=^(?:Tier\s*\d+|Step\s*\d+|Recommendation\s*\d+|HCP\s*\d+|NBA\s*\d+|Next Best Action\s*\d+)[:.\-].*)"

    parts = re.split(
        pattern,
        output_text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    parts = [p.strip() for p in parts if p.strip()]

    items = []

    for part in parts:
        lines = part.splitlines()
        title = lines[0].strip() if lines else "Section"

        # Avoid very long dropdown titles
        if len(title) > 90:
            title = title[:90] + "..."

        items.append(
            {
                "title": title,
                "content": part
            }
        )

    if not items:
        items.append(
            {
                "title": "Full Generated Output",
                "content": output_text
            }
        )

    return items


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
# PROMPT INPUT
# -----------------------------
user_prompt = st.text_area(
    "Ask your question",
    value=st.session_state.prompt,
    height=180,
    placeholder="Example: Analyse call notes data and generate NBA for high-potential prescribers of Empagliflozin and explain why."
)

st.session_state.prompt = user_prompt

# -----------------------------
# GENERATE OUTPUT BUTTON
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
# DISPLAY FULL OUTPUT
# -----------------------------
if st.session_state.generated_output:

    st.subheader("Generated Full Output")

    if isinstance(st.session_state.generated_output, str):
        st.markdown(st.session_state.generated_output, unsafe_allow_html=True)
    else:
        st.json(st.session_state.generated_output)

    st.divider()

    # -----------------------------
    # SELECT ONE SECTION TO EMAIL
    # -----------------------------
    st.subheader("Send One Selected HCP/NBA Section by Email")

    nba_items = st.session_state.nba_items

    selected_index = st.selectbox(
        "Select one section to email",
        range(len(nba_items)),
        format_func=lambda i: nba_items[i]["title"]
    )

    selected_output = nba_items[selected_index]["content"]

    st.markdown("### Selected Content Preview")
    st.markdown(selected_output, unsafe_allow_html=True)

    # -----------------------------
    # EMAIL INPUT
    # -----------------------------
    emails = st.text_area(
        "Enter recipient email address(es)",
        placeholder="example1@email.com, example2@email.com\nor one email per line",
        height=100
    )

    # -----------------------------
    # SEND EMAIL BUTTON
    # -----------------------------
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
            with st.spinner("Sending selected section email..."):

                email_response = requests.post(
                    API_URL,
                    headers=headers,
                    json=email_payload,
                    timeout=120
                )

            if email_response.status_code == 200:
                st.success(f"Selected section sent to {len(email_list)} email(s).")
            else:
                st.error(f"Email API Error: {email_response.status_code}")
                st.write(email_response.text)

        except requests.exceptions.Timeout:
            st.error("Email request timed out.")

        except Exception as e:
            st.error(f"Error: {e}")
