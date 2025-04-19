import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import os

st.set_page_config(page_title="Register Volunteer", layout="centered")
st.title("🙋🏻‍♂️ Register Volunteer")

# File path for volunteers data
volunteer_file = "volunteers.csv"

# Check if the file exists
if os.path.exists(volunteer_file):
    df_volunteers = pd.read_csv(volunteer_file)
else:
    # Initialize dataframe with proper column names
    df_volunteers = pd.DataFrame(columns=["ID", "Name", "Phone", "Address", "Latitude", "Longitude", "Vehicle Type"])

# Form to register a new volunteer
with st.form("volunteer_form"):
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    vehicle = st.selectbox("Vehicle Type", ["Bike", "Car", "Van", "Truck"])
    address = st.text_input("City or Full Address")

    submitted = st.form_submit_button("Register Volunteer")

    if submitted:
        # Geocode address to lat/long
        geolocator = Nominatim(user_agent="food-distribution-app")
        location = geolocator.geocode(address)

        if location:
            lat, lon = location.latitude, location.longitude
            
            # Generate a unique ID for the new volunteer
            volunteer_id = len(df_volunteers) + 1  # Auto-increment ID based on current row count

            # Create a DataFrame with the new volunteer's data
            new_data = pd.DataFrame({
                "ID": [volunteer_id],
                "Name": [name],
                "Phone": [phone],
                "Address": [address],
                "Latitude": [lat],
                "Longitude": [lon],
                "Vehicle Type": [vehicle]
            })

            # Remove original Latitude and Longitude columns before concatenating
            df_volunteers = df_volunteers.loc[:, ~df_volunteers.columns.isin(["Latitude", "Longitude"])]

            # Rename Latitude and Longitude to lat and lon
            new_data = new_data.rename(columns={"Latitude": "lat", "Longitude": "lon"})

            # Append the new volunteer data to the existing dataframe
            df_volunteers = pd.concat([df_volunteers, new_data], ignore_index=True)

            # Save the updated data to CSV
            df_volunteers.to_csv(volunteer_file, index=False)

            st.success(f"✅ Volunteer '{name}' registered successfully!")
            st.map(new_data[["lat", "lon"]])  # Use the 'lat' and 'lon' columns for map
        else:
            st.error("❌ Could not find the location. Please enter a valid address.")