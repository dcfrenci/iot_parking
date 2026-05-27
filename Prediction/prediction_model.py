import os
import pandas as pd
from sqlalchemy import create_engine
from prophet import Prophet
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "Backend", "parking.db"))

engine = create_engine(f"sqlite:///{DB_PATH}")
parkings = pd.read_sql_query("SELECT parking_id, parking_name FROM parkings", con=engine)

st.title("IoT Parking - Predictions")

parking_options = dict(zip(parkings['parking_name'], parkings['parking_id']))
selected_name = st.selectbox("Select parking", list(parking_options.keys()))
parking_id = parking_options[selected_name]

df = pd.read_sql_query(f"""SELECT timestamp, occupied_slots, disabled_occupied_slots FROM parking_history WHERE parking_id = {parking_id}""",
                       con=engine)
df['timestamp'] = pd.to_datetime(df['timestamp'])



def build_forecast_chart(forecast, historical, title, color):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper'], forecast['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor=f'rgba({color}, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence band'
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        line=dict(color=f'rgb({color})', width=2),
        name='Forecast'
    ))

    fig.add_trace(go.Scatter(
        x=historical['ds'],
        y=historical['y'],
        mode='markers',
        marker=dict(color='black', size=3, opacity=0.4),
        name='Historical data'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Occupied slots",
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=7,  label="1w", step="day",  stepmode="backward"),
                    dict(count=14, label="2w", step="day",  stepmode="backward"),
                    dict(count=1,  label="1m", step="month",stepmode="backward"),
                    dict(step="all", label="All")
                ]
            ),
            rangeslider=dict(visible=True),
            range=[
                forecast['ds'].max() - pd.Timedelta(days=14),
                forecast['ds'].max()
            ]
        )
    )

    return fig



def build_components_chart(forecast, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['trend'],
        name='Trend', line=dict(width=2)
    ))

    fig.update_layout(title=f"{title} - Trend", xaxis_title="Date", yaxis_title="Value")
    return fig



if st.button("Generate predictions"):
    with st.spinner("Training model..."):
        dataset_n = df[["timestamp", "occupied_slots"]].rename(
            columns={"timestamp": "ds", "occupied_slots": "y"})
        dataset_n = dataset_n.drop_duplicates('ds').sort_values('ds').reset_index(drop=True)

        dataset_h = df[["timestamp", "disabled_occupied_slots"]].rename(
            columns={"timestamp": "ds", "disabled_occupied_slots": "y"})
        dataset_h = dataset_h.drop_duplicates('ds').sort_values('ds').reset_index(drop=True)

        model_n = Prophet(yearly_seasonality=False, weekly_seasonality=True,
                         daily_seasonality=True, seasonality_mode='multiplicative',
                         interval_width=0.80)
        model_n.fit(dataset_n)
        future_n = model_n.make_future_dataframe(periods=168, freq='h')
        forecast_n = model_n.predict(future_n)

        model_h = Prophet(yearly_seasonality=False, weekly_seasonality=True,
                         daily_seasonality=True, seasonality_mode='multiplicative',
                         interval_width=0.80)
        model_h.fit(dataset_h)
        future_h = model_h.make_future_dataframe(periods=168, freq='h')
        forecast_h = model_h.predict(future_h)

    st.subheader("Standard slots")
    fig1 = build_forecast_chart(forecast_n, dataset_n, "Standard slots forecast", "55, 138, 221")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = build_components_chart(forecast_n, "Standard slots")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Disabled slots")
    fig3 = build_forecast_chart(forecast_h, dataset_h, "Disabled slots forecast", "99, 180, 99")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = build_components_chart(forecast_h, "Disabled slots")
    st.plotly_chart(fig4, use_container_width=True)