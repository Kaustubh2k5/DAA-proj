import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from geopy.distance import geodesic
import streamlit as st
import folium
from streamlit_folium import st_folium
from random import randint
from folium import Popup
import hashlib
from sklearn.metrics.pairwise import haversine_distances
from math import radians

# 📁 Load the data
def load_data():
    if not os.path.exists("volunteers.csv") or os.stat("volunteers.csv").st_size == 0:
        st.error("volunteers.csv is missing or empty.")
        return None, None, None
    if not os.path.exists("ngos.xlsx") or os.stat("ngos.xlsx").st_size == 0:
        st.error("ngos.xlsx is missing or empty.")
        return None, None, None
    if not os.path.exists("destinations.xlsx") or os.stat("destinations.xlsx").st_size == 0:
        st.error("destinations.xlsx is missing or empty.")
        return None, None, None

    volunteers = pd.read_csv("volunteers.csv")
    ngos = pd.read_excel("ngos.xlsx")
    destinations = pd.read_excel("destinations.xlsx")

    volunteers.rename(columns={'lat': 'Latitude', 'lon': 'Longitude'}, inplace=True)

    return volunteers, ngos, destinations


# 🔄 Normalize needs vs availability
@st.cache_resource
def normalize_food_supply(ngos, destinations):
    total_need = destinations["People in Need"].sum()
    total_supply = ngos["Food_Availability"].sum()

    if total_supply < total_need:
        scale_factor = total_supply / total_need
        destinations["Adjusted Need"] = (destinations["People in Need"] * scale_factor).round().astype(int)
    else:
        destinations["Adjusted Need"] = destinations["People in Need"]

    return ngos, destinations


# 👥 Group NGOs and destinations among volunteers using KMeans clustering
@st.cache_resource
def assign_locations(volunteers, ngos, destinations):
    num_volunteers = len(volunteers)
    volunteers["Volunteer_ID"] = range(num_volunteers)

    # Label types
    ngos["Type"] = "NGO"
    destinations["Type"] = "Destination"

    # Combine and compute coordinates
    combined = pd.concat([ngos, destinations], ignore_index=True)
    coords = combined[["Latitude", "Longitude"]].applymap(radians).values

    # KMeans based on geo coordinates
    kmeans = KMeans(n_clusters=num_volunteers, random_state=42, n_init='auto')
    cluster_labels = kmeans.fit_predict(coords)
    combined["Cluster"] = cluster_labels

    # Split back into NGO and destinations
    ngos = combined[combined["Type"] == "NGO"].copy()
    destinations = combined[combined["Type"] == "Destination"].copy()

    # Calculate supply/need per cluster
    cluster_info = {}
    for i in range(num_volunteers):
        ngo_group = ngos[ngos["Cluster"] == i]
        dest_group = destinations[destinations["Cluster"] == i]

        total_supply = ngo_group["Food_Availability"].sum()
        total_need = dest_group["Adjusted Need"].sum()

        cluster_info[i] = {
            "supply": total_supply,
            "need": total_need,
            "ngos": ngo_group,
            "destinations": dest_group
        }

    # Rebalance destinations: if cluster supply << need, move nearest destination to another cluster
    for _ in range(3):  # Multiple passes to stabilize
        for cid, info in cluster_info.items():
            excess = info["supply"] - info["need"]
            if excess < 0:  # Need more supply, try moving a destination out
                dests = info["destinations"]
                if len(dests) <= 1:
                    continue
                for _, row in dests.iterrows():
                    # Find nearest other cluster
                    d_coord = [radians(row["Latitude"]), radians(row["Longitude"])]
                    best_cid = None
                    min_dist = float('inf')

                    for other_cid in cluster_info:
                        if other_cid == cid:
                            continue
                        other_centroid = kmeans.cluster_centers_[other_cid]
                        dist = haversine_distances([d_coord, other_centroid])[0][1]
                        if dist < min_dist:
                            min_dist = dist
                            best_cid = other_cid

                    # Move destination
                    if best_cid is not None:
                        cluster_info[cid]["destinations"] = cluster_info[cid]["destinations"].drop(index=row.name)
                        cluster_info[cid]["need"] -= row["Adjusted Need"]

                        cluster_info[best_cid]["destinations"] = pd.concat([
                            cluster_info[best_cid]["destinations"],
                            pd.DataFrame([row])
                        ])
                        cluster_info[best_cid]["need"] += row["Adjusted Need"]
                        break

    # Rebuild final DataFrames
    ngo_list, dest_list = [], []
    for i, info in cluster_info.items():
        info["ngos"]["Volunteer_ID"] = i
        info["destinations"]["Volunteer_ID"] = i
        ngo_list.append(info["ngos"])
        dest_list.append(info["destinations"])

    ngos_final = pd.concat(ngo_list, ignore_index=True).drop(columns=["Type", "Cluster"])
    destinations_final = pd.concat(dest_list, ignore_index=True).drop(columns=["Type", "Cluster"])

    return volunteers, ngos_final, destinations_final



