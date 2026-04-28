import streamlit as st
import requests
import json
from io import BytesIO
import pandas as pd
import re

# -----------------------------
# SAFE IMPORTS
# -----------------------------
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from pptx import Presentation
    LIBS_AVAILABLE = True
except Exception:
    LIBS_AVAILABLE = False


# -----------------------------
# CONFIG
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v5%20Task"
API_KEY = "681vyxaddAuuuJ21FD7LOYVogX7B0dHB"

st.set_page_config("Commercial Pharma", "💬", layout="centered")


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
# EXECUTIVE PPT GENERATOR
# -----------------------------
def create_ppt(text):
    prs = Presentation()

    sections = [s.strip() for s in text.split("\n") if s.strip()]

    # Title Slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Pharma Next Best Action"
    slide.placeholders[1].text = "Executive Report"

    # Executive Summary
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"
    slide.placeholders[1].text = " | ".join(sections[:3])[:900]

    # Key Insights
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"
    slide.placeholders[1].text = "\n".join(sections[3:6])[:1000]

    # Strategic Actions
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Strategic Actions"
    slide.placeholders[1].text = "\n".join(sections[6:9])[:1000]

    # Final Slide
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Next Best Actions"
    slide.placeholders[1].text = text[:1200]

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer


# -----------------------------
# AUTO CHART FUNCTION
# -----------------------------
def generate_chart_from_text(text):
    """
    Extract simple patterns like:
    Hospital A - 120
    Clinic B: 95
    """

    pattern = r'([A-Za-z0-9\s]+)[-:]\s*(\d+)'
    matches = re.findall(pattern, text)

    if len(matches) >= 2:
        df = pd.DataFrame(matches, columns=["Category", "Value"])
        df["Value"] = pd.to_numeric(df["Value"])
        return df

    return None


# -----------------------------
# UI HEADER
# -----------------------------
st.markdown("## 💬 Next Best Action - Commercial Pharma")


# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("form"):
    prompt = st.text_area("Enter your query", height=120)

    role = st.radio(
        "Select Role",
        ["Sales Representative", "Market Access Specialist", "Medical Science Liaison (MSL)"]
    )

    submit = st.form_submit_button("Generate")


# -----------------------------
# API CALL
# -----------------------------
if submit and prompt.strip():

    with st.spinner("Generating response..."):

        payload = [{"question_type": role, "prompt": prompt}]
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            res = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            data = res.json()

            reply = data[0]["Customer_Story"] if isinstance(data, list) else str(data)

        except Exception as e:
            reply = f"Error: {e}"


    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("Response")
    st.info(reply)

    # -----------------------------
    # AUTO GRAPH GENERATION
    # -----------------------------
    df_chart = generate_chart_from_text(reply)

    if df_chart is not None:
        st.subheader("📊 Visual Insights")
        st.bar_chart(df_chart.set_index("Category"))
    else:
        st.caption("No structured data found for visualization.")


    # -----------------------------
    # DOWNLOADS
    # -----------------------------
    st.subheader("⬇️ Download Reports")

    if LIBS_AVAILABLE:
        pdf_file = create_pdf(reply)
        ppt_file = create_ppt(reply)

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
                file_name="Pharma_Executive_NBA.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
    else:
        st.error("PDF/PPT libraries not installed. Check requirements.txt.")


elif submit and not prompt.strip():
    st.warning("Please enter a question.")
