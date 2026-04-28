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
# UI HEADER
# -----------------------------
st.markdown("## 💬 Next Best Action - Commercial Pharma")

# -----------------------------
# FORM
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


# -----------------------------
# 📊 ANALYTICS DASHBOARD
# -----------------------------
st.write("---")
st.header("📊 Pharma Analytics Dashboard")

@st.cache_data
def load_data():
    years = list(range(2018, 2025))
    countries = ["KSA", "UAE", "UK", "USA"]

    data = []
    for c in countries:
        base = np.random.randint(50, 100)
        for y in years:
            data.append({
                "Country": c,
                "Year": y,
                "Sales": base + np.random.randint(-10, 20)
            })

    return pd.DataFrame(data)

df = load_data()

# Filters
min_year = df["Year"].min()
max_year = df["Year"].max()

from_year, to_year = st.slider(
    "Select Year Range",
    min_year,
    max_year,
    (min_year, max_year)
)

countries = df["Country"].unique()

selected_countries = st.multiselect(
    "Select Markets",
    countries,
    default=list(countries)
)

# Filter data
filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"] >= from_year) &
    (df["Year"] <= to_year)
]

# Chart
st.subheader("📈 Sales Trend")
st.line_chart(filtered_df, x="Year", y="Sales", color="Country")

# Metrics
st.subheader("📊 Market Performance")

latest_year = filtered_df["Year"].max()
prev_year = latest_year - 1

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % 4]

    with col:
        latest = filtered_df[
            (filtered_df["Country"] == country) &
            (filtered_df["Year"] == latest_year)
        ]["Sales"].values

        prev = filtered_df[
            (filtered_df["Country"] == country) &
            (filtered_df["Year"] == prev_year)
        ]["Sales"].values

        if len(latest) > 0 and len(prev) > 0:
            growth = latest[0] - prev[0]

            st.metric(
                label=f"{country} Sales",
                value=f"{latest[0]}",
                delta=f"{growth}"
            )
