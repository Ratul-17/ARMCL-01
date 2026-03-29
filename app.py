# (FULL COMBINED APP.PY)

"""
ARMCL-01 ERP + LOGISTICS SYSTEM
AKIJ READYMIX CONCRETE LTD.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.express as px
import os, json, uuid
import requests
import folium

# ── PAGE CONFIG ─────────────────────────
st.set_page_config(page_title="ARMCL ERP", layout="wide")

# ── BASIC STYLING ───────────────────────
st.markdown("""
<style>
body {background-color:#0b0f19;color:white;}
h1,h2,h3 {color:#f97316;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ───────────────────────────
DATA_FILE = "data.csv"
COLS = ["id","date","client","location","qty"]

# ── DATA FUNCTIONS ──────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=COLS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_record(rec):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([rec])])
    save_data(df)

# ── SIDEBAR ─────────────────────────────
with st.sidebar:
    st.title("🏗️ ARMCL ERP")

    page = st.radio("Navigation", [
        "📊 Dashboard",
        "➕ Add Entry",
        "📋 Records",
        "🚚 Logistics Optimization"
    ])

# ── DASHBOARD ───────────────────────────
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No data")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Total Deliveries", len(df))
        col2.metric("Total Qty", df["qty"].sum())

        fig = px.bar(df, x="date", y="qty")
        st.plotly_chart(fig, use_container_width=True)

# ── ADD ENTRY ───────────────────────────
elif page == "➕ Add Entry":
    st.title("➕ Add Delivery")

    with st.form("form"):
        d = st.date_input("Date")
        client = st.text_input("Client")
        location = st.text_input("Lat,Lng")
        qty = st.number_input("Quantity")

        if st.form_submit_button("Save"):
            rec = {
                "id": str(uuid.uuid4())[:6],
                "date": str(d),
                "client": client,
                "location": location,
                "qty": qty
            }
            add_record(rec)
            st.success("Saved!")

# ── RECORDS ─────────────────────────────
elif page == "📋 Records":
    st.title("📋 Records")

    df = load_data()
    st.dataframe(df)

# ── LOGISTICS ───────────────────────────
elif page == "🚚 Logistics Optimization":

    st.title("🚚 Logistics Optimization")

    df = load_data()

    locations = st.text_area("Enter Locations (lat,lng per line)")

    mileage = st.number_input("Mileage", value=4.0)
    fuel_price = st.number_input("Fuel Price", value=110.0)
    driver_rate = st.number_input("Driver Rate", value=200.0)

    traffic = st.selectbox("Traffic", ["Low","Medium","High"])
    factor = {"Low":1,"Medium":1.3,"High":2}[traffic]

    if st.button("Optimize"):

        locs = [l.strip() for l in locations.split("\n") if l.strip()]

        if len(locs) < 2:
            st.error("Need at least 2 locations")
        else:
            api_key = st.secrets["GOOGLE_MAPS_API_KEY"]

            url = f"https://maps.googleapis.com/maps/api/directions/json?origin={locs[0]}&destination={locs[-1]}&waypoints=optimize:true|{'|'.join(locs[1:-1])}&key={api_key}"

            res = requests.get(url).json()

            dist = 0
            time = 0
            route = []

            for leg in res["routes"][0]["legs"]:
                dist += leg["distance"]["value"]
                time += leg["duration"]["value"]
                route.append((leg["start_location"]["lat"], leg["start_location"]["lng"]))

            route.append((res["routes"][0]["legs"][-1]["end_location"]["lat"],
                          res["routes"][0]["legs"][-1]["end_location"]["lng"]))

            dist_km = dist / 1000
            time_hr = time / 3600

            fuel = (dist_km / mileage) * fuel_price
            driver = time_hr * factor * driver_rate
            total = fuel + driver

            st.metric("Distance", f"{dist_km:.2f} km")
            st.metric("Total Cost", f"৳{total:.0f}")

            m = folium.Map(location=route[0], zoom_start=10)
            for p in route:
                folium.Marker(p).add_to(m)
            folium.PolyLine(route).add_to(m)

            st.components.v1.html(m._repr_html_(), height=500)
```