# 📍 Helper to compute route using greedy TSP approximation
@st.cache_resource
def compute_greedy_route(start, locations):
    route = [start]
    remaining = locations.copy()

    current = start
    while remaining:
        next_loc = min(remaining, key=lambda x: geodesic(current, x).km)
        route.append(next_loc)
        remaining.remove(next_loc)
        current = next_loc

    return route


@st.cache_resource
def build_volunteer_routes(volunteers, ngos, destinations):
    routes = {}

    for i, vol in volunteers.iterrows():
        vol_id = i
        start_point = (vol["Latitude"], vol["Longitude"])

        vol_ngos = ngos[ngos["Volunteer_ID"] == vol_id]
        vol_dests = destinations[destinations["Volunteer_ID"] == vol_id]

        pickup_locs = list(zip(vol_ngos["Latitude"], vol_ngos["Longitude"]))
        drop_locs = list(zip(vol_dests["Latitude"], vol_dests["Longitude"]))

        # Skip volunteers with no deliveries
        if not pickup_locs and not drop_locs:
            continue

        pickup_route = compute_greedy_route(start_point, pickup_locs) if pickup_locs else [start_point]
        delivery_route = compute_greedy_route(pickup_route[-1], drop_locs) if drop_locs else []

        full_route = pickup_route + delivery_route[1:] if delivery_route else pickup_route

        routes[vol["Name"] if "Name" in vol else f"Volunteer_{i}"] = full_route

    return routes


# 👇 Function to generate a unique color
def get_color_from_id(vol_id):
    hex_hash = hashlib.md5(str(vol_id).encode()).hexdigest()
    return f"#{hex_hash[:6]}"

import openrouteservice
from openrouteservice import convert
import random
import requests

