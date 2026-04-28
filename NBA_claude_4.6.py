import streamlit as st
import requests
import json
from io import BytesIO
import pandas as pd
import numpy as np

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
# PDF
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
# PPT
# -----------------------------
def create_ppt(text):
    prs = Presentation()
    sections = [s.strip() for s in text.split("\n") if s.strip()]

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Pharma NBA"
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
# 🔥 SMART PARSER (REGION DATA)
# -----------------------------
def parse_region(text):

    priority_score = {"🔴": 4, "🟠": 3, "🟡": 2, "🟢": 1}

    lines = text.split("\n")
    data = []

    for line in lines:
        for symbol, score in priority_score.items():
            if symbol in line and "-" in line:
                parts = line.split("\t") if "\t" in line else line.split("  ")

                if len(parts) >= 3:
                    region = parts[0].strip()
                    accounts = parts[1].strip()
                    priority = parts[2].strip()

                    data.append({
                        "Region": region,
                        "Score": score,
                        "Accounts": len(accounts.split(","))
                    })

    return pd.DataFrame(data) if len(data) > 0 else None


# -----------------------------
# UI
# -----------------------------
st.markdown("## 💬 Next Best Action - Pharma AI")


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

    with st.spinner("Generating..."):

        payload = [{"question_type": role, "prompt": prompt}]
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        data = res.json()

        reply = data[0]["Customer_Story"] if isinstance(data, list) else str(data)


    # -----------------------------
    # TEXT OUTPUT
    # -----------------------------
    st.subheader("Response")
    st.info(reply)


    # -----------------------------
    # 📊 BAR CHART + 📈 GRAPH VIEW
    # -----------------------------
    df = parse_region(reply)

    if df is not None and not df.empty:

        st.subheader("📊 Regional Priority (Bar Chart)")
        st.bar_chart(df.set_index("Region")["Score"])

        st.subheader("📈 Trend View (Line Graph)")
        df_sorted = df.sort_values("Score")
        st.line_chart(df_sorted.set_index("Region")["Score"])

        st.subheader("📊 Engagement Impact (Bubble View)")
        st.scatter_chart(df.set_index("Region")[["Score", "Accounts"]])

    else:
        st.caption("No structured region data found for visualization.")


    # -----------------------------
    # DOWNLOADS
    # -----------------------------
    st.subheader("⬇️ Downloads")

    if LIBS_AVAILABLE:

        pdf = create_pdf(reply)
        ppt = create_ppt(reply)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button("📄 PDF", pdf, "NBA.pdf", "application/pdf")

        with col2:
            st.download_button(
                "📊 PPT",
                ppt,
                "NBA.pptx",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

    else:
        st.error("Install reportlab + python-pptx")


elif submit and not prompt.strip():
    st.warning("Enter a query")
