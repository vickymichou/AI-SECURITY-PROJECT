import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

st.set_page_config(page_title="AI Security Monitoring Dashboard", layout="wide")
st.title("🛡️ AI Security Monitoring Dashboard")

DB_FILE = "security_events.db"


def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()

    conn = sqlite3.connect(DB_FILE)

    query = """
        SELECT id, timestamp, status, risk_score, prompt, response, model, source
        FROM security_events
        ORDER BY timestamp ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["risk_score"] = df["risk_score"].clip(lower=0)

    return df


df = load_data()

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
    st.dataframe(
        df.sort_values("timestamp", ascending=False).head(10),
        use_container_width=True
    )

    st.subheader("Summary")
    st.write(f"Total Events: {len(df)}")
    st.write(f"Average Risk Score: {df['risk_score'].mean():.2f}")
    st.write(f"Unique Status Types: {df['status'].nunique()}")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="security_events.csv",
        mime="text/csv"
    )

else:
    st.info("Περιμένω δεδομένα από τη βάση SQLite...")