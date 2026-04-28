import streamlit as st
import pandas as pd

# Try importing Plotly
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# -----------------------------
# SAMPLE DATA (Replace with yours)
# -----------------------------
data = {
    "Region": ["London", "Manchester", "Birmingham", "Leeds"],
    "lat": [51.5074, 53.4808, 52.4862, 53.8008],
    "lon": [-0.1278, -2.2426, -1.8904, -1.5491],
    "Score": [85, 70, 60, 75]
}

df_region = pd.DataFrame(data)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Region Dashboard", layout="wide")

st.title("📊 Region Performance Dashboard")

# -----------------------------
# VIEW TOGGLE (Chart vs Table)
# -----------------------------
view_option = st.radio(
    "Select View",
    ["Chart View", "Table View"],
    horizontal=True
)

# -----------------------------
# PLACEHOLDER (controls position)
# -----------------------------
output_container = st.container()

# -----------------------------
# RENDER OUTPUT IN PLACE
# -----------------------------
with output_container:

    if view_option == "Chart View":

        if PLOTLY_AVAILABLE and df_region is not None and not df_region.empty:

            col1, col2 = st.columns(2)

            # -----------------------------
            # MAP CHART
            # -----------------------------
            with col1:
                st.subheader("📍 Region Map")

                fig_map = px.scatter_mapbox(
                    df_region,
                    lat="lat",
                    lon="lon",
                    size="Score",
                    color="Score",
                    hover_name="Region",
                    zoom=4,
                    mapbox_style="open-street-map",
                    size_max=20
                )

                fig_map.update_layout(
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=400
                )

                st.plotly_chart(fig_map, use_container_width=True)

            # -----------------------------
            # BAR CHART
            # -----------------------------
            with col2:
                st.subheader("📊 Score by Region")

                fig_bar = px.bar(
                    df_region,
                    x="Region",
                    y="Score",
                    color="Score",
                    text="Score"
                )

                fig_bar.update_layout(height=400)

                st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("Plotly not installed or no data available")

    else:
        # Table view (only if user selects it)
        st.subheader("📄 Data Table")
        st.dataframe(df_region, use_container_width=True)
