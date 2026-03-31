import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="AI Security Dashboard", layout="wide")
st.title("🛡️ AI Security Audit Dashboard")

def load_data():
    if not os.path.exists("security_audit.log"):
        return pd.DataFrame()

    data = []
    with open("security_audit.log", "r", encoding="utf-8") as f:
        for line in f:
            try:
                parts = line.split(" | ")
                status = parts[1]
                data.append({"Status": status})
            except:
                continue

    return pd.DataFrame(data)

df = load_data()

if not df.empty:
    st.subheader("Στατιστικά Ασφαλείας")

    fig = px.pie(
        df,
        names='Status',
        color='Status',
        color_discrete_map={
            'ALLOWED': 'green',
            'BLOCKED': 'red',
            'ALERT': 'orange'
        }
    )

    st.plotly_chart(fig)

else:
    st.warning("Δεν βρέθηκαν δεδομένα στο log αρχείο.")