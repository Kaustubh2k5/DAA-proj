import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils import add_destination

st.set_page_config(page_title="Register Destination", page_icon="🏚")

st.markdown("<h2>📍 Register a Destination</h2>", unsafe_allow_html=True)
st.markdown("Click on the map to select the location, then fill in the details below.")

# --- 1. Show clickable map for location selection ---
default_location = [12.8405, 80.1535]  # Center map around VIT Chennai
click_map = folium.Map(location=default_location, zoom_start=13)
click_map.add_child(folium.LatLngPopup())  # Enable click popup to show lat/lon
map_data = st_folium(click_map, height=400, width=700)

clicked_location = map_data.get("last_clicked")
latitude = clicked_location["lat"] if clicked_location else None
longitude = clicked_location["lng"] if clicked_location else None

if clicked_location:
    st.success(f"✅ Location selected: ({latitude:.6f}, {longitude:.6f})")

# --- 2. Destination Registration Form ---
with st.form("destination_form"):
    dest_id = st.text_input("Destination ID")
    name = st.text_input("Name")
    people_in_need = st.number_input("People in Need", min_value=1)

    submitted = st.form_submit_button("Register Destination")

    if submitted:
        if dest_id and name and latitude is not None and longitude is not None:
            add_destination(dest_id, name, latitude, longitude, people_in_need)
            st.success(f"Destination '{name}' registered at ({latitude:.6f}, {longitude:.6f})!")
        else:
            st.error("❌ Please fill out all fields and select a location on the map.")

# --- 3. Display Registered Destinations (after submit) ---
st.markdown("---")
st.header("📍 Registered Destinations Map")

try:
    df = pd.read_excel("destinations.xlsx")

    if not df.empty:
        map_view = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=12)

        for _, row in df.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=f"{row['Name']}<br>People in Need: {row['People in Need']}",
                icon=folium.Icon(color="purple", icon="home", prefix="fa")
            ).add_to(map_view)

        st_folium(map_view, width=700, height=500)
    else:
        st.info("No destinations registered yet.")

except FileNotFoundError:
    st.warning("Destination data file not found.")
except Exception as e:
    st.error(f"Error displaying registered destinations: {e}")
