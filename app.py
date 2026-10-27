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

# Professional Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 12px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title(
    "⚡ Solar Energy Management & Analytics Hub for Administrative Building"
)
st.markdown(
    "**Call Center Administrative Building Microgrid Project** | Featuring 5"
    " Distinct Professional Visualizations for Graduation Defense"
)
st.markdown("---")

# Sidebar Controls with Expanders
with st.sidebar:
  st.header("🎛️ Control Panel")

  with st.expander("🛠️ Simulation Parameters", expanded=True):
    pv_capacity = st.slider("PV Capacity (kW)", 100, 500, 350, step=25)
    peak_limit = st.slider("Peak Shaving Limit (kW)", 500, 900, 650, step=25)
    tariff = st.number_input(
        "Tariff Rate (EGP/kWh)", min_value=1.0, max_value=10.0, value=3.5
    )

  with st.expander("📊 View Options", expanded=False):
    show_table = st.checkbox("Show Raw Data Table", value=True)

# Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Peak Load", "820.22 kW", "Original Max")
col2.metric("Daily Energy", "10,731.34 kWh", "Total Consumption")
col3.metric("PV Plant", f"{pv_capacity} kW", "Installed")
col4.metric(
    "Daily Savings", f"≈ {int(pv_capacity * 27):,} EGP", "Cost Reduction"
)

st.markdown("---")

# Simulation Data Generation (24 Hours)
hours = np.arange(0, 24)
base_load = 250 + 570.22 * np.exp(-((hours - 14) ** 2) / 10)
base_load[14] = 820.22  # Pinpoint peak at 2 PM

solar_gen = np.zeros(24)
for h in range(6, 19):
  solar_gen[h] = pv_capacity * np.sin(np.pi * (h - 6) / 12)

net_load = np.minimum(base_load - solar_gen, peak_limit)
net_load = np.maximum(50, net_load)

cost_before = base_load * tariff
cost_after = net_load * tariff
savings = cost_before - cost_after
cumulative_savings = np.cumsum(savings)

df = pd.DataFrame({
    'Hour': [f'{h:02d}:00' for h in hours],
    'Base Load (kW)': np.round(base_load, 2),
    'Solar Gen (kW)': np.round(solar_gen, 2),
    'Net Load (kW)': np.round(net_load, 2),
    'Cost Before (EGP)': np.round(cost_before, 2),
    'Cost After (EGP)': np.round(cost_after, 2),
    'Savings (EGP)': np.round(savings, 2),
    'Cumulative Savings (EGP)': np.round(cumulative_savings, 2),
})

# -------------------------------------------------------------------------
# Chart 1: Filled Area Chart for Power Profile
# -------------------------------------------------------------------------
st.subheader("📈 1. 24-Hour Power Profile (Filled Area Chart)")
fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=df['Hour'],
        y=df['Base Load (kW)'],
        name='Base Load',
        fill='tozeroy',
        line=dict(color='#ff4b4b', width=2),
    )
)
fig1.add_trace(
    go.Scatter(
        x=df['Hour'],
        y=df['Solar Gen (kW)'],
        name='Solar Generation',
        fill='tozeroy',
        line=dict(color='#ffa15c', width=2),
    )
)
fig1.add_trace(
    go.Scatter(
        x=df['Hour'],
        y=df['Net Load (kW)'],
        name='Net Grid Load',
        line=dict(color='#00CC96', width=4),
    )
)

fig1.update_layout(
    xaxis_title='Hour of Day',
    yaxis_title='Power (kW)',
    template='plotly_dark',
    hovermode='x unified',
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------------------
# Chart 2 & Chart 3 (Side by Side)
# -------------------------------------------------------------------------
c_left, c_right = st.columns(2)

with c_left:
  st.subheader("🍩 2. Energy Share Breakdown (Donut Chart)")
  total_solar = np.sum(solar_gen)
  total_net = np.sum(net_load)
  fig2 = go.Figure(
      data=[
          go.Pie(
              labels=['Solar Energy', 'Grid Energy'],
              values=[total_solar, total_net],
              hole=0.5,
              marker=dict(colors=['#ffa15c', '#00CC96']),
          )
      ]
  )
  fig2.update_layout(template='plotly_dark', margin=dict(t=0, b=0, l=0, r=0))
  st.plotly_chart(fig2, use_container_width=True)

with c_right:
  st.subheader("📊 3. Hourly Savings (Horizontal Bar Chart)")
  fig3 = px.bar(
      df,
      x='Savings (EGP)',
      y='Hour',
      orientation='h',
      color='Savings (EGP)',
      color_continuous_scale='Greens',
  )
  fig3.update_layout(template='plotly_dark', margin=dict(t=0, b=0, l=0, r=0))
  st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------------------
# Chart 4 & Chart 5 (Side by Side)
# -------------------------------------------------------------------------
c_left2, c_right2 = st.columns(2)

with c_left2:
  st.subheader("📉 4. Cumulative Savings (Line Chart)")
  fig4 = go.Figure()
  fig4.add_trace(
      go.Scatter(
          x=df['Hour'],
          y=df['Cumulative Savings (EGP)'],
          mode='lines+markers',
          name='Cumulative Savings',
          line=dict(color='#00cc96', width=3),
          fill='tozeroy',
      )
  )
  fig4.update_layout(
      template='plotly_dark',
      margin=dict(t=0, b=0, l=0, r=0),
      xaxis_title='Hour',
      yaxis_title='EGP',
  )
  st.plotly_chart(fig4, use_container_width=True)

with c_right2:
  st.subheader("📊 5. Hourly Cost Comparison (Grouped Bar Chart)")
  fig5 = go.Figure()
  fig5.add_trace(
      go.Bar(
          x=df['Hour'],
          y=df['Cost Before (EGP)'],
          name='Cost Without System',
          marker_color='#ef553b',
      )
  )
  fig5.add_trace(
      go.Bar(
          x=df['Hour'],
          y=df['Cost After (EGP)'],
          name='Cost With System',
          marker_color='#636efa',
      )
  )
  fig5.update_layout(
      barmode='group',
      template='plotly_dark',
      margin=dict(t=0, b=0, l=0, r=0),
      xaxis_title='Hour',
      yaxis_title='EGP/h',
  )
  st.plotly_chart(fig5, use_container_width=True)

# -------------------------------------------------------------------------
# Interactive Data Table
# -------------------------------------------------------------------------
if show_table:
  st.markdown("---")
  st.subheader("📋 Detailed Operational & Financial Data Table")
  st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption(
    'Administrative Building Solar Energy Hub | Professional Graduation Project'
)