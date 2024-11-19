# Importing necessary libraries
import pandas as pd
import joblib
import pickle
import folium
from streamlit_folium import folium_static
import streamlit as st

# Using traffic prediction model
model = joblib.load('traffic_prediction_model.pkl')
with open('preprocessing_pipeline.pkl', 'rb') as pipeline_file:
    pipeline = pickle.load(pipeline_file)

# Loading the junction and traffic data
junction_data = pd.read_excel('junction_data.xlsx')
traffic_data = pd.read_excel('new traffic data.xlsx')

st.title('SMART TRAFFIC SIGNALS MANAGEMENT')

# Creating sidebar for road junction filters
st.sidebar.title('Road Junction Filters')
junction_id_selected = st.sidebar.selectbox('Select Junction ID', junction_data['Junction ID'].unique())
date_input = st.sidebar.date_input('Select Date', value=pd.to_datetime('2024-11-20'))
time_input = st.sidebar.time_input('Select Time', value=pd.to_datetime('2024-11-20 12:30:00').time())
combined_datetime = pd.to_datetime(f"{date_input} {time_input}")
junction_info = junction_data[junction_data['Junction ID'] == junction_id_selected].iloc[0]

# Extracting details of the selected junction
junction_lat = junction_info['Junction Latitude']
junction_lon = junction_info['Junction Longitude']
streets = []
street_info = {}

# Defining function to calculate green light based on bus count
def calculateTimer(bus_count):
    time_per_bus = 4
    lanes = 2 
    green_time = (bus_count * time_per_bus) // lanes
    return green_time
total_green_time = 0

