import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="AI Security Dashboard", layout="wide")
st.title("🛡️ AI Security Monitoring Dashboard")

def load_data():
    if not os.path.exists("security_audit.log"):
        return pd.DataFrame()
    data = []
    with open("security_audit.log", "r", encoding="utf-8") as f:
        for line in f:
            try:
                parts = line.split(" | ")
                timestamp = parts[0].strip("[]")
                status = parts[1]
                risk = float(parts[2].split(": ")[1])
                data.append({"Timestamp": timestamp, "Status": status, "Risk Score": risk})
            except: continue
    return pd.DataFrame(data)

df = load_data()
if not df.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(df, names='Status', color='Status', color_discrete_map={'ALLOWED':'green', 'BLOCKED':'red'}))
    with c2:
        st.plotly_chart(px.line(df, x='Timestamp', y='Risk Score'))
    st.table(df.tail(5))
else:
    st.info("Περιμένω δεδομένα από το chatbot...")