def snap_to_nearest(lat, lon, ors_key, max_retries=5, jitter_attempts=5, base_radius=350):
    url = "https://api.openrouteservice.org/v2/nearest"
    headers = {
        "Authorization": ors_key,
        "Content-Type": "application/json"
    }

    def try_snap(lat_, lon_, radius_):
        body = {"coordinates": [[lon_, lat_]], "radius": radius_}
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            coords = response.json()["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0]
        except:
            return None

    # First try actual point with expanding radius
    for i in range(max_retries):
        radius = base_radius * (i + 1)  # Expanding radius with retries
        snapped = try_snap(lat, lon, radius)
        if snapped:
            return snapped
    
    # If no snapping found, consider larger radius (up to 1 km)
    radius = 1000  # 1 km
    snapped = try_snap(lat, lon, radius)
    if snapped:
        return snapped

    # Jitter and retry nearby points for better luck
    for _ in range(jitter_attempts):
        lat_jittered = lat + random.uniform(-0.0005, 0.0005)
        lon_jittered = lon + random.uniform(-0.0005, 0.0005)
        snapped = try_snap(lat_jittered, lon_jittered, base_radius)
        if snapped:
            return snapped

    # If still unsuccessful, warn and return original coordinates
    st.warning(f"⚠ Failed to snap ({lat}, {lon}) even after expanding radius and jittering.")
    return lat, lon


import folium
from folium import Popup
import streamlit as st
from streamlit_folium import st_folium

def get_unique_color(index):
    # Generate visually distinct colors (repeat-safe)
    base_colors = [
        "#FF5733", "#33FF57", "#3357FF", "#F39C12", "#9B59B6",
        "#1ABC9C", "#E74C3C", "#8E44AD", "#2ECC71", "#3498DB",
        "#E67E22", "#16A085", "#2980B9", "#D35400", "#C0392B"
    ]
    
    if index < len(base_colors):
        return base_colors[index]
    else:
        # Generate a random hex color for more routes
        import random
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
def display_routes_on_map(volunteers, routes, ngos, destinations):
    avg_lat = volunteers["Latitude"].mean()
    avg_lon = volunteers["Longitude"].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    ors_key = "5b3ce3597851110001cf6248d2d13a3a91b24d658890fe0b396b2550"
    client = openrouteservice.Client(key=ors_key)

    for idx, (vol_id, route) in enumerate(routes.items()):
        color = get_unique_color(idx)  # Unique color based on index

        # 🔄 Snap each point in the route
        snapped_route = [snap_to_nearest(pt[0], pt[1], ors_key) for pt in route]
        coords = [(pt[1], pt[0]) for pt in snapped_route]  # ORS expects [lon, lat]

        # 🚗 Request actual driving route from ORS
        try:
            geometry = client.directions(
                coords,
                profile='driving-car',
                format='geojson'
            )["features"][0]["geometry"]

            folium.GeoJson(
                geometry,
                name=f"Volunteer {vol_id}",
                style_function=lambda x, color=color: {
                    'color': color, 'weight': 4, 'opacity': 0.8
                }
            ).add_to(m)
        except Exception as e:
            st.error(f"❌ Failed to get route for Volunteer {vol_id}: {e}")
            continue

        # 📍 Add markers and info for all points (including start and end)
        for i, point in enumerate(route):
            popup_text = f"Volunteer {vol_id} "
            icon_color = "blue"

            ngo_at_point = ngos[(ngos["Latitude"] == point[0]) & (ngos["Longitude"] == point[1])]
            dest_at_point = destinations[(destinations["Latitude"] == point[0]) & (destinations["Longitude"] == point[1])]

            if not ngo_at_point.empty:
                food_picked_up = ngo_at_point["Food_Availability"].values[0]
                popup_text += f"Pickup: {food_picked_up} units"
                icon_color = "green"
                folium.CircleMarker(point, radius=5, color='green', fill=True, fill_color='green',
                                    popup=popup_text).add_to(m)

            elif not dest_at_point.empty:
                food_dropped_off = dest_at_point["Adjusted Need"].values[0]
                popup_text += f"Drop-off: {food_dropped_off} units"
                icon_color = "red"
                folium.CircleMarker(point, radius=5, color='red', fill=True, fill_color='red',
                                    popup=popup_text).add_to(m)

            else:
                popup_text += f"{'Start' if i == 0 else 'End' if i == len(route) - 1 else 'Transit'} Point"
                icon_color = "blue"

            folium.Marker(
                point,
                popup=Popup(popup_text, parse_html=True),
                icon=folium.Icon(color=icon_color)
            ).add_to(m)

    st.subheader("📌 Volunteer Routes Map")
    st_folium(m, width=900, height=600)


def main():
    st.title("🥫 Food Distribution Route Optimizer")

    volunteers, ngos, destinations = load_data()

    if volunteers is None or ngos is None or destinations is None:
        return

    ngos, destinations = normalize_food_supply(ngos, destinations)
    volunteers, ngos, destinations = assign_locations(volunteers, ngos, destinations)
    routes = build_volunteer_routes(volunteers, ngos, destinations)

    display_routes_on_map(volunteers, routes, ngos, destinations)


if __name__== "__main__":
    main()