import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Administrative Building Solar Project Analytics",
    layout="wide",
    page_icon="⚡",
)

# Professional Custom Styling & Color-Accented Cards
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title {
        color: #8b949e;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)

st.title(
    "⚡ Solar Energy Management & Analytics Hub for Administrative Building"
)
st.markdown(
    "**Call Center Administrative Building Microgrid Project** | Advanced"
    " Professional Dashboard & Hourly Analytics"
)
st.markdown("---")


# Load Data directly from the Excel file
@st.cache_data
def load_excel_data():
  try:
    filepath = "Call Center Daily Load.xlsx"
    df_solar = pd.read_excel(filepath, sheet_name="solar gen ", skiprows=2)
    df_solar.columns = df_solar.iloc[0]
    df_solar_clean = df_solar.iloc[1:25].copy()
    return df_solar_clean
  except Exception as e:
    hours = [f"{h:02d}:00 - {(h+1)%24:02d}:00" for h in range(24)]
    base_load = [
        144.59,
        144.59,
        144.59,
        144.59,
        144.59,
        186.35,
        295.19,
        541.25,
        739.7,
        820.22,
        820.22,
        802.27,
        784.32,
        802.27,
        820.22,
        820.22,
        702.29,
        502.35,
        356.25,
        292.18,
        228.11,
        186.35,
        164.04,
        144.59,
    ]
    solar = [
        0,
        0,
        0,
        0,
        0,
        0,
        35,
        105,
        210,
        280,
        332.5,
        350,
        350,
        332.5,
        280,
        210,
        105,
        35,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    net = [max(50, b - s) for b, s in zip(base_load, solar)]
    return pd.DataFrame({
        "Hour": hours,
        "Building Load (kW)": base_load,
        "Solar Generation (kW)": solar,
        "Net Load / Grid Import (kW)": net,
    })


df_raw = load_excel_data()

# Clean and convert numeric columns
df_raw["Building Load (kW)"] = pd.to_numeric(
    df_raw["Building Load (kW)"], errors="coerce"
)
base_solar_excel = pd.to_numeric(
    df_raw["Solar Generation (kW)"], errors="coerce"
).values

# Sidebar Controls with Sliders
with st.sidebar:
  st.header("🎛️ Control Panel")

  with st.expander("🛠️ Simulation & PV Parameters", expanded=True):
    pv_capacity = st.slider(
        "PV System Capacity (kW)",
        min_value=100.0,
        max_value=600.0,
        value=350.0,
        step=25.0,
    )
    peak_limit = st.slider(
        "Grid Peak Power Limit (kW)",
        min_value=500.0,
        max_value=900.0,
        value=650.0,
        step=25.0,
    )
    tariff = st.slider(
        "Electricity Tariff (EGP/kWh)",
        min_value=1.0,
        max_value=10.0,
        value=3.5,
        step=0.25,
    )
    system_cost = (
        st.slider(
            "PV System Cost (Million EGP)",
            min_value=1.0,
            max_value=10.0,
            value=5.0,
            step=0.5,
        )
        * 1000000
    )

  with st.expander("📊 View Options", expanded=False):
    show_table = st.checkbox("Show Raw Data Table at Bottom", value=True)

# Scale solar generation based on user PV capacity slider relative to base 350kW
solar_gen = base_solar_excel * (pv_capacity / 350.0)

# Hourly Calculations
hours_list = [f"{h:02d}:00" for h in range(24)]
building_load = df_raw["Building Load (kW)"].values
net_load_before = np.maximum(0, building_load - solar_gen)
net_load_after = np.minimum(
    np.maximum(50, building_load - solar_gen), peak_limit
)

cost_no_solar = building_load * tariff
cost_with_ems = net_load_after * tariff
hourly_savings = cost_no_solar - cost_with_ems
cumulative_savings = np.cumsum(hourly_savings)

# KPI Metrics Calculations
total_daily_energy = building_load.sum()
total_solar_energy = solar_gen.sum()
solar_share_pct = (
    (total_solar_energy / total_daily_energy) * 100
    if total_daily_energy > 0
    else 0
)

total_cost_no_solar = cost_no_solar.sum()
total_cost_with_ems = cost_with_ems.sum()
total_daily_savings = total_cost_no_solar - total_cost_with_ems
total_savings_pct = (
    (total_daily_savings / total_cost_no_solar) * 100
    if total_cost_no_solar > 0
    else 0
)

annual_saving = total_daily_savings * 365
payback_period = system_cost / annual_saving if annual_saving > 0 else 0

original_peak = building_load.max()
new_peak = net_load_after.max()


# Custom HTML Card Render Function with Color Accents
def render_card(title, value, accent_color="#636efa"):
  st.markdown(
      f"""
        <div class="metric-card" style="border-left: 5px solid {accent_color};">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )


# Top KPI Summary Cards (Row 1)
col1, col2, col3, col4 = st.columns(4)
with col1:
  render_card(
      "Daily Consumption", f"{total_daily_energy:,.1f} kWh", "#636efa"
  )
with col2:
  render_card(
      "Solar Energy Used",
      f"{total_solar_energy:,.0f} kWh ({solar_share_pct:.1f}%)",
      "#ffa15c",
  )
with col3:
  render_card(
      "Cost: No Solar", f"{int(total_cost_no_solar):,} EGP/day", "#ef553b"
  )
with col4:
  render_card(
      "Cost: Solar + EMS", f"{int(total_cost_with_ems):,} EGP/day", "#00cc96"
  )

# Top KPI Summary Cards (Row 2)
col5, col6, col7, col8 = st.columns(4)
with col5:
  render_card(
      "Total Saving",
      f"{total_savings_pct:.1f}% ({int(total_daily_savings):,} EGP)",
      "#00cc96",
  )
with col6:
  render_card(
      "Peak Grid Demand", f"{original_peak:.1f} -> {new_peak:.1f} kW", "#ab63fa"
  )
with col7:
  render_card(
      "Annual Saving",
      f"{int(annual_saving / 1000):,} k EGP / year",
      "#00cc96",
  )
with col8:
  render_card("Payback Period", f"{payback_period:.1f} years", "#19d3f3")

st.markdown("---")

df_display = pd.DataFrame({
    "Hour": hours_list,
    "Building Load (kW)": np.round(building_load, 2),
    "Solar Gen (kW)": np.round(solar_gen, 2),
    "Net Load Before EMS (kW)": np.round(net_load_before, 2),
    "Net Load After EMS (kW)": np.round(net_load_after, 2),
    "Cost Before (EGP)": np.round(cost_no_solar, 2),
    "Cost After (EGP)": np.round(cost_with_ems, 2),
    "Savings (EGP)": np.round(hourly_savings, 2),
    "Cumulative Savings (EGP)": np.round(cumulative_savings, 2),
})

# Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Advanced Curves", "Financial Analysis"])

with tab1:
  st.subheader("📈 24-Hour Power Profile: Load, Solar and Grid Import")
  fig1 = go.Figure()
  fig1.add_trace(
      go.Scatter(
          x=df_display["Hour"],
          y=df_display["Building Load (kW)"],
          mode="lines+markers",
          name="Building Load",
          line=dict(color="#636efa", width=3),
      )
  )
  fig1.add_trace(
      go.Scatter(
          x=df_display["Hour"],
          y=df_display["Solar Gen (kW)"],
          mode="lines+markers",
          name="Solar Generation",
          line=dict(color="#ffa15c", width=3),
          fill="tozeroy",
      )
  )
  fig1.add_trace(
      go.Scatter(
          x=df_display["Hour"],
          y=df_display["Net Load Before EMS (kW)"],
          mode="lines+markers",
          name="Net Load (Before EMS)",
          line=dict(color="#ef553b", width=3),
      )
  )
  fig1.add_trace(
      go.Scatter(
          x=df_display["Hour"],
          y=df_display["Net Load After EMS (kW)"],
          mode="lines+markers",
          name="Net Load (After EMS)",
          line=dict(color="#00cc96", width=3),
      )
  )
  fig1.update_layout(
      xaxis_title="Hour of day",
      yaxis_title="Power (kW)",
      template="plotly_dark",
      hovermode="x unified",
  )
  st.plotly_chart(fig1, use_container_width=True)

  c_ov1, c_ov2 = st.columns(2)
  with c_ov1:
    st.subheader("🍩 Daily Energy Share Breakdown")
    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=["Solar Energy", "Grid Energy"],
                values=[
                    total_solar_energy,
                    max(0, total_daily_energy - total_solar_energy),
                ],
                hole=0.5,
                marker=dict(colors=["#ffa15c", "#00cc96"]),
            )
        ]
    )
    fig_donut.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_donut, use_container_width=True)

  with c_ov2:
    st.subheader("📊 Hourly Financial Savings")
    fig_hbar = px.bar(
        df_display,
        x="Savings (EGP)",
        y="Hour",
        orientation="h",
        color="Savings (EGP)",
        color_continuous_scale="Greens",
    )
    fig_hbar.update_layout(
        template="plotly_dark",
        margin=dict(t=0, b=0, l=0, r=0),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_hbar, use_container_width=True)

with tab2:
  st.subheader("📊 Advanced Power & Cumulative Curves")
  c_l1, c_r1 = st.columns(2)

  with c_l1:
    fig_smooth = go.Figure()
    fig_smooth.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=df_display["Building Load (kW)"],
            name="Building Load",
            line=dict(color="#636efa", width=2),
        )
    )
    fig_smooth.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=df_display["Net Load Before EMS (kW)"],
            name="Net Load (Before EMS)",
            line=dict(color="#ef553b", width=2),
            fill="tonexty",
        )
    )
    fig_smooth.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=df_display["Net Load After EMS (kW)"],
            name="Net Load (After EMS)",
            line=dict(color="#00cc96", width=2),
            fill="tonexty",
        )
    )
    fig_smooth.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=df_display["Solar Gen (kW)"],
            name="Solar Generation",
            line=dict(color="#ffa15c", width=2),
            fill="tozeroy",
        )
    )
    fig_smooth.update_layout(
        title="Hourly Power - Smooth Area",
        template="plotly_dark",
        margin=dict(t=30, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_smooth, use_container_width=True)

  with c_r1:
    cum_building = np.cumsum(building_load)
    cum_net_before = np.cumsum(net_load_before)
    cum_net_after = np.cumsum(net_load_after)

    fig_cum = go.Figure()
    fig_cum.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=cum_building,
            name="Building Load",
            line=dict(color="#636efa", width=2),
        )
    )
    fig_cum.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=cum_net_before,
            name="Grid (Before EMS)",
            line=dict(color="#ef553b", width=2),
        )
    )
    fig_cum.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=cum_net_after,
            name="Grid (After EMS)",
            line=dict(color="#00cc96", width=2),
        )
    )
    fig_cum.update_layout(
        title="Cumulative Energy Curve (kWh)",
        template="plotly_dark",
        margin=dict(t=30, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_cum, use_container_width=True)

  st.markdown("---")
  sorted_load = np.sort(building_load)[::-1]
  sorted_net_before = np.sort(net_load_before)[::-1]
  sorted_net_after = np.sort(net_load_after)[::-1]
  rank_hours = np.arange(1, 25)

  fig_duration = go.Figure()
  fig_duration.add_trace(
      go.Scatter(
          x=rank_hours,
          y=sorted_load,
          mode="lines",
          name="Building Load",
          line=dict(color="#636efa", width=2, shape="hv"),
      )
  )
  fig_duration.add_trace(
      go.Scatter(
          x=rank_hours,
          y=sorted_net_before,
          mode="lines",
          name="Grid (Before EMS)",
          line=dict(color="#ef553b", width=2, shape="hv"),
      )
  )
  fig_duration.add_trace(
      go.Scatter(
          x=rank_hours,
          y=sorted_net_after,
          mode="lines",
          name="Grid (After EMS)",
          line=dict(color="#00cc96", width=2, shape="hv"),
      )
  )
  fig_duration.update_layout(
      title="Load Duration Curve (Ranked from Highest Load)",
      xaxis_title="Hours per day (ranked)",
      yaxis_title="Power (kW)",
      template="plotly_dark",
  )
  st.plotly_chart(fig_duration, use_container_width=True)

with tab3:
  st.subheader("💰 Financial Analysis & Grid Dependency")
  c_l2, c_r2 = st.columns(2)

  with c_l2:
    cum_cost_no = np.cumsum(cost_no_solar)
    cum_cost_with = np.cumsum(cost_with_ems)

    fig_cost_cum = go.Figure()
    fig_cost_cum.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=cum_cost_no,
            name="No Solar",
            line=dict(color="#ef553b", width=3),
        )
    )
    fig_cost_cum.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=cum_cost_with,
            name="Solar + EMS",
            line=dict(color="#00cc96", width=3),
        )
    )
    fig_cost_cum.update_layout(
        title="Cumulative Daily Cost (EGP)",
        template="plotly_dark",
        margin=dict(t=30, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_cost_cum, use_container_width=True)

  with c_r2:
    solar_share = (
        (solar_gen / building_load) * 100 if building_load.any() else 0
    )
    grid_dep = 100 - solar_share

    fig_dep = go.Figure()
    fig_dep.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=solar_share,
            mode="lines+markers",
            name="Solar Share (%)",
            line=dict(color="#ffa15c", width=2),
        )
    )
    fig_dep.add_trace(
        go.Scatter(
            x=df_display["Hour"],
            y=grid_dep,
            mode="lines+markers",
            name="Grid Dependency (%)",
            line=dict(color="#ef553b", width=2),
        )
    )
    fig_dep.update_layout(
        title="Solar Share vs Grid Dependency (%)",
        template="plotly_dark",
        margin=dict(t=30, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_dep, use_container_width=True)

# -------------------------------------------------------------------------
# Raw Data Table at the Bottom
# -------------------------------------------------------------------------
if show_table:
  st.markdown("---")
  st.subheader("📋 Detailed Hourly Operational & Financial Data Table")
  st.dataframe(df_display, use_container_width=True)

st.markdown("---")
st.caption(
    "Administrative Building Solar Energy Hub | Professional Graduation Project"
)