import os
import pandas as pd
from sqlalchemy import create_engine
from prophet import Prophet
import plotly.graph_objects as go
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv



st.set_page_config(layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv(ENV_PATH)

DB_PATH        = os.path.normpath(os.path.join(BASE_DIR, "..", "Backend", "parking.db"))
MANAGER_EMAIL  = os.getenv("MANAGER_EMAIL")
SENDER_EMAIL   = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
DRY_RUN        = os.getenv("DRY_RUN", "true").lower() == "true"


engine = create_engine(f"sqlite:///{DB_PATH}")
st.title("IoT Parking - Predictions")

parkings = pd.read_sql_query("SELECT parking_id, parking_name, total_slot, disabled_slot FROM parkings", con=engine)

parking_options = {
    row['parking_name']: {
        "id": row['parking_id'],
        "total_slot": row['total_slot'],
        "disabled_slot": row['disabled_slot']
    }
    for _, row in parkings.iterrows()
}

selected_name = st.selectbox("Select parking", list(parking_options.keys()))
parking_id     = parking_options[selected_name]["id"]
TOTAL_SLOTS    = parking_options[selected_name]["total_slot"]
DISABLED_SLOTS = parking_options[selected_name]["disabled_slot"]


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



def send_weekly_report(forecast_n, forecast_h, dataset_n, dataset_h, parking_name):
    
    next_7_days = forecast_n[forecast_n['ds'] >= pd.Timestamp.now()].head(168)
    next_7_days_h = forecast_h[forecast_h['ds'] >= pd.Timestamp.now()].head(168)
    
    past_7_days = dataset_n[dataset_n['ds'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
    past_7_days_h = dataset_h[dataset_h['ds'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]

    avg_past = round(past_7_days['y'].mean(), 1)
    max_past = int(past_7_days['y'].max())
    peak_hour = past_7_days.loc[past_7_days['y'].idxmax(), 'ds'].strftime('%A %H:%M')
    
    avg_past_h = round(past_7_days_h['y'].mean(), 1)
    max_past_h = int(past_7_days_h['y'].max())

    daily_forecast = next_7_days.groupby(next_7_days['ds'].dt.date)['yhat'].mean().round(1)
    daily_forecast_h = next_7_days_h.groupby(next_7_days_h['ds'].dt.date)['yhat'].mean().round(1)

    def occupancy_color(value, total):
        pct = value / total * 100
        if pct >= 85:
            return "#e74c3c"
        elif pct >= 60:
            return "#f39c12"
        else:
            return "#27ae60"

    forecast_rows = ""
    for date, val in daily_forecast.items():
        color = occupancy_color(val, TOTAL_SLOTS)
        forecast_rows += f"""
        <tr>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">{pd.Timestamp(date).strftime('%A %d %b')}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee; color: {color}; font-weight: bold;">{val}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee; color: {color};">{round(val / TOTAL_SLOTS * 100, 1)}%</td>
        </tr>
        """

    forecast_rows_h = ""
    for date, val in daily_forecast_h.items():
        color = occupancy_color(val, DISABLED_SLOTS)
        forecast_rows_h += f"""
        <tr>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">{pd.Timestamp(date).strftime('%A %d %b')}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee; color: {color}; font-weight: bold;">{val}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #eee; color: {color};">{round(val / DISABLED_SLOTS * 100, 1)}%</td>
        </tr>
        """

    html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px;">
            Weekly Report — {parking_name}
        </h2>
        <p style="color: #666;">Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>

        <h3 style="color: #2c3e50;">Last 7 days — Standard slots</h3>
        <table style="width:100%; border-collapse: collapse; background: #f9f9f9;">
            <tr style="background: #3498db; color: white;">
                <td style="padding: 8px 12px;">Metric</td>
                <td style="padding: 8px 12px;">Value</td>
            </tr>
            <tr><td style="padding: 8px 12px; border-bottom: 1px solid #eee;">Average occupancy</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">{avg_past} slots</td></tr>
            <tr><td style="padding: 8px 12px; border-bottom: 1px solid #eee;">Peak occupancy</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">{max_past} slots</td></tr>
            <tr><td style="padding: 8px 12px;">Busiest moment</td>
                <td style="padding: 8px 12px;">{peak_hour}</td></tr>
        </table>

        <h3 style="color: #2c3e50; margin-top: 24px;">Last 7 days — Disabled slots</h3>
        <table style="width:100%; border-collapse: collapse; background: #f9f9f9;">
            <tr style="background: #3498db; color: white;">
                <td style="padding: 8px 12px;">Metric</td>
                <td style="padding: 8px 12px;">Value</td>
            </tr>
            <tr><td style="padding: 8px 12px; border-bottom: 1px solid #eee;">Average occupancy</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">{avg_past_h} slots</td></tr>
            <tr><td style="padding: 8px 12px;">Peak occupancy</td>
                <td style="padding: 8px 12px;">{max_past_h} slots</td></tr>
        </table>

        <h3 style="color: #2c3e50; margin-top: 24px;">Next 7 days forecast — Standard slots</h3>
        <table style="width:100%; border-collapse: collapse; background: #f9f9f9;">
            <tr style="background: #3498db; color: white;">
                <td style="padding: 8px 12px;">Day</td>
                <td style="padding: 8px 12px;">Avg predicted</td>
                <td style="padding: 8px 12px;">Occupancy %</td>
            </tr>
            {forecast_rows}
        </table>

        <h3 style="color: #2c3e50; margin-top: 24px;">Next 7 days forecast — Disabled slots</h3>
        <table style="width:100%; border-collapse: collapse; background: #f9f9f9;">
            <tr style="background: #3498db; color: white;">
                <td style="padding: 8px 12px;">Day</td>
                <td style="padding: 8px 12px;">Avg predicted</td>
                <td style="padding: 8px 12px;">Occupancy %</td>
            </tr>
            {forecast_rows_h}
        </table>

        <p style="margin-top: 32px; font-size: 12px; color: #999;">
            IoT Parking System — automated weekly report
        </p>
    </body></html>
    """

    msg = MIMEMultipart('alternative')
    msg['From']    = SENDER_EMAIL
    msg['To']      = MANAGER_EMAIL
    msg['Subject'] = f"[IoT Parking] Weekly Report — {parking_name} — {pd.Timestamp.now().strftime('%d %b %Y')}"
    msg.attach(MIMEText(html, 'html'))

    if DRY_RUN:
        st.info("[DRY RUN] Report would be sent — check the preview below")
        st.components.v1.html(html, height=800, scrolling=True)
        return

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, MANAGER_EMAIL, msg.as_string())
        st.success(f"Weekly report sent to {MANAGER_EMAIL}")
    except Exception as e:
        st.error(f"Failed to send report: {e}")



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

        st.session_state['forecast_n'] = forecast_n
        st.session_state['forecast_h'] = forecast_h
        st.session_state['dataset_n']  = dataset_n
        st.session_state['dataset_h']  = dataset_h

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


if st.button("Send weekly report"):
    if 'forecast_n' not in st.session_state:
        st.warning("Generate predictions first.")
    else:
        send_weekly_report(
            st.session_state['forecast_n'],
            st.session_state['forecast_h'],
            st.session_state['dataset_n'],
            st.session_state['dataset_h'],
            selected_name
        )