# Extracting all relevant street and signal data
for i in range(1, 5):  # As there should be exactly 4 streets to make the junction
    start_lat_col = f'Street{i} Start Latitude'
    start_lon_col = f'Street{i} Start Longitude'
    end_lat_col = f'Street{i} End Latitude'
    end_lon_col = f'Street{i} End Longitude'
    
    if pd.notna(junction_info[start_lat_col]) and pd.notna(junction_info[start_lon_col]) and \
            pd.notna(junction_info[end_lat_col]) and pd.notna(junction_info[end_lon_col]):
        streets.append({
            "start": (junction_info[start_lat_col], junction_info[start_lon_col]),
            "end": (junction_info[end_lat_col], junction_info[end_lon_col]),
        })

        # Searching traffic data file to fetch the FROM_STREET and TO_STREET values
        street_match = traffic_data[(traffic_data['START_LATITUDE'] == junction_info[start_lat_col]) &
                             (traffic_data['START_LONGITUDE'] == junction_info[start_lon_col]) &
                             (traffic_data['END_LATITUDE'] == junction_info[end_lat_col]) &
                             (traffic_data['END_LONGITUDE'] == junction_info[end_lon_col])]

        if not street_match.empty:
            # Extract street data
            from_street = street_match.iloc[0]['FROM_STREET']
            to_street = street_match.iloc[0]['TO_STREET']
            start_latitude = junction_info[start_lat_col]
            start_longitude = junction_info[start_lon_col]
            end_latitude = junction_info[end_lat_col]
            end_longitude = junction_info[end_lon_col]

            # Prepare input for prediction
            new_data = pd.DataFrame({
                'TIME': [combined_datetime],
                'FROM_STREET': [from_street],
                'TO_STREET': [to_street],
                'START_LATITUDE': [start_latitude],
                'START_LONGITUDE': [start_longitude],
                'END_LATITUDE': [end_latitude],
                'END_LONGITUDE': [end_longitude],
            })
            new_data['TIME'] = pd.to_datetime(new_data['TIME'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
            new_data['HOUR'] = new_data['TIME'].dt.hour
            new_data['DAY_OF_WEEK'] = new_data['TIME'].dt.dayofweek
            new_data['MONTH'] = new_data['TIME'].dt.month

            X_new = new_data[['FROM_STREET', 'TO_STREET', 'HOUR', 'DAY_OF_WEEK', 'MONTH', 
                            'START_LATITUDE', 'START_LONGITUDE', 'END_LATITUDE', 'END_LONGITUDE']]

            # Transform and predict
            X_new_transformed = pipeline.transform(X_new)
            predictions = model.predict(X_new_transformed).astype(int)

            # Calculate the green timer for each street
            bus_count = predictions[0]  
            green_time = calculateTimer(bus_count)

            # Store information along with bus count in street_info
            street_info[f"Street {i}"] = {
                "from_street": from_street,
                "to_street": to_street,
                "bus_count": predictions[0],
                "green_time": green_time,
                "yellow_time": 3
            }
            total_green_time += green_time

# Calculating red light timer
for idx in range(1, 5):
    red_time = total_green_time - street_info[f"Street {idx}"]['green_time']
    street_info[f"Street {idx}"]['red_time'] = red_time

# Map creation
map_center = [junction_lat, junction_lon]
m = folium.Map(location=map_center, zoom_start=17)

# To calculate the bounds of all street lines (both start and end points)
bounds = [[junction_lat, junction_lon]] 

# Add the junction marker with traffic signal icon
folium.Marker(
    location=[junction_lat, junction_lon],
    tooltip=f"Junction ID: {junction_id_selected} Coordinates: ({junction_lat}, {junction_lon})",
    icon=folium.CustomIcon("signal-icon.png", icon_size=(50,50)) 
).add_to(m)

# Add markers and lines for each street
for idx, street in enumerate(streets, start=1):
    start_coords = street["start"]
    end_coords = street["end"]

    # Start marker of a street
    folium.CircleMarker(
        location=start_coords,
        radius=8,  
        color='black', 
        fill=True,  
        fill_color='white',  
        fill_opacity=1.0,
        tooltip=f"Street {idx} Start Coordinates: {start_coords}",
    ).add_to(m)

    # End amrker of a street
    folium.CircleMarker(
        location=end_coords,
        radius=8,  
        color='black',  
        fill=True,  
        fill_color='white',
        fill_opacity=1.0, 
        tooltip=f"Street {idx} End Coordinates: {end_coords}",
    ).add_to(m)

    # Line border of the street
    folium.PolyLine(
        locations=[start_coords, end_coords],
        color="blue",  
        weight=12,  
        opacity=1.0, 
        tooltip=f"Street {idx} Path",  
    ).add_to(m)

    # Line marker of the street
    folium.PolyLine(
        locations=[start_coords, end_coords],
        color="#71AFE5", 
        weight=8,  
        opacity=0.7, 
        tooltip=f"Street {idx} Path",  
    ).add_to(m)

    # Extend the bounds to include start and end coordinates of this street
    bounds.extend([start_coords, end_coords])

# Calculate the bounds of all coordinates
max_lat = max(bounds, key=lambda x: x[0])[0]  
min_lat = min(bounds, key=lambda x: x[0])[0]  
max_lon = max(bounds, key=lambda x: x[1])[1] 
min_lon = min(bounds, key=lambda x: x[1])[1]  

# Update the map to fit the bounds of all street lines and display it
m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
st.subheader(f"Road Junction Plot on Map")
folium_static(m)

# Adding custom CSS for styling the card-like output boxes
st.markdown("""
    <style>
    .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        color: black;
    }
    .card h5 {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    .card p {
        font-size: 16px;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

st.subheader("Signals Information")

# Create two columns for displaying street details
col1, col2 = st.columns(2)

# Function to generate a colored circle
def generate_circle(color):
    return f'<div style="display: inline-block; width: 20px; height: 20px; border-radius: 50%; background-color: {color}; margin-right: 10px;"></div>'

# Display street info in cards inside the two columns
with col1:
    for idx in range(1, 3):
        if f"Street {idx}" in street_info:
            red_circle = generate_circle("#B81D13")
            yellow_circle = generate_circle("#EFB700")
            green_circle = generate_circle("#008450")

            # Safely retrieve timer values to handle missing data
            red_time = street_info[f"Street {idx}"].get("red_time", "N/A")
            yellow_time = street_info[f"Street {idx}"].get("yellow_time", "N/A")
            green_time = street_info[f"Street {idx}"].get("green_time", "N/A")

            # Display street info
            st.markdown(
                f'<div class="card">'
                f'<h5>Street {idx} (From {street_info[f"Street {idx}"]["from_street"]} to {street_info[f"Street {idx}"]["to_street"]}) </h5>'
                f'<p>Predicted Bus Count: {street_info[f"Street {idx}"]["bus_count"]}'
                f'{red_circle}Red Light Timer: {red_time} seconds<br>'
                f'{yellow_circle}Yellow Light Timer: {yellow_time} seconds<br>'
                f'{green_circle}Green Light Timer: {green_time} seconds<br></p>',
                unsafe_allow_html=True
            )

with col2:
    for idx in range(3, 5):
        if f"Street {idx}" in street_info:
            red_circle = generate_circle("#B81D13")
            yellow_circle = generate_circle("#EFB700")
            green_circle = generate_circle("#008450")

            # Safely retrieve timer values to handle missing data
            red_time = street_info[f"Street {idx}"].get("red_time", "N/A")
            yellow_time = street_info[f"Street {idx}"].get("yellow_time", "N/A")
            green_time = street_info[f"Street {idx}"].get("green_time", "N/A")

            # Display street info
            st.markdown(
                f'<div class="card">'
                f'<h5>Street {idx} (From {street_info[f"Street {idx}"]["from_street"]} to {street_info[f"Street {idx}"]["to_street"]}) </h5>'
                f'<p>Predicted Bus Count: {street_info[f"Street {idx}"]["bus_count"]}'
                f'{red_circle}Red Light Timer: {red_time} seconds<br>'
                f'{yellow_circle}Yellow Light Timer: {yellow_time} seconds<br>'
                f'{green_circle}Green Light Timer: {green_time} seconds<br></p>',
                unsafe_allow_html=True
            )