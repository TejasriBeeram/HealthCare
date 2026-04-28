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
# PPT GENERATOR
# -----------------------------
def create_ppt(text):
    prs = Presentation()

    sections = [s.strip() for s in text.split("\n") if s.strip()]

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Pharma Next Best Action"
    slide.placeholders[1].text = "Executive Report"

    for i, sec in enumerate(sections[:6]):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"Insight {i+1}"
        slide.placeholders[1].text = sec[:800]

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer


# -----------------------------
# SMART REGION TABLE PARSER
# -----------------------------
def parse_region_data(text):

    lines = text.split("\n")
    data = []

    priority_map = {
        "🔴": 4,
        "🟠": 3,
        "🟡": 2,
        "🟢": 1
    }

    for line in lines:
        if any(p in line for p in priority_map.keys()):

            parts = line.split("\t") if "\t" in line else line.split("  ")

            if len(parts) >= 3:
                region = parts[0].strip()
                accounts = parts[1].strip()
                priority_raw = parts[2].strip()

                score = 0
                for k, v in priority_map.items():
                    if k in priority_raw:
                        score = v

                data.append({
                    "Region": region,
                    "Accounts": accounts,
                    "Priority": priority_raw,
                    "Score": score
                })

    if len(data) > 0:
        return pd.DataFrame(data)

    return None


# -----------------------------
# UI
# -----------------------------
st.markdown("## 💬 Next Best Action - Commercial Pharma")

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
    # OUTPUT TEXT
    # -----------------------------
    st.subheader("Response")
    st.info(reply)


    # -----------------------------
    # 📊 REGION CHART
    # -----------------------------
    df_regions = parse_region_data(reply)

    if df_regions is not None:
        st.subheader("📊 Regional Priority Insights")

        chart_df = df_regions.sort_values("Score", ascending=False)

        st.bar_chart(
            chart_df.set_index("Region")["Score"]
        )

        st.dataframe(df_regions)

    else:
        st.caption("No regional structured data detected.")


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
        st.error("PDF/PPT libraries not installed.")


elif submit and not prompt.strip():
    st.warning("Please enter a question.")
