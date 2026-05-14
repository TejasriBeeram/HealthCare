import streamlit as st
import requests
import re

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v6%20Task"
API_KEY = "YOUR_NEW_TOKEN_HERE"

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

if "matched_block" not in st.session_state:
    st.session_state.matched_block = None


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
                    or str(first_item)
                )
            return str(first_item)
        return "No output returned."

    if isinstance(result, dict):
        return (
            result.get("Customer_Story")
            or result.get("response")
            or result.get("output")
            or result.get("answer")
            or result.get("content")
            or str(result)
        )

    return str(result)


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_section_by_heading(full_output, search_heading):
    """
    Finds the section that starts with the heading typed by user.
    Sends from that heading until the next major heading.
    """

    if not full_output or not search_heading:
        return None

    text = str(full_output)

    # Remove common HTML tags for matching, but keep original content for sending
    plain_text = re.sub(r"<[^>]+>", "", text)

    search_norm = normalize_text(search_heading)
    plain_norm = normalize_text(plain_text)

    if search_norm not in plain_norm:
        return None

    # Find approximate position in original plain text
    lines = plain_text.splitlines()

    start_index = None

    for i, line in enumerate(lines):
        if search_norm in normalize_text(line):
            start_index = i
            break

    if start_index is None:
        return None

    heading_patterns = [
        r"^High-Potential Empagliflozin Prescriber Identification",
        r"^Clinical Evidence Foundation",
        r"^Next Best Action Plan",
        r"^NBA\s*\d+\s*:",
        r"^Territory-Level Institutional Priority Summary",
        r"^Cross-Cutting NBA Themes",
        r"^Theme\s*\d+\s*:",
        r"^Summary NBA Priority Matrix",
        r"^Methodology:",
        r"^Overview",
        r"^Objective:"
    ]

    combined_heading_pattern = re.compile(
        "|".join(heading_patterns),
        re.IGNORECASE
    )

    end_index = len(lines)

    for j in range(start_index + 1, len(lines)):
        current_line = lines[j].strip()

        if combined_heading_pattern.search(current_line):
            end_index = j
            break

    selected_block = "\n".join(lines[start_index:end_index]).strip()

    return selected_block


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
            st.session_state.matched_block = None

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
    st.markdown(st.session_state.generated_output, unsafe_allow_html=True)

    st.divider()

    # -----------------------------
    # TYPE SECTION NAME TO SEND
    # -----------------------------
    st.subheader("Send Specific Section by Email")

    section_name = st.text_input(
        "Type the section heading you want to send",
        placeholder="Example: NBA 1: Prof. Saleh A. Alqahtani — KFSHRC Riyadh"
    )

    if st.button("Find Section"):

        if not section_name.strip():
            st.warning("Please enter the section heading.")
            st.stop()

        matched_block = find_section_by_heading(
            st.session_state.generated_output,
            section_name
        )

        if matched_block:
            st.session_state.matched_block = matched_block
            st.success("Section found.")
        else:
            st.session_state.matched_block = None
            st.error("No matching section found. Please copy the exact heading from the generated output.")

    # -----------------------------
    # DISPLAY MATCHED SECTION
    # -----------------------------
    if st.session_state.matched_block:

        st.markdown("### Selected Section Preview")
        st.markdown(st.session_state.matched_block, unsafe_allow_html=True)

        emails = st.text_area(
            "Enter recipient email address(es)",
            placeholder="example1@email.com, example2@email.com\nor one email per line",
            height=100
        )

        if st.button("Send Selected Section Email"):

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
                "selected_output": st.session_state.matched_block
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
