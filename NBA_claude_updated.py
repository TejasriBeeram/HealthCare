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

.chart-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 28px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.kpi-card {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #1d4ed8;
}

.kpi-label {
    font-size: 14px;
    color: #334155;
}

h1, h2, h3 {
    color: #0f172a;
}

@media print {
    .stButton, .stTextArea, .stRadio, .stForm {
        display: none !important;
    }

    .chart-card, .report-card {
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
# DATA
# -----------------------------
def hospital_df():
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
            "King Abdulaziz University Hospital",
        ],
        "Prescription Volume": [
            452.04, 425.16, 400.84, 387.26, 378.82, 332.16,
            303.74, 279.02, 253.77, 248.29, 232.91, 184.87
        ],
    })

def market_df():
    return pd.DataFrame({
        "Year": [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2045],
        "Market Size USD Bn": [2.0, 2.18, 2.38, 2.59, 2.82, 3.08, 3.4, None],
        "Patients Mn": [4.27, 4.45, 4.65, 4.9, 5.15, 5.35, 5.6, 7.5],
    })

def drug_share_df():
    return pd.DataFrame({
        "Class": ["Insulins", "Oral Anti-Diabetics", "Non-Insulin Injectables"],
        "Share": [51, 27, 22],
    })

def hcp_df():
    return pd.DataFrame({
        "Name": [
            "Al-Muhanna", "Alghamdi K.S.", "Ba Hamid", "Al-Quorain A.",
            "Al-Rubeaan", "Sulaiman R.", "Al-Quorain Abd", "Al-Sultan",
            "Al-Ghamdi K.", "Alshareef M.", "Al-Ali A.", "Al-Somali",
            "Al-Habib", "Aljohani N."
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
        ],
        "Score": [9.2, 8.1, 7.6, 7.1, 7.1, 7.9, 7.0, 6.8, 5.9, 5.8, 5.7, 5.6, 4.9, 4.8],
    })

def category_df():
    return pd.DataFrame({
        "Category": [
            "HCP / Researcher",
            "HCP Clinician",
            "KOL Professor",
            "HCP Consultant",
            "KOL Speaker",
            "Collaborator"
        ],
        "Count": [16, 6, 3, 3, 3, 2],
    })

def cvot_df():
    return pd.DataFrame({
        "Trial": ["SUSTAIN-6", "PIONEER-6", "LEADER", "REWIND", "EXSCEL", "ELIXA"],
        "Drug": [
            "Semaglutide inj",
            "Oral Semaglutide",
            "Liraglutide",
            "Dulaglutide",
            "Exenatide weekly",
            "Lixisenatide"
        ],
        "HR": [0.74, 0.79, 0.87, 0.88, 0.91, 1.02],
        "Low": [0.58, 0.57, 0.78, 0.79, 0.83, 0.89],
        "High": [0.95, 1.11, 0.97, 0.99, 1.00, 1.17],
    })

def function_df():
    return pd.DataFrame({
        "Function": ["MSL", "Sales Rep", "Market Access", "Marketing"],
        "Visits": [22, 21, 18, 18],
    })

def evidence_df():
    return pd.DataFrame({
        "Trial": ["SUSTAIN-6", "SELECT", "SURPASS-2", "LEADER", "EMPA-KIDNEY", "DAPA-HF", "PIONEER-6"],
        "Impact Rating": [5, 4, 4, 4, 5, 4, 4],
        "Relevance": [
            "Direct class support",
            "Expands patient pool",
            "Competitive threat",
            "Class support",
            "Complementary CKD",
            "Combination therapy",
            "Oral option"
        ],
    })

def journey_df():
    return pd.DataFrame({
        "Stakeholder": ["Dr. Al-Ahmadi", "Dr. Al-Shehri", "NUPCO", "Dr. Mansour"],
        "Jan 2023": [1, 1, 1, 1],
        "Jul 2023": [2, 2, 2, 1],
        "Jan 2024": [3, 3, 4, 2],
        "Jul 2024": [3, 4, None, 3],
        "Jan 2025": [4, 4, None, 4],
        "Jul 2025": [5, 5, None, 5],
    })

