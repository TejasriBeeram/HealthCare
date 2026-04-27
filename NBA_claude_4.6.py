import streamlit as st
import requests
import json
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pptx import Presentation


# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v5%20Task"
API_KEY = "681vyxaddAuuuJ21FD7LOYVogX7B0dHB"

st.set_page_config(
    page_title="Commercial Pharma",
    page_icon="💬",
    layout="centered"
)

# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer


# -----------------------------
# PPT GENERATOR
# -----------------------------
def create_ppt(text):
    prs = Presentation()

    sections = text.split("\n\n")

    for section in sections:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = slide.shapes.title
        content = slide.placeholders[1]

        title.text = "Next Best Action"
        content.text = section[:1000]

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer


# -----------------------------
# LIGHT THEME CSS
# -----------------------------
st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #000 !important;
}

.stTextInput > div > div,
.stTextArea > div,
.stSelectbox > div,
.stRadio > div {
    background-color: #f8f9fa !important;
    border: 1px solid #ccc !important;
    border-radius: 10px !important;
}

.stTextArea textarea {
    color: #000 !important;
    background-color: #fff !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #777 !important;
}

[data-testid="stForm"] {
    background-color: #f2f2f2 !important;
    padding: 20px !important;
    border-radius: 12px !important;
}

button[data-testid="baseButton-primary"] {
    background-color: #2563eb !important;
    color: white !important;
}

.stAlert {
    background-color: #eef6ff !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:20px;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png"
             width="260">
        <br><br>
        <a href="https://www.allotltd.com/"
            style="font-size:22px; color:#2563eb;">
            www.allotltd.com
        </a>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# TITLE
# -----------------------------
st.markdown("## 💬 Next Best Action for Commercial Pharma")
st.write("---")


# -----------------------------
# OVERVIEW
# -----------------------------
st.markdown("""
### 📘 Overview
This application offers Next Best Actions (NBA) for pharma teams in the Saudi Arabia diabetes market.
""")

st.write("---")


# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):

    st.subheader("Enquiry:")
    prompt = st.text_area("", placeholder="Type your question here...", height=110)

    st.subheader("Select role:")
    role = st.radio(
        "",
        [
            "Sales Representative",
            "Market Access Specialist",
            "Medical Science Liaison (MSL)"
        ],
        index=0
    )

    submitted = st.form_submit_button("Send")


# -----------------------------
# PROCESS API
# -----------------------------
if submitted and prompt.strip():

    with st.spinner(f"Fetching response for {role}..."):

        payload = [{"question_type": role, "prompt": prompt}]
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and "Customer_Story" in data[0]:
                reply = data[0]["Customer_Story"]
            else:
                reply = f"Unexpected API response format: {data}"

        except Exception as e:
            reply = f"⚠️ Error: {e}"


    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.write("---")
    st.subheader("Response:")
    st.info(reply)


    # -----------------------------
    # DOWNLOAD FILES
    # -----------------------------
    pdf_file = create_pdf(reply)
    ppt_file = create_ppt(reply)

    st.write("---")
    st.subheader("⬇️ Download Outputs")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📄 Download PDF",
            data=pdf_file,
            file_name="NBA_Report.pdf",
            mime="application/pdf"
        )

    with col2:
        st.download_button(
            label="📊 Download PPT",
            data=ppt_file,
            file_name="NBA_Report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )


elif submitted and not prompt.strip():
    st.warning("Please enter a question before sending.")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr>
<p style="text-align:center; font-size: 0.9em; color: #777;">
© 2025 KSA Commercial Excellence | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
