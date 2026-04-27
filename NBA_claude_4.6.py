import streamlit as st
import requests
import json
from io import BytesIO

# -----------------------------
# SAFE IMPORTS (IMPORTANT FIX)
# -----------------------------
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from pptx import Presentation
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False


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
# CSS
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

.stTextArea textarea {
    color: #000 !important;
    background-color: #fff !important;
}

.stAlert {
    background-color: #eef6ff !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div style="text-align:center;">
    <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png" width="260">
    <br><br>
    <a href="https://www.allotltd.com/" style="font-size:20px;">
        www.allotltd.com
    </a>
</div>
<hr>
""", unsafe_allow_html=True)


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
Saudi Arabia Diabetes Market NBA Generator (Sales / Market Access / MSL)
""")

st.write("---")


# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):

    prompt = st.text_area("Enquiry:", placeholder="Type your question here...", height=110)

    role = st.radio(
        "Select role:",
        [
            "Sales Representative",
            "Market Access Specialist",
            "Medical Science Liaison (MSL)"
        ]
    )

    submitted = st.form_submit_button("Send")


# -----------------------------
# PROCESS REQUEST
# -----------------------------
if submitted and prompt.strip():

    with st.spinner("Fetching response..."):

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
                reply = f"Unexpected API format: {data}"

        except Exception as e:
            reply = f"⚠️ Error: {e}"


    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.write("---")
    st.subheader("Response:")
    st.info(reply)


    # -----------------------------
    # DOWNLOADS (SAFE CHECK)
    # -----------------------------
    if LIBS_AVAILABLE:

        pdf_file = create_pdf(reply)
        ppt_file = create_ppt(reply)

        st.write("---")
        st.subheader("⬇️ Download Outputs")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📄 Download PDF",
                pdf_file,
                file_name="NBA_Report.pdf",
                mime="application/pdf"
            )

        with col2:
            st.download_button(
                "📊 Download PPT",
                ppt_file,
                file_name="NBA_Report.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

    else:
        st.warning("PDF/PPT features disabled. Install: reportlab, python-pptx")


elif submitted and not prompt.strip():
    st.warning("Please enter a question.")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr>
<p style="text-align:center; font-size:12px;">
© 2025 KSA Commercial Excellence | Powered by Allot Ltd
</p>
""", unsafe_allow_html=True)
