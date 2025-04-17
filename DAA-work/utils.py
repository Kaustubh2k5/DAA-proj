import streamlit as st
import pandas as pd
import os
import pandas as pd
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic



def add_ngo(ngo_id, name, latitude, longitude, food_availability, file_path='ngos.xlsx'):
    # Create a new NGO record
    new_ngo = {
        'ID': ngo_id,
        'Name': name,
        'Latitude': latitude,
        'Longitude': longitude,
        'Food_Availability': food_availability
    }

    # If file exists, append to it
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([new_ngo])], ignore_index=True)
    else:
        df = pd.DataFrame([new_ngo])

    # Save back to Excel
    df.to_excel(file_path, index=False)
    print(f"✅ NGO '{name}' added successfully.")






def add_destination(dest_id, name, latitude, longitude, people_in_need, file_path='destinations.xlsx'):
    # Create new destination entry
    new_dest = {
        'ID': dest_id,
        'Name': name,
        'Latitude': latitude,
        'Longitude': longitude,
        'People in Need': people_in_need  # ✅ updated key
    }

    # If file exists, append to it
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([new_dest])], ignore_index=True)
    else:
        df = pd.DataFrame([new_dest])

    # Save back to Excel
    df.to_excel(file_path, index=False)
    print(f"✅ Destination '{name}' added successfully.")





def add_volunteer(aadhar_id, name, latitude, longitude, status='available', file_path='volunteers.xlsx'):
    # Create new volunteer entry
    new_volunteer = {
        'Aadhar_ID': str(aadhar_id),
        'Name': name,
        'Latitude': latitude,
        'Longitude': longitude,
        'Status': status.lower()  # e.g., 'available' or 'busy'
    }

    # If file exists, append to it
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([new_volunteer])], ignore_index=True)
    else:
        df = pd.DataFrame([new_volunteer])

    # Save back to Excel
    df.to_excel(file_path, index=False)
    print(f"✅ Volunteer '{name}' added successfully.")




def build_weighted_graph(node_df, node_type="NGO"):
    coords = [(row['Latitude'], row['Longitude']) for idx, row in node_df.iterrows()]
    G = nx.Graph()

    for idx, (lat, lon) in enumerate(coords):
        node_id = f"{node_type}_{idx}"
        G.add_node(node_id, pos=(lat, lon), label=node_id)

    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            node_i = f"{node_type}_{i}"
            node_j = f"{node_type}_{j}"
            loc1, loc2 = coords[i], coords[j]
            try:
                dist = ox.distance.shortest_path_length(
                    G=ox.graph_from_point(loc1, dist=10000, network_type='drive'),
                    orig=ox.distance.nearest_nodes(G=ox.graph_from_point(loc1, dist=10000, network_type='drive'), X=loc1[1], Y=loc1[0]),
                    dest=ox.distance.nearest_nodes(G=ox.graph_from_point(loc2, dist=10000, network_type='drive'), X=loc2[1], Y=loc2[0]),
                    weight='length'
                ) / 1000
            except Exception:
                dist = geodesic(loc1, loc2).km

            G.add_edge(node_i, node_j, weight=dist)

    return G





def assign_routes(ngo_df, dest_df, volunteer_df):
    ngo_graph = build_weighted_graph(ngo_df, node_type="NGO")
    dest_graph = build_weighted_graph(dest_df, node_type="Dest")
    combined_graph = nx.compose(ngo_graph, dest_graph)

    route_info = {}

    for volunteer_idx, volunteer in volunteer_df.iterrows():
        volunteer_pos = (volunteer['Latitude'], volunteer['Longitude'])

        closest_ngo = None
        min_dist = float('inf')
        closest_ngo_id = None

        for idx in ngo_df.index:
            ngo_pos = (ngo_df.loc[idx, 'Latitude'], ngo_df.loc[idx, 'Longitude'])
            dist = geodesic(volunteer_pos, ngo_pos).km
            if dist < min_dist:
                closest_ngo = idx
                closest_ngo_id = f"NGO_{idx}"
                min_dist = dist

        volunteer_route = [closest_ngo_id]

        for dest_idx in dest_df.index:
            dest_id = f"Dest_{dest_idx}"
            try:
                shortest_path = nx.shortest_path(combined_graph, source=closest_ngo_id, target=dest_id, weight='weight')
                volunteer_route.extend(shortest_path[1:])
            except nx.NetworkXNoPath:
                continue

        total_distance = 0
        for i in range(len(volunteer_route) - 1):
            u = volunteer_route[i]
            v = volunteer_route[i + 1]
            total_distance += combined_graph[u][v]['weight']

        route_info[volunteer['ID']] = {
            'Route': volunteer_route,
            'Total Distance (km)': total_distance
        }

    return route_info





# Displaying the routes on a map using Streamlit (optional)
def display_routes(route_info, ngo_df, dest_df):
    """
    Display routes on a map using Streamlit.
    Args:
        route_info (dict): Routes assigned to volunteers
        ngo_df (pd.DataFrame): NGO DataFrame
        dest_df (pd.DataFrame): Destination DataFrame
    """
    import folium
    import streamlit as st
    from streamlit_folium import folium_static

    # Initialize the map at a central point
    m = folium.Map(location=[ngo_df['Latitude'].mean(), ngo_df['Longitude'].mean()], zoom_start=13)

    # Add NGO markers
    for idx, row in ngo_df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']], popup=row['Name'], icon=folium.Icon(color='green')).add_to(m)

    # Add Destination markers
    for idx, row in dest_df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']], popup=row['Name'], icon=folium.Icon(color='red')).add_to(m)

    # Add routes for volunteers
    for volunteer_id, info in route_info.items():
        route = info['Route']
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i + 1]

            # Extract index and type for both nodes
            if u.startswith("NGO_"):
                u_idx = int(u.split("_")[1])
                u_pos = (ngo_df.loc[u_idx, 'Latitude'], ngo_df.loc[u_idx, 'Longitude'])
            elif u.startswith("Dest_"):
                u_idx = int(u.split("_")[1])
                u_pos = (dest_df.loc[u_idx, 'Latitude'], dest_df.loc[u_idx, 'Longitude'])

            if v.startswith("NGO_"):
                v_idx = int(v.split("_")[1])
                v_pos = (ngo_df.loc[v_idx, 'Latitude'], ngo_df.loc[v_idx, 'Longitude'])
            elif v.startswith("Dest_"):
                v_idx = int(v.split("_")[1])
                v_pos = (dest_df.loc[v_idx, 'Latitude'], dest_df.loc[v_idx, 'Longitude'])

            folium.PolyLine([u_pos, v_pos], color='blue', weight=2.5, opacity=1).add_to(m)

    # Display map
    st.write("### Volunteer Routes")
    folium_static(m)