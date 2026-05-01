import streamlit as st
import requests
import json
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# CONFIGURATION
# -----------------------------
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/projects/Tejasri%20Reddy%20Beeram/Diabetes_v5%20Task"
API_KEY = st.secrets.get("API_KEY", "681vyxaddAuuuJ21FD7LOYVogX7B0dHB")

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
    max-width: 1150px;
    padding-top: 2rem;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #000 !important;
}

[data-testid="stForm"] {
    background-color: #f8fafc !important;
    padding: 24px !important;
    border-radius: 16px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}

.stTextArea textarea {
    color: #000 !important;
    background-color: #fff !important;
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
}

button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 0.7em 1.4em !important;
    border: none !important;
    font-weight: 600 !important;
}

.metric-card {
    background: #ffffff;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

.insight-box {
    background:#ffffff;
    padding:22px;
    border-radius:16px;
    border:1px solid #e5e7eb;
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
    line-height:1.7;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def detect_chart_type(prompt: str, reply: str = ""):
    text = f"{prompt} {reply}".lower()

    if any(w in text for w in ["share", "percentage", "distribution", "breakdown", "mix"]):
        return "pie"

    if any(w in text for w in ["trend", "growth", "projection", "forecast", "over time", "year"]):
        return "line"

    if any(w in text for w in ["market", "patients", "patient", "dual", "cagr"]):
        return "dual"

    if any(w in text for w in ["ranking", "rank", "top", "compare", "comparison", "volume", "sales", "hospital"]):
        return "bar"

    return "bar"


def extract_ranked_data_from_text(text: str):
    """
    Extracts lines like:
    King Abdulaziz Medical City (NGHA)      452.04
    Najran General Hospital                162.58
    """
    rows = []

    for line in text.splitlines():
        clean = line.strip()

        if not clean:
            continue

        match = re.search(r"^(.+?)\s+([0-9]+(?:\.[0-9]+)?)$", clean)

        if match:
            name = match.group(1).strip()
            value = float(match.group(2))

            ignore_words = [
                "scale", "chart", "top", "total", "cagr",
                "patient growth", "benchmark"
            ]

            if not any(w in name.lower() for w in ignore_words):
                rows.append({
                    "Category": name,
                    "Value": value
                })

    if rows:
        df = pd.DataFrame(rows)
        df = df.drop_duplicates()
        return df

    return None


def extract_year_market_patient_data(text: str):
    """
    Extracts common year-based values from chart-style text if possible.
    Fallback is used if no structured data exists.
    """
    years = re.findall(r"\b(20[0-9]{2})\b", text)
    numeric_values = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*(?:B|M|million|bn)?", text, flags=re.I)

    if len(years) >= 3 and len(numeric_values) >= len(years):
        unique_years = []
        for y in years:
            if y not in unique_years:
                unique_years.append(y)

        values = [float(v) for v in numeric_values if float(v) < 10000]

        if len(values) >= len(unique_years):
            return pd.DataFrame({
                "Year": unique_years[:len(values)],
                "Value": values[:len(unique_years)]
            })

    return None


def build_dataframe(reply, chart_data=None):
    """
    Priority:
    1. API chart_data
    2. Extract hospital/ranked data from text
    3. Extract year-based data from text
    4. Fallback demo data
    """

    if chart_data:
        try:
            df = pd.DataFrame(chart_data)
            if not df.empty:
                return df
        except Exception:
            pass

    ranked_df = extract_ranked_data_from_text(reply)
    if ranked_df is not None and not ranked_df.empty:
        return ranked_df

    year_df = extract_year_market_patient_data(reply)
    if year_df is not None and not year_df.empty:
        return year_df

    return pd.DataFrame({
        "Year": [2024, 2026, 2028, 2030, 2035, 2045],
        "Market Value USD Bn": [2.2, 2.4, 2.7, 3.0, 3.8, 5.0],
        "Patients Millions": [4.0, 4.27, 5.0, 5.6, 6.5, 7.5]
    })


def render_chart(chart_type, df, title="Visual Insight"):
    if df is None or df.empty:
        st.info("No chart data available.")
        return

    columns = list(df.columns)

    # Ranking / hospital-style horizontal bar
    if chart_type == "bar":
        value_col = columns[1]
        category_col = columns[0]

        df_plot = df.copy()
        df_plot[value_col] = pd.to_numeric(df_plot[value_col], errors="coerce")
        df_plot = df_plot.dropna(subset=[value_col])
        df_plot = df_plot.sort_values(value_col, ascending=True)

        fig = px.bar(
            df_plot,
            x=value_col,
            y=category_col,
            orientation="h",
            text=value_col,
            title=title
        )

        fig.update_traces(
            marker_color="#0f5aa6",
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            height=max(520, len(df_plot) * 36),
            xaxis_title="",
            yaxis_title="",
            template="plotly_white",
            font=dict(family="Inter, Arial", size=13),
            title_font=dict(size=22),
            margin=dict(l=20, r=80, t=70, b=30),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff"
        )

    elif chart_type == "line":
        fig = px.line(
            df,
            x=columns[0],
            y=columns[1:],
            markers=True,
            title=title
        )

        fig.update_traces(line=dict(width=4), marker=dict(size=9))

        fig.update_layout(
            height=520,
            template="plotly_white",
            font=dict(family="Inter, Arial", size=13),
            title_font=dict(size=22),
            legend=dict(orientation="h", y=-0.18),
            margin=dict(l=30, r=30, t=70, b=50)
        )

    elif chart_type == "pie":
        fig = px.pie(
            df,
            names=columns[0],
            values=columns[1],
            title=title,
            hole=0.35
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig.update_layout(
            height=520,
            template="plotly_white",
            font=dict(family="Inter, Arial", size=13),
            title_font=dict(size=22),
            margin=dict(l=30, r=30, t=70, b=30)
        )

    elif chart_type == "dual" and len(columns) >= 3:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df[columns[0]],
            y=df[columns[1]],
            name=columns[1],
            marker_color="#0f5aa6",
            text=df[columns[1]],
            textposition="outside"
        ))

        fig.add_trace(go.Scatter(
            x=df[columns[0]],
            y=df[columns[2]],
            name=columns[2],
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#10b981", width=4),
            marker=dict(size=9)
        ))

        fig.update_layout(
            title=title,
            height=520,
            template="plotly_white",
            font=dict(family="Inter, Arial", size=13),
            title_font=dict(size=22),
            yaxis=dict(title=columns[1]),
            yaxis2=dict(
                title=columns[2],
                overlaying="y",
                side="right"
            ),
            legend=dict(orientation="h", y=-0.18),
            margin=dict(l=40, r=50, t=70, b=50)
        )

    else:
        value_col = columns[1]
        category_col = columns[0]

        fig = px.bar(
            df,
            x=category_col,
            y=value_col,
            text=value_col,
            title=title
        )

        fig.update_traces(
            marker_color="#0f5aa6",
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            height=520,
            template="plotly_white",
            font=dict(family="Inter, Arial", size=13),
            title_font=dict(size=22),
            margin=dict(l=30, r=30, t=70, b=50)
        )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:10px;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png"
             alt="Allot Logo" width="260">
        <br><br>
        <a href="https://www.allotltd.com/"
            style="text-decoration:none; font-size:22px; color:#2563eb; font-weight:600;">
            www.allotltd.com
        </a>
    </div>
    <hr style="margin-top: 2em; opacity:0.3;">
    """,
    unsafe_allow_html=True
)

# -----------------------------
# PAGE TITLE
# -----------------------------
st.markdown("## 💬 Next Best Action for Commercial Pharma")
st.caption("KSA Diabetes Market | Commercial Excellence Dashboard")

# -----------------------------
# OVERVIEW
# -----------------------------
with st.expander("📘 Overview", expanded=True):
    st.markdown(
        """
This application offers **Next Best Actions (NBAs)** for commercial, sales, market access, and medical pharmaceutical field teams.

It focuses on the **diabetes market in the Kingdom of Saudi Arabia (KSA)** and uses internal sales, CRM call notes, medical data, external market policy, healthcare data, publications, and congress information.

### ⚠️ Data Limitations
This demo reflects Saudi Arabia diabetes market data, including:
- Sales data
- HCP profiles
- Call notes
- Market summaries
- Scientific publication data
        """
    )

with st.expander("💡 Sample Questions"):
    st.markdown(
        """
**Sales Representative**
- Analyse call notes data and generate NBA for high-potential prescribers of Empagliflozin and explain why.
- Show top hospitals by total drug volume.

**Market Access Specialist**
- Give me the Market Access Strategy for five hospitals with greatest number of diabetes patients.
- Compare hospitals by reimbursement status and market opportunity.

**Medical Science Liaison (MSL)**
- Analyze call notes for MSL follow-up requests or complex clinical questions flagged by the Sales Team.
- Identify KOLs requesting specific data and generate NBA.
        """
    )

st.write("---")

# -----------------------------
# INPUT FORM
# -----------------------------
with st.form("chat_form", clear_on_submit=False):

    st.subheader("Enquiry")
    prompt = st.text_area(
        "",
        placeholder="Type your question here...",
        height=120
    )

    st.subheader("Select role")
    role = st.radio(
        "",
        [
            "Sales Representative",
            "Market Access Specialist",
            "Medical Science Liaison (MSL)"
        ],
        index=0,
        horizontal=True
    )

    submitted = st.form_submit_button("🚀 Send")

# -----------------------------
# PROCESS SUBMISSION
# -----------------------------
if submitted:

    if not prompt.strip():
        st.warning("Please enter a question before sending.")

    else:
        with st.spinner(f"Fetching response for {role}..."):

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
                    reply = data[0].get("Customer_Story", "No response returned.")
                    chart_data = data[0].get("chart_data", None)
                else:
                    reply = f"Unexpected API response format: {data}"
                    chart_data = None

            except requests.exceptions.Timeout:
                reply = "⚠️ Request timed out. Please try again."
                chart_data = None

            except requests.exceptions.RequestException as e:
                reply = f"⚠️ API Error: {e}"
                chart_data = None

            except Exception as e:
                reply = f"⚠️ Unexpected Error: {e}"
                chart_data = None

        st.write("---")

        # -----------------------------
        # RESPONSE + CHART
        # -----------------------------
        left, right = st.columns([0.95, 1.55], gap="large")

        with left:
            st.subheader("💡 Response")
            st.markdown(
                f"""
                <div class="insight-box">
                    {reply.replace(chr(10), "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:
            st.subheader("📊 Power BI Style Visual")

            df = build_dataframe(reply, chart_data)
            chart_type = detect_chart_type(prompt, reply)

            # If extracted response has Category/Value, force ranking bar
            if list(df.columns)[:2] == ["Category", "Value"]:
                chart_type = "bar"

            render_chart(
                chart_type,
                df,
                title="Commercial Pharma Visual Insight"
            )

            with st.expander("View extracted chart data"):
                st.dataframe(df, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
    <hr style="margin-top: 3em; opacity:0.3;">
    <p style="text-align:center; font-size: 0.9em; color: #777;">
        © 2025 KSA Commercial Excellence | Powered by Allot Ltd
    </p>
    """,
    unsafe_allow_html=True
)
