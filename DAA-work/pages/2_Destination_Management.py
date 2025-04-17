import streamlit as st
import pandas as pd
from utils import add_destination
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Register Destination", page_icon="🏚")

st.markdown("<h2>📍 Register a Destination</h2>", unsafe_allow_html=True)

st.markdown("Use the form below to add a destination in need of food.")

with st.form("destination_form"):
    dest_id = st.text_input("Destination ID")
    name = st.text_input("Name")
    latitude = st.number_input("Latitude", format="%.6f")
    longitude = st.number_input("Longitude", format="%.6f")
    people_in_need = st.number_input("People in Need", min_value=1)

    submitted = st.form_submit_button("Register Destination")

    if submitted:
        if dest_id and name:
            add_destination(dest_id, name, latitude, longitude, people_in_need)
            st.success(f"Destination '{name}' registered successfully!")
        else:
            st.error("❌ Please fill out all required fields.")

st.markdown("---")
st.header("📍 Registered Destinations Map")

try:
    df = pd.read_excel("destinations.xlsx")
    if not df.empty:
        # Center map on the first destination
        m = folium.Map(location=[df["Latitude"][0], df["Longitude"][0]], zoom_start=5)
        for _, row in df.iterrows():
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                popup=f"{row['Name']}<br>People in Need: {row['People in Need']}",
                icon=folium.Icon(color="purple", icon="home", prefix="fa")
            ).add_to(m)

        st_folium(m, width=700, height=500)
    else:
        st.info("No destinations registered yet.")
except FileNotFoundError:
    st.warning("Destination data file not found.")
except Exception as e:
    st.error(f"Error displaying map: {e}")