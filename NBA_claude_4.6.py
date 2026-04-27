import streamlit as st
import requests
import json
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pptx import Presentation


# -----------------------------
# CONFIG
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v5%20Task"
API_KEY = "681vyxaddAuuuJ21FD7LOYVogX7B0dHB"

st.set_page_config("Commercial Pharma", "💬", layout="centered")


# -----------------------------
# SAFE PPT GENERATOR (EXECUTIVE VERSION)
# -----------------------------
def create_ppt(text):

    prs = Presentation()

    sections = [s.strip() for s in text.split("\n") if s.strip()]

    # ---------------- TITLE SLIDE ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Pharmaceutical Next Best Action"
    slide.placeholders[1].text = "Executive Intelligence Report"

    # ---------------- EXECUTIVE SUMMARY ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"

    summary = sections[:3]
    slide.placeholders[1].text = " | ".join(summary)[:900]

    # ---------------- KEY INSIGHTS ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Insights"

    insights = sections[3:6]
    slide.placeholders[1].text = "\n".join(insights)[:1000]

    # ---------------- STRATEGIC ACTIONS ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Strategic Actions"

    actions = sections[6:9]
    slide.placeholders[1].text = "\n".join(actions)[:1000]

    # ---------------- FINAL RECOMMENDATION ----------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Next Best Actions"

    slide.placeholders[1].text = text[:1200]

    return prs


# -----------------------------
# UI
# -----------------------------
st.markdown("## 💬 Next Best Action - Pharma Executive System")


with st.form("form"):
    prompt = st.text_area("Enter query", height=120)

    role = st.radio(
        "Role",
        ["Sales Representative", "Market Access Specialist", "Medical Science Liaison (MSL)"]
    )

    submit = st.form_submit_button("Generate")


# -----------------------------
# API CALL
# -----------------------------
if submit and prompt.strip():

    with st.spinner("Generating Executive NBA..."):

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
            reply = str(e)


    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("Response")
    st.info(reply)


    # -----------------------------
    # PPT DOWNLOAD
    # -----------------------------
    ppt = create_ppt(reply)

    buffer = BytesIO()
    ppt.save(buffer)
    buffer.seek(0)

    st.download_button(
        "📊 Download Executive PPT",
        buffer,
        file_name="Pharma_Executive_NBA.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
