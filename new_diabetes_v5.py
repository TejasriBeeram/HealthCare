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
API_TIMEOUT_SECONDS = 600

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
    max-width: 1250px;
    padding-top: 2rem;
}

.report-card {
    background: #f8fbff;
    border: 1px solid #dbeafe;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 22px;
    line-height: 1.65;
}

.chart-card, .table-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 28px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

h1, h2, h3 {
    color: #0f172a;
}

@media print {
    .stButton, .stTextArea, .stRadio, .stForm {
        display: none !important;
    }

    .chart-card, .report-card, .table-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }

    [data-testid="stHeader"] {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def extract_json_from_text(text):
    if not text:
        return None

    if isinstance(text, dict):
        return text

    try:
        return json.loads(text)
    except Exception:
        pass

    text = str(text).strip()

    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None

    return None


def safe_numeric_convert(df):
    df = df.copy()

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")

        # Only replace if at least one value converted successfully
        if converted.notna().sum() > 0:
            df[col] = converted

    return df


def remove_ascii_charts(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text)

    cleaned = re.sub(
        r"Visual Data Analysis.*?(?=(Theoretical|Applied Theory|Key Findings|Detailed Response|Recommendations|$))",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    cleaned = re.sub(
        r"📊\s*CHART\s*\d+.*?(?=📊\s*CHART\s*\d+|Theoretical|Applied Theory|Key Findings|Detailed Response|Recommendations|$)",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    cleaned = re.sub(r"[┌╔].*?[┘╝]", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"Downloadable Outputs.*", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"📊 Visual Insights.*", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    return cleaned.strip()


def chart_card_start(title):
    st.markdown(f"<div class='chart-card'><h3>{title}</h3>", unsafe_allow_html=True)


def table_card_start(title):
    st.markdown(f"<div class='table-card'><h3>{title}</h3>", unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def normalize_charts(charts):
    if charts is None:
        return []

    if isinstance(charts, str):
        parsed = extract_json_from_text(charts)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return parsed.get("charts", [])

    if isinstance(charts, dict):
        return [charts]

    if isinstance(charts, list):
        return charts

    return []


def normalize_tables(tables):
    if tables is None:
        return []

    if isinstance(tables, str):
        parsed = extract_json_from_text(tables)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return parsed.get("tables", [])

    if isinstance(tables, dict):
        return [tables]

    if isinstance(tables, list):
        return tables

    return []


def make_dataframe(data):
    if not data:
        return pd.DataFrame()

    if isinstance(data, str):
        parsed = extract_json_from_text(data)
        data = parsed if parsed is not None else []

    try:
        df = pd.DataFrame(data)
        return safe_numeric_convert(df)
    except Exception:
        return pd.DataFrame()

# -----------------------------
# DYNAMIC CHART RENDERER
# -----------------------------
def render_dynamic_chart(chart):
    if not isinstance(chart, dict):
        return

    title = chart.get("title", "Chart")
    chart_type = str(chart.get("type", "bar")).lower().strip()

    data = chart.get("data", [])
    df = make_dataframe(data)

    if df.empty or len(df.columns) < 2:
        st.warning(f"No valid data available for chart: {title}")
        return

    x = chart.get("x", df.columns[0])
    y = chart.get("y", df.columns[1])
    secondary_y = chart.get("secondary_y")
    size = chart.get("size")
    color = chart.get("color")
    value = chart.get("value")

    if x not in df.columns:
        x = df.columns[0]

    if y not in df.columns:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        y = numeric_cols[0] if numeric_cols else df.columns[1]

    chart_card_start(title)

    try:
        if chart_type == "bar":
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                text=y
            )

        elif chart_type in ["horizontal_bar", "hbar"]:
            fig = px.bar(
                df,
                x=y,
                y=x,
                orientation="h",
                color=color if color in df.columns else None,
                text=y
            )

        elif chart_type == "line":
            fig = px.line(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                markers=True
            )

        elif chart_type == "pie":
            fig = px.pie(
                df,
                names=x,
                values=y,
                hole=0.45
            )

        elif chart_type in ["scatter", "bubble"]:
            fig = px.scatter(
                df,
                x=x,
                y=y,
                size=size if size in df.columns else None,
                color=color if color in df.columns else None,
                hover_name=x,
                text=x
            )
            fig.update_traces(textposition="top center")

        elif chart_type in ["dual_axis", "dual"]:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df[x],
                y=df[y],
                name=y
            ))

            if secondary_y and secondary_y in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[x],
                    y=df[secondary_y],
                    name=secondary_y,
                    mode="lines+markers",
                    yaxis="y2"
                ))

                fig.update_layout(
                    yaxis2=dict(
                        title=secondary_y,
                        overlaying="y",
                        side="right"
                    )
                )

            fig.update_layout(yaxis=dict(title=y))

        elif chart_type == "heatmap":
            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            if not numeric_cols:
                st.warning(f"No numeric values available for heatmap: {title}")
                st.dataframe(df, use_container_width=True, hide_index=True)
                card_end()
                return

            heat_value = value if value in df.columns else numeric_cols[0]

            heat_df = df.pivot_table(
                index=y,
                columns=x,
                values=heat_value,
                aggfunc="mean"
            )

            fig = px.imshow(
                heat_df,
                aspect="auto",
                text_auto=True
            )

        elif chart_type == "funnel":
            fig = px.funnel(
                df,
                x=y,
                y=x
            )

        elif chart_type == "area":
            fig = px.area(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None
            )

        else:
            fig = px.bar(df, x=x, y=y, text=y)

        fig.update_layout(
            template="plotly_white",
            height=500,
            margin=dict(l=20, r=40, t=30, b=30),
            legend=dict(orientation="h", y=-0.2)
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Could not render chart '{title}': {e}")
        st.dataframe(df, use_container_width=True, hide_index=True)

    card_end()

# -----------------------------
# TABLE RENDERER
# -----------------------------
def render_dynamic_table(table):
    if not isinstance(table, dict):
        return

    title = table.get("title", "Table")
    data = table.get("data", [])

    df = make_dataframe(data)

    if df.empty:
        return

    table_card_start(title)
    st.dataframe(df, use_container_width=True, hide_index=True)
    card_end()

# -----------------------------
# API CALL
# -----------------------------
def call_api(prompt, role):
    payload = [{
        "question_type": role,
        "prompt": prompt
    }]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=API_TIMEOUT_SECONDS
    )

    response.raise_for_status()
    data = response.json()

    if isinstance(data, list) and data:
        result = data[0]
    elif isinstance(data, dict):
        result = data
    else:
        return {
            "Customer_Story": "Unexpected API format.",
            "charts": [],
            "tables": []
        }

    customer_story = result.get("Customer_Story", "")
    charts = result.get("charts", [])
    tables = result.get("tables", [])

    parsed_story = extract_json_from_text(customer_story)
    if isinstance(parsed_story, dict):
        customer_story = parsed_story.get("Customer_Story", customer_story)
        charts = parsed_story.get("charts", charts)
        tables = parsed_story.get("tables", tables)

    for key in ["response", "result", "answer", "output"]:
        if key in result:
            parsed = extract_json_from_text(result[key])
            if isinstance(parsed, dict):
                customer_story = parsed.get("Customer_Story", customer_story)
                charts = parsed.get("charts", charts)
                tables = parsed.get("tables", tables)

    return {
        "Customer_Story": customer_story,
        "charts": normalize_charts(charts),
        "tables": normalize_tables(tables)
    }

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:10px;">
        <img src="https://allot.123-web.uk/wp-content/uploads/2018/12/logo-2.png" width="260">
        <br><br>
        <a href="https://www.allotltd.com/" style="font-size:22px; color:#2563eb;">
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
# MAIN PROCESS
# -----------------------------
if submitted:
    if not prompt.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner(f"Fetching response... this can take up to {API_TIMEOUT_SECONDS} seconds"):
            try:
                result = call_api(prompt, role)

            except requests.exceptions.Timeout:
                result = {
                    "Customer_Story": (
                        "The API request timed out. SnapLogic did not return within "
                        f"{API_TIMEOUT_SECONDS} seconds. Please check the SnapLogic pipeline runtime."
                    ),
                    "charts": [],
                    "tables": []
                }

            except Exception as e:
                result = {
                    "Customer_Story": f"Error while calling API: {e}",
                    "charts": [],
                    "tables": []
                }

        reply = remove_ascii_charts(result.get("Customer_Story", ""))
        charts = normalize_charts(result.get("charts", []))
        tables = normalize_tables(result.get("tables", []))

        st.write("---")
        st.subheader("Response")

        split_match = re.search(
            r"(Visual Data Analysis|Charts|Chart Analysis|Key Findings|Detailed Response|Recommendations|Applied Theory Sections|Theoretical Integration Points)",
            reply,
            flags=re.IGNORECASE
        )

        if split_match:
            top_text = reply[:split_match.start()].strip()
            bottom_text = reply[split_match.start():].strip()
        else:
            top_text = reply
            bottom_text = ""

        if top_text:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(top_text)
            st.markdown('</div>', unsafe_allow_html=True)

        if charts:
            st.markdown("## 📊 Visual Data Analysis")
            for chart in charts:
                render_dynamic_chart(chart)
        else:
            st.warning(
                "No structured chart data was returned. Check that SnapLogic returns `charts` as a JSON array."
            )

        if tables:
            st.markdown("## 📋 Tables")
            for table in tables:
                render_dynamic_table(table)

        if bottom_text:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(bottom_text)
            st.markdown('</div>', unsafe_allow_html=True)

        st.info(
            "PDF export tip: open the app in full screen, wait for charts to load, "
            "then use browser Print → Save as PDF."
        )

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
