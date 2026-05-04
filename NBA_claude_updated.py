import streamlit as st
import requests
import json
import re
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
    layout="wide"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

.report-card {
    background: #f8fbff;
    border: 1px solid #dbeafe;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
}

h1, h2, h3 {
    color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CLEAN ASCII CHARTS FROM LLM TEXT
# -----------------------------
def remove_ascii_charts(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    cleaned_lines = []
    skip_block = False

    section_starters = [
        "Applied Theory",
        "Key Findings",
        "Detailed Response",
        "Recommendations",
        "Downloadable Outputs",
        "Section",
        "🎓",
        "🔴",
        "📋"
    ]

    ascii_chars = ["╔", "╗", "╚", "╝", "║", "═", "█", "▌", "─", "┌", "┐", "└", "┘"]

    for line in lines:
        stripped = line.strip()

        if re.match(r"^📊\s*CHART\s*\d+", stripped, re.IGNORECASE):
            skip_block = True
            continue

        if any(ch in stripped for ch in ["╔", "║", "╚"]):
            skip_block = True
            continue

        if skip_block and any(stripped.startswith(s) for s in section_starters):
            skip_block = False

        if skip_block:
            if (
                any(ch in stripped for ch in ascii_chars)
                or re.search(r"\[[█\s▌]+\]", stripped)
                or re.search(r"[●★]{1,}", stripped)
            ):
                continue

        if not skip_block:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    cleaned_text = re.sub(
        r"► TO GENERATE:.*?(?=\n\n|\Z)",
        "",
        cleaned_text,
        flags=re.DOTALL
    )

    return cleaned_text.strip()

# -----------------------------
# CHART TYPE DETECTION
# -----------------------------
def detect_chart_type(prompt: str):
    prompt = prompt.lower()

    if any(word in prompt for word in ["trend", "growth", "over time", "forecast", "projection"]):
        return "line"

    if any(word in prompt for word in ["distribution", "share", "percentage", "breakdown", "mix"]):
        return "pie"

    if any(word in prompt for word in ["compare", "comparison", "vs", "top", "ranking", "rank"]):
        return "bar"

    if any(word in prompt for word in ["market", "patients", "growth projection"]):
        return "dual"

    return "bar"

# -----------------------------
# DATAFRAME HELPERS
# -----------------------------
def make_dataframe(raw_data):
    if raw_data is None:
        return None

    try:
        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data)

        df = pd.DataFrame(raw_data)

        if df.empty:
            return None

        return df

    except Exception:
        return None

def default_market_df():
    return pd.DataFrame({
        "Year": [2024, 2026, 2028, 2030, 2035, 2045],
        "Market Size USD Bn": [2.0, 2.3, 2.7, 3.4, None, None],
        "Patients Mn": [4.27, 4.8, 5.2, 5.6, 6.5, 7.5]
    })

def default_hcp_priority_df():
    return pd.DataFrame({
        "Name": [
            "Al-Muhanna",
            "Alghamdi K.S.",
            "Ba Hamid",
            "Al-Quorain A.",
            "Al-Rubeaan",
            "Sulaiman R.",
            "Al-Quorain Abd",
            "Al-Sultan",
            "Al-Ghamdi K.",
            "Alshareef M.",
            "Al-Ali A.",
            "Al-Somali",
            "Al-Habib",
            "Aljohani N."
        ],
        "Patients": [5432, 3456, 1320, 1234, 1220, 987, 956, 828, 768, 765, 765, 756, 354, 342],
        "Visits": [3, 2, 4, 2, 2, 6, 6, 6, 1, 0, 4, 1, 3, 3],
        "Priority": [
            "URGENT", "HIGH", "DEVELOP", "DEVELOP", "DEVELOP",
            "MAINTAIN", "MAINTAIN", "MAINTAIN", "DEVELOP",
            "COLD", "DEVELOP", "DEVELOP", "DEVELOP", "DEVELOP"
        ],
        "Action": [
            "Upgrade to Tier-1 MSL + Sales",
            "Initiate MSL nephropathy track",
            "Eastern Province lead role",
            "Research engagement",
            "KOL depth investment",
            "Advocacy deepening",
            "Stable advocate",
            "Research collaboration",
            "Diabetic foot public health",
            "Immediate reactivation",
            "Active development",
            "Tertiary hospital access",
            "Private network",
            "Obesity / Endo focus"
        ]
    })

def default_hospital_df():
    return pd.DataFrame({
        "Hospital": [
            "King Abdulaziz Medical City",
            "King Fahd Medical City",
            "International Medical Center",
            "Security Forces Hospital",
            "King Faisal Specialist Hospital",
            "Prince Sultan Military Medical City",
            "King Saud University Medical City",
            "Dr. Sulaiman Al Habib Medical Group",
            "Dallah Hospital",
            "King Fahd Specialist Hospital Dammam",
            "Saudi German Hospital Jeddah",
            "King Abdulaziz University Hospital"
        ],
        "Prescription Volume": [
            452.04, 425.16, 400.84, 387.26, 378.82, 332.16,
            303.74, 279.02, 253.77, 248.29, 232.91, 184.87
        ]
    })

# -----------------------------
# CHART RENDERING
# -----------------------------
def render_chart(chart_type, df, title="Visual Insight"):
    if df is None or df.empty:
        st.info("No structured data available for visualization.")
        return

    df = df.copy()

    for col in df.columns:
        if col != df.columns[0]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(df.columns) < 2:
        st.info("Not enough columns to build a chart.")
        return

    x_col = df.columns[0]

    try:
        if chart_type == "line":
            fig = px.line(
                df,
                x=x_col,
                y=numeric_cols,
                markers=True,
                title=title
            )
            fig.update_traces(line=dict(width=3))

        elif chart_type == "pie":
            value_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.pie(
                df,
                names=x_col,
                values=value_col,
                title=title,
                hole=0.4
            )

        elif chart_type == "dual":
            fig = go.Figure()

            if not numeric_cols:
                st.info("No numeric columns available for chart.")
                return

            primary_col = numeric_cols[0]

            fig.add_trace(go.Bar(
                x=df[x_col],
                y=df[primary_col],
                name=primary_col
            ))

            if len(numeric_cols) > 1:
                secondary_col = numeric_cols[1]

                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[secondary_col],
                    name=secondary_col,
                    yaxis="y2",
                    mode="lines+markers",
                    line=dict(width=3)
                ))

                fig.update_layout(
                    yaxis2=dict(
                        title=secondary_col,
                        overlaying="y",
                        side="right"
                    )
                )

            fig.update_layout(title=title)

        else:
            if not numeric_cols:
                st.info("No numeric columns available for chart.")
                return

            fig = px.bar(
                df,
                x=x_col,
                y=numeric_cols,
                title=title,
                barmode="group"
            )

        fig.update_layout(
            template="plotly_white",
            height=480,
            margin=dict(l=30, r=30, t=70, b=40),
            font=dict(family="Arial, sans-serif", size=13),
            legend=dict(orientation="h", y=-0.25),
            title=dict(x=0.02)
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Chart rendering error: {e}")

# -----------------------------
# DEFAULT DASHBOARD
# -----------------------------
def render_hcp_section():
    st.subheader("📋 HCP Priority Matrix")

    hcp_df = default_hcp_priority_df()

    st.dataframe(
        hcp_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.scatter(
        hcp_df,
        x="Patients",
        y="Visits",
        size="Patients",
        color="Priority",
        hover_name="Name",
        text="Name",
        title="HCP Engagement vs Patient Potential"
    )

    fig.update_traces(textposition="top center")

    fig.update_layout(
        template="plotly_white",
        height=520,
        margin=dict(l=30, r=30, t=70, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

def render_default_dashboard():
    st.subheader("📊 Market Growth Projection")
    render_chart("dual", default_market_df(), "KSA Diabetes Market Growth Projection")

    st.subheader("🏥 Hospital Prescription Volume")

    hospital_df = default_hospital_df()

    fig = px.bar(
        hospital_df.sort_values("Prescription Volume"),
        x="Prescription Volume",
        y="Hospital",
        orientation="h",
        title="Top Hospital Accounts by Prescription Volume"
    )

    fig.update_layout(
        template="plotly_white",
        height=560,
        margin=dict(l=30, r=30, t=70, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    render_hcp_section()

def pdf_export_note():
    st.info(
        "PDF tip: use browser Print → Save as PDF after all charts finish loading. "
        "This version removes text-based ASCII charts and displays real charts/tables."
    )

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:10px;">
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

st.markdown("## 💬 Next Best Action for Commercial Pharma")

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form"):
    prompt = st.text_area("Enquiry:", height=120)

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
        reply = ""
        chart_data = None
        table_data = None

        with st.spinner("Fetching response..."):
            payload = [{"question_type": role, "prompt": prompt}]

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    API_URL,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=300
                )

                response.raise_for_status()
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("Customer_Story", "No response.")
                    chart_data = data[0].get("chart_data", None)
                    table_data = data[0].get("table_data", None)

                elif isinstance(data, dict):
                    reply = data.get("Customer_Story", "No response.")
                    chart_data = data.get("chart_data", None)
                    table_data = data.get("table_data", None)

                else:
                    reply = "Unexpected API format."

            except requests.exceptions.Timeout:
                reply = (
                    "The API request timed out. The dashboard below is showing fallback visuals. "
                    "Please try again or check the SnapLogic task runtime."
                )

            except Exception as e:
                reply = f"Error while calling API: {e}"

        # -----------------------------
        # RESPONSE TEXT
        # -----------------------------
        st.write("---")
        st.subheader("Response")

        cleaned_reply = remove_ascii_charts(reply)

        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.markdown(cleaned_reply)
        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # API TABLE
        # -----------------------------
        table_df = make_dataframe(table_data)

        if table_df is not None:
            st.subheader("📋 Structured Table")
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True
            )

        # -----------------------------
        # VISUALS
        # -----------------------------
        st.subheader("📊 Visual Insights")

        chart_df = make_dataframe(chart_data)

        if chart_df is not None:
            chart_type = detect_chart_type(prompt)
            render_chart(chart_type, chart_df, "API Generated Visual Insight")
        else:
            render_default_dashboard()

        pdf_export_note()

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
