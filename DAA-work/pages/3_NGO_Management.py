import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from utils import add_ngo  # assuming your functions are in utils.py
import os

st.set_page_config(page_title="Register NGO", layout="wide")
st.title("🏢 Register an NGO")

# NGO Input Form
with st.form("ngo_form"):
    ngo_id = st.text_input("NGO ID")
    name = st.text_input("NGO Name")
    latitude = st.number_input("Latitude", format="%.6f")
    longitude = st.number_input("Longitude", format="%.6f")
    food_availability = st.number_input("Food Availability (units)", min_value=0)

    submitted = st.form_submit_button("Add NGO")
    if submitted:
        if not ngo_id or not name:
            st.warning("Please fill in all fields.")
        else:
            add_ngo(ngo_id, name, latitude, longitude, food_availability)
            st.success(f"✅ NGO '{name}' added!")

# Load and display NGO data
file_path = 'ngos.xlsx'
if os.path.exists(file_path):
    df = pd.read_excel(file_path)

    st.subheader("📍 NGOs on Map")
    # Center the map at average coordinates
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Name']} (Food: {row['Food_Availability']})",
            icon=folium.Icon(color='green', icon='cutlery', prefix='fa')
        ).add_to(m)

    folium_static(m)
else:
    st.info("No NGOs registered yet.")