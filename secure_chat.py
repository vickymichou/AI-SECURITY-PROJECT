import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

st.set_page_config(page_title="AI Security Monitoring Dashboard", layout="wide")
st.title("🛡️ AI Security Monitoring Dashboard")

LOG_FILE = "security_audit.jsonl"


def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    data = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                data.append(record)
            except Exception:
                continue

    df = pd.DataFrame(data)

    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()

if not df.empty:
    df["risk_score"] = df["risk_score"].clip(lower=0)

if not df.empty:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Request Status Distribution")
        fig_status = px.pie(
            df,
            names="status",
            color="status",
            color_discrete_map={
                "ALLOWED": "green",
                "BLOCKED": "red",
                "ALERT": "orange",
                "API_ERROR": "purple",
                "REQUEST_FAILED": "gray"
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with c2:
        st.subheader("Risk Score Over Time")
        fig_risk = px.line(df, x="timestamp", y="risk_score", markers=True)
        st.plotly_chart(fig_risk, use_container_width=True)

    st.subheader("Recent Security Events")
    st.dataframe(df.sort_values("timestamp", ascending=False).head(10), use_container_width=True)

    st.subheader("Summary")
    st.write(f"Total Events: {len(df)}")
    st.write(f"Average Risk Score: {df['risk_score'].mean():.2f}")

else:
    st.info("Περιμένω δεδομένα από το chatbot...")