# -----------------------------
# TEXT CLEANING
# -----------------------------
def split_report_and_remove_ascii(text: str):
    if not text:
        return ""

    cleaned = text

    cleaned = re.sub(
        r"Visual Data Analysis.*?(?=(Theoretical Integration Points|Applied Theory Sections|Key Findings|Detailed Response|Recommendations|$))",
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

    cleaned = re.sub(
        r"Downloadable Outputs.*?(?=Recommendations|$)",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    cleaned = re.sub(
        r"📊 Visual Insights.*",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    return cleaned.strip()

# -----------------------------
# CHART HELPERS
# -----------------------------
def chart_card(title):
    st.markdown(f"<div class='chart-card'><h3>{title}</h3>", unsafe_allow_html=True)

def end_card():
    st.markdown("</div>", unsafe_allow_html=True)

def render_kpis():
    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("USD 2B", "Market Size 2024"),
        ("4.27M", "Diabetes Patients 2024"),
        ("9%", "Market CAGR"),
        ("NUPCO", "Preferred Listed"),
    ]

    for col, (value, label) in zip([c1, c2, c3, c4], cards):
        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_all_visuals():
    st.markdown("## 📊 Visual Data Analysis — Power BI Style Dashboards")

    render_kpis()

    chart_card("Chart 1: Top Hospital Accounts by Prescription Volume")
    df = hospital_df().sort_values("Prescription Volume", ascending=True)
    fig = px.bar(
        df,
        x="Prescription Volume",
        y="Hospital",
        orientation="h",
        text="Prescription Volume"
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(
        template="plotly_white",
        height=560,
        margin=dict(l=20, r=40, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    chart_card("Chart 2: HCP Segmentation Matrix — Visits vs Patient Volume")
    df = hcp_df()
    fig = px.scatter(
        df,
        x="Visits",
        y="Patients",
        size="Patients",
        color="Priority",
        hover_name="Name",
        text="Name",
        size_max=55,
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        template="plotly_white",
        height=560,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    col1, col2 = st.columns(2)

    with col1:
        chart_card("Chart 3: KOL Category Distribution")
        fig = px.pie(category_df(), names="Category", values="Count", hole=0.45)
        fig.update_layout(template="plotly_white", height=430)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        chart_card("Chart 4: Drug Class Market Share")
        fig = px.pie(drug_share_df(), names="Class", values="Share", hole=0.45)
        fig.update_layout(template="plotly_white", height=430)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    chart_card("Chart 5: KSA Diabetes Market Growth Projection")
    df = market_df()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Year"],
        y=df["Market Size USD Bn"],
        name="Market Size USD Bn"
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Patients Mn"],
        name="Patients Mn",
        yaxis="y2",
        mode="lines+markers"
    ))
    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis=dict(title="Market Size USD Bn"),
        yaxis2=dict(title="Patients Mn", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    chart_card("Chart 6: GLP-1 CVOT Evidence Forest Plot")
    df = cvot_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["HR"],
        y=df["Drug"] + " — " + df["Trial"],
        mode="markers",
        marker=dict(size=13),
        error_x=dict(
            type="data",
            symmetric=False,
            array=df["High"] - df["HR"],
            arrayminus=df["HR"] - df["Low"],
        ),
        name="Hazard Ratio"
    ))
    fig.add_vline(x=1.0, line_dash="dash", annotation_text="Neutral HR = 1.0")
    fig.update_layout(
        template="plotly_white",
        height=430,
        xaxis_title="Hazard Ratio",
        yaxis_title="",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    chart_card("Chart 7: Customer Journey Progression Heatmap")
    df = journey_df().set_index("Stakeholder")
    fig = px.imshow(
        df,
        labels=dict(x="Period", y="Stakeholder", color="Maturity"),
        aspect="auto",
        text_auto=True,
    )
    fig.update_layout(
        template="plotly_white",
        height=420,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    col1, col2 = st.columns(2)

    with col1:
        chart_card("Chart 8: Cross-Functional Activity Distribution")
        fig = px.bar(function_df(), x="Function", y="Visits", text="Visits")
        fig.update_traces(textposition="outside")
        fig.update_layout(template="plotly_white", height=430)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        chart_card("Chart 9: Scientific Evidence Impact")
        df = evidence_df().sort_values("Impact Rating")
        fig = px.bar(
            df,
            x="Impact Rating",
            y="Trial",
            orientation="h",
            hover_data=["Relevance"]
        )
        fig.update_layout(template="plotly_white", height=430)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    chart_card("Chart 10: Top HCPs by Composite Priority Score")
    df = hcp_df().sort_values("Score", ascending=True)
    fig = px.bar(
        df,
        x="Score",
        y="Name",
        orientation="h",
        color="Priority",
        text="Score"
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(
        template="plotly_white",
        height=520,
        margin=dict(l=20, r=40, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    chart_card("Chart 11: HCP Priority Action Table")
    st.dataframe(
        hcp_df()[["Name", "Patients", "Visits", "Priority", "Action"]],
        use_container_width=True,
        hide_index=True
    )
    end_card()

    chart_card("Chart 12: Market Access Pathway")
    pathway = pd.DataFrame({
        "Step": [
            "SFDA Approval",
            "NUPCO Listing",
            "Etimad Tender",
            "Hospital P&T",
            "Private Sector",
            "PHC Rollout"
        ],
        "Status Score": [100, 100, 75, 90, 65, 85],
    })
    fig = px.line(pathway, x="Step", y="Status Score", markers=True)
    fig.update_traces(line=dict(width=4), marker=dict(size=12))
    fig.update_layout(
        template="plotly_white",
        height=420,
        yaxis_range=[0, 110]
    )
    st.plotly_chart(fig, use_container_width=True)
    end_card()

# -----------------------------
# API
# -----------------------------
def call_api(prompt, role):
    payload = [{"question_type": role, "prompt": prompt}]

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
        return data[0].get("Customer_Story", "No response.")

    if isinstance(data, dict):
        return data.get("Customer_Story", "No response.")

    return "Unexpected API format."

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
# FORM
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
        with st.spinner(f"Fetching response... this can take up to {API_TIMEOUT_SECONDS} seconds"):
            try:
                raw_reply = call_api(prompt, role)

            except requests.exceptions.Timeout:
                raw_reply = (
                    "The API request timed out. This means SnapLogic did not return a response "
                    f"within {API_TIMEOUT_SECONDS} seconds. Showing the visual dashboard using fallback data."
                )

            except Exception as e:
                raw_reply = f"Error while calling API: {e}"

        cleaned_reply = split_report_and_remove_ascii(raw_reply)

        st.write("---")
        st.subheader("Response")

        split_match = re.search(
            r"(Theoretical Integration Points|Applied Theory Sections|Key Findings|Detailed Response|Recommendations)",
            cleaned_reply,
            flags=re.IGNORECASE
        )

        if split_match:
            top_text = cleaned_reply[:split_match.start()].strip()
            bottom_text = cleaned_reply[split_match.start():].strip()
        else:
            top_text = cleaned_reply
            bottom_text = ""

        if top_text:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(top_text)
            st.markdown('</div>', unsafe_allow_html=True)

        render_all_visuals()

        if bottom_text:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(bottom_text)
            st.markdown('</div>', unsafe_allow_html=True)

        st.info(
            "PDF export tip: open the app in full screen, wait for all charts to load, "
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
