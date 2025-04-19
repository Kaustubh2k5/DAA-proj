import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils import add_ngo  # assumes your logic is in utils.py
import os

st.set_page_config(page_title="Register NGO", layout="wide")
st.title("🏢 Register an NGO")

st.markdown("Click on the map to select the NGO's location. Then fill out the form below to register.")

# --- 1. Interactive Clickable Map ---
default_location = [12.8405, 80.1535]  # Centered around VIT Chennai by default
map_obj = folium.Map(location=default_location, zoom_start=13)
map_obj.add_child(folium.LatLngPopup())  # Click to get coordinates

# Capture clicked location
map_data = st_folium(map_obj, height=400, width=700)
clicked_location = map_data.get("last_clicked")

latitude = clicked_location["lat"] if clicked_location else None
longitude = clicked_location["lng"] if clicked_location else None

if clicked_location:
    st.success(f"✅ Selected location: ({latitude:.6f}, {longitude:.6f})")

# --- 2. NGO Input Form ---
with st.form("ngo_form"):
    ngo_id = st.text_input("NGO ID")
    name = st.text_input("NGO Name")
    food_availability = st.number_input("Food Availability (units)", min_value=0)

    submitted = st.form_submit_button("Add NGO")

    if submitted:
        if not ngo_id or not name or latitude is None or longitude is None:
            st.warning("❗ Please complete all fields and click a location on the map.")
        else:
            add_ngo(ngo_id, name, latitude, longitude, food_availability)
            st.success(f"🎉 NGO '{name}' registered at ({latitude:.6f}, {longitude:.6f})!")

# --- 3. Display NGOs on Updated Map ---
file_path = 'ngos.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)

    if not df.empty:
        st.subheader("📍 Registered NGOs on Map")

        # Center on the newly added NGO if submitted, else average center
        if submitted and latitude and longitude:
            map_center = [latitude, longitude]
        else:
            map_center = [df['Latitude'].mean(), df['Longitude'].mean()]

        m = folium.Map(location=map_center, zoom_start=13)

        for _, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Name']}<br>Food: {row['Food_Availability']}",
                icon=folium.Icon(color='green', icon='cutlery', prefix='fa')
            ).add_to(m)

        st_folium(m, width=700, height=500)
    else:
        st.info("No NGOs registered yet.")
else:
    st.info("No NGO data file found.")
