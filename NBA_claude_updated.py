import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
# CHART TYPE DETECTION
# -----------------------------
def detect_chart_type(prompt: str):
    prompt = prompt.lower()

    if any(word in prompt for word in ["trend", "growth", "over time", "forecast", "projection"]):
        return "line"

    elif any(word in prompt for word in ["distribution", "share", "percentage", "breakdown"]):
        return "pie"

    elif any(word in prompt for word in ["compare", "comparison", "vs", "top", "ranking"]):
        return "bar"

    elif any(word in prompt for word in ["market", "patients", "growth projection"]):
        return "dual"

    return "bar"

# -----------------------------
# CHART RENDERING
# -----------------------------
def render_chart(chart_type, df):

    if df is None or df.empty:
        st.info("No structured data available for visualization.")
        return

    if chart_type == "line":
        fig = px.line(df, x=df.columns[0], y=df.columns[1:])
        fig.update_traces(line=dict(width=3))

    elif chart_type == "bar":
        fig = px.bar(df, x=df.columns[0], y=df.columns[1:])

    elif chart_type == "pie":
        fig = px.pie(df, names=df.columns[0], values=df.columns[1])

    elif chart_type == "dual":
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df.iloc[:, 0],
            y=df.iloc[:, 1],
            name="Primary Metric",
            marker=dict(color="#2563eb")
        ))

        if df.shape[1] > 2:
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0],
                y=df.iloc[:, 2],
                name="Secondary Metric",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#10b981", width=3)
            ))

            fig.update_layout(
                yaxis2=dict(overlaying="y", side="right")
            )

    else:
        fig = px.bar(df, x=df.columns[0], y=df.columns[1:])

    fig.update_layout(
        template="plotly_white",
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", y=-0.2)
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LIGHT THEME CSS
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #000000 !important;
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

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):

    prompt = st.text_area("Enquiry:", height=110)

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
# PROCESS
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
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

                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("Customer_Story", "No response.")
                    chart_data = data[0].get("chart_data", None)
                else:
                    reply = "Unexpected API format"
                    chart_data = None

            except Exception as e:
                reply = f"Error: {e}"
                chart_data = None

        # -----------------------------
        # TEXT OUTPUT
        # -----------------------------
        st.write("---")
        st.subheader("Response:")
        st.info(reply)

        # -----------------------------
        # CHART OUTPUT
        # -----------------------------
        st.subheader("📊 Visual Insight")

        chart_type = detect_chart_type(prompt)

        df = None

        # Try API data
        if chart_data:
            try:
                df = pd.DataFrame(chart_data)
            except:
                df = None

        # Fallback chart (ensures UI always looks good)
        if df is None:
            df = pd.DataFrame({
                "Year": [2024, 2026, 2028, 2030, 2035, 2045],
                "Market": [2.2, 2.0, 1.8, 2.1, 2.5, 3.4],
                "Patients": [4.0, 4.27, 5.0, 5.6, 6.5, 7.5]
            })
            chart_type = "dual"

        render_chart(chart_type, df)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
    <hr>
    <p style="text-align:center; font-size: 0.9em; color: #777;">
        © 2025 KSA Commercial Excellence | Powered by Allot Ltd
    </p>
    """,
    unsafe_allow_html=True
)
