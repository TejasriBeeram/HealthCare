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
    max-width: 1280px;
    padding-top: 2rem;
}

.report-card {
    background: #f8fbff;
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: 26px;
    margin-bottom: 24px;
    line-height: 1.7;
    font-size: 15px;
}

.chart-card, .table-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 30px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
}

.chart-title {
    font-size: 22px;
    font-weight: 750;
    color: #0f172a;
    margin-bottom: 10px;
}

.insight-box {
    background: #eff6ff;
    border-left: 5px solid #2563eb;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 18px;
    color: #0f172a;
}

h1, h2, h3 {
    color: #0f172a;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
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
        if converted.notna().sum() > 0:
            df[col] = converted

    return df


def remove_ascii_charts(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text)

    cleaned = re.sub(
        r"📊\s*CHART\s*\d+.*?(?=📊\s*CHART\s*\d+|Theoretical|Applied Theory|Key Findings|Detailed Response|Recommendations|SECTION|$)",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    cleaned = re.sub(r"[┌╔].*?[┘╝]", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"Downloadable Outputs.*", "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    return cleaned.strip()


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", str(title or "").strip()).lower()


def chart_card_start(title, insight=None):
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)

    if insight:
        st.markdown(
            f"<div class='insight-box'><strong>Insight:</strong> {insight}</div>",
            unsafe_allow_html=True
        )


def table_card_start(title, insight=None):
    st.markdown("<div class='table-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='chart-title'>{title}</div>", unsafe_allow_html=True)

    if insight:
        st.markdown(
            f"<div class='insight-box'><strong>Insight:</strong> {insight}</div>",
            unsafe_allow_html=True
        )


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


def get_first_numeric_column(df, exclude=None):
    exclude = exclude or []
    numeric_cols = [
        col for col in df.select_dtypes(include="number").columns.tolist()
        if col not in exclude
    ]
    return numeric_cols[0] if numeric_cols else None


def apply_powerbi_layout(fig, height=520):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=30, r=40, t=35, b=45),
        font=dict(family="Arial, sans-serif", size=13, color="#1f2937"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="left",
            x=0
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Arial"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#edf2f7",
        zeroline=False,
        linecolor="#e5e7eb"
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#e5e7eb"
    )

    return fig

# -----------------------------
# DYNAMIC CHART RENDERER
# -----------------------------
def render_dynamic_chart(chart):
    if not isinstance(chart, dict):
        return

    title = chart.get("title", "Chart")
    insight = chart.get("insight", "")
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
    text_col = chart.get("text")

    if x not in df.columns:
        x = df.columns[0]

    if y not in df.columns:
        fallback_y = get_first_numeric_column(df, exclude=[x])
        y = fallback_y if fallback_y else df.columns[1]

    chart_card_start(title, insight)

    try:
        # -----------------------------
        # KPI CARD CHART
        # -----------------------------
        if chart_type in ["kpi", "card", "scorecard"]:
            numeric_col = y if y in df.columns else get_first_numeric_column(df)
            label_col = x if x in df.columns else df.columns[0]

            cols = st.columns(min(len(df), 4))

            for idx, (_, row) in enumerate(df.iterrows()):
                col = cols[idx % len(cols)]
                label = row.get(label_col, "")
                value_out = row.get(numeric_col, "")

                col.markdown(
                    f"""
                    <div style="
                        background:#eff6ff;
                        border:1px solid #bfdbfe;
                        border-radius:16px;
                        padding:20px;
                        text-align:center;
                        margin-bottom:12px;">
                        <div style="font-size:28px;font-weight:800;color:#1d4ed8;">{value_out}</div>
                        <div style="font-size:14px;color:#334155;">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            card_end()
            return

        # -----------------------------
        # HORIZONTAL BAR — best for rankings
        # -----------------------------
        if chart_type in ["horizontal_bar", "hbar", "ranking"]:
            if y in df.columns:
                df = df.sort_values(by=y, ascending=True)

            fig = px.bar(
                df,
                x=y,
                y=x,
                orientation="h",
                color=color if color in df.columns else None,
                text=y,
                hover_data=df.columns
            )

            fig.update_traces(
                texttemplate="%{text}",
                textposition="outside",
                marker_line_width=0,
                opacity=0.92
            )

            fig.update_layout(yaxis_title="", xaxis_title=y)

        # -----------------------------
        # VERTICAL BAR
        # -----------------------------
        elif chart_type == "bar":
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                text=y,
                hover_data=df.columns
            )

            fig.update_traces(
                texttemplate="%{text}",
                textposition="outside",
                marker_line_width=0,
                opacity=0.92
            )

        # -----------------------------
        # STACKED BAR
        # -----------------------------
        elif chart_type in ["stacked_bar", "stacked"]:
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                text=y,
                hover_data=df.columns
            )

            fig.update_layout(barmode="stack")

        # -----------------------------
        # LINE
        # -----------------------------
        elif chart_type == "line":
            fig = px.line(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                markers=True,
                hover_data=df.columns
            )

            fig.update_traces(line=dict(width=4), marker=dict(size=9))

        # -----------------------------
        # DONUT
        # -----------------------------
        elif chart_type in ["pie", "donut"]:
            fig = px.pie(
                df,
                names=x,
                values=y,
                hole=0.55
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                pull=[0.04] + [0] * (len(df) - 1)
            )

        # -----------------------------
        # BUBBLE / SCATTER
        # -----------------------------
        elif chart_type in ["scatter", "bubble"]:
            fig = px.scatter(
                df,
                x=x,
                y=y,
                size=size if size in df.columns else None,
                color=color if color in df.columns else None,
                hover_name=text_col if text_col in df.columns else x,
                text=text_col if text_col in df.columns else None,
                hover_data=df.columns,
                size_max=55
            )

            fig.update_traces(
                marker=dict(opacity=0.82, line=dict(width=1, color="white")),
                textposition="top center"
            )

        # -----------------------------
        # DUAL AXIS
        # -----------------------------
        elif chart_type in ["dual_axis", "dual"]:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df[x],
                y=df[y],
                name=y,
                opacity=0.85
            ))

            if secondary_y and secondary_y in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[x],
                    y=df[secondary_y],
                    name=secondary_y,
                    mode="lines+markers",
                    yaxis="y2",
                    line=dict(width=4),
                    marker=dict(size=9)
                ))

                fig.update_layout(
                    yaxis2=dict(
                        title=secondary_y,
                        overlaying="y",
                        side="right",
                        showgrid=False
                    )
                )

            fig.update_layout(yaxis=dict(title=y))

        # -----------------------------
        # HEATMAP
        # -----------------------------
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

        # -----------------------------
        # FUNNEL
        # -----------------------------
        elif chart_type == "funnel":
            fig = px.funnel(
                df,
                x=y,
                y=x,
                hover_data=df.columns
            )

        # -----------------------------
        # AREA
        # -----------------------------
        elif chart_type == "area":
            fig = px.area(
                df,
                x=x,
                y=y,
                color=color if color in df.columns else None,
                hover_data=df.columns
            )

        else:
            fig = px.bar(df, x=x, y=y, text=y, hover_data=df.columns)

        fig = apply_powerbi_layout(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

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
    insight = table.get("insight", "")
    data = table.get("data", [])
    df = make_dataframe(data)

    if df.empty:
        return

    table_card_start(title, insight)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    card_end()

# -----------------------------
# INLINE REPORT RENDERER
# -----------------------------
def render_report_with_inline_visuals(reply, charts, tables):
    chart_map = {
        normalize_title(c.get("title", "")): c
        for c in charts
        if isinstance(c, dict) and c.get("title")
    }

    table_map = {
        normalize_title(t.get("title", "")): t
        for t in tables
        if isinstance(t, dict) and t.get("title")
    }

    used_charts = set()
    used_tables = set()

    token_pattern = r"(\[\[CHART:(.*?)\]\]|\[\[TABLE:(.*?)\]\])"
    parts = re.split(token_pattern, reply, flags=re.DOTALL)

    buffer = ""

    def flush_buffer():
        nonlocal buffer

        if buffer.strip():
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(buffer.strip())
            st.markdown('</div>', unsafe_allow_html=True)
            buffer = ""

    for part in parts:
        if not part or not str(part).strip():
            continue

        part = str(part).strip()

        if part.startswith("[[CHART:"):
            flush_buffer()

            title = part.replace("[[CHART:", "").replace("]]", "").strip()
            key = normalize_title(title)
            chart = chart_map.get(key)

            if chart:
                render_dynamic_chart(chart)
                used_charts.add(key)
            else:
                st.warning(f"Chart placeholder found but chart data missing: {title}")

        elif part.startswith("[[TABLE:"):
            flush_buffer()

            title = part.replace("[[TABLE:", "").replace("]]", "").strip()
            key = normalize_title(title)
            table = table_map.get(key)

            if table:
                render_dynamic_table(table)
                used_tables.add(key)
            else:
                st.warning(f"Table placeholder found but table data missing: {title}")

        elif part.startswith("CHART:") or part.startswith("TABLE:"):
            continue

        elif normalize_title(part) in chart_map or normalize_title(part) in table_map:
            continue

        else:
            buffer += "\n\n" + part

    flush_buffer()

    if charts and not used_charts:
        st.warning(
            "Charts were returned, but no matching [[CHART:...]] placeholders were found in Customer_Story."
        )

    if tables and not used_tables:
        st.warning(
            "Tables were returned, but no matching [[TABLE:...]] placeholders were found in Customer_Story."
        )

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

# -----------------------------
# PAGE TITLE
# -----------------------------
st.markdown("## 💬 **Next Best Action for Commercial Pharma**")
st.write("---")

# -----------------------------
# OVERVIEW
# -----------------------------
st.markdown(
    """
### 📘 Overview

This application offers the **Next Best Actions (NBAs)** for commercial, sales, market access, and medical pharmaceutical field teams. It focuses on the diabetes market in the Kingdom of Saudi Arabia(KSA). Analysis of client internal sales, CRM call notes, medical data, together with external in-market policy, healthcare data, recent medical publications, and future health conferences are governed by client specific business rules that control the output.

### 🎯 Data Scope
This demo only reflects **Saudi Arabia diabetes market data**, including:
- Sales data  
- HCP profiles  
- Call notes  
- Market summaries  
- Scientific publication data

### 💡 Sample Questions
- *Sales Representative:*  
  Analyse call notes data and generate NBA for high-potential prescribers of **Empagliflozin** and explain why?.

- *Market Access Specialist:*  
  Give me the Market Access Strategy for five hospitals with greatest number of diabetes patients. Consider reimbursement status and the market overview?

- *Medical Science Liaison (MSL):*  
  Analyze the call notes data for any MSL follow-up requests or complex clinical questions flagged by the Sales Team, or for any KOLs requesting specific data. Generate the 'Next Best Action' (NBA) for each assigned MSL, prioritizing engagements that address complex topics beyond the sales representative’s scope.
"""
)

st.write("---")


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

        render_report_with_inline_visuals(reply, charts, tables)

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
