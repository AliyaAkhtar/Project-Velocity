import plotly.express as px
import pandas as pd
import streamlit as st
import joblib
import pickle
import folium
from folium.plugins import HeatMap
import numpy as np
from geopy.distance import geodesic
from branca.colormap import linear
from streamlit_folium import folium_static
if "page" not in st.session_state:
     st.session_state.page = "home"
def navigate_to(page_name):
     st.session_state.page = page_name
def heat_map():
    st.header("🌍Interactive Heat-Map display")
    # Bit to be reused by Salman
    model = joblib.load('traffic_prediction_model.pkl')
    with open('preprocessing_pipeline.pkl', 'rb') as pipeline_file:
        pipeline = pickle.load(pipeline_file)
    # This is a file I made for fetching street data
    street_data = pd.read_excel('new traffic data.xlsx')


    # This is specific to my module, but you may take the dropdown thingies if you need it
    st.sidebar.title('Traffic Prediction Model')
    if st.sidebar.button('Back'):
            navigate_to("home")
    today_date = pd.to_datetime('today').date()
    date_input = st.sidebar.date_input('Select Date', value=pd.to_datetime('2024-11-19').date(), min_value=today_date)
    time_input = st.sidebar.time_input('Select Time', value=pd.to_datetime('2024-11-20 12:30:00').time())
    combined_datetime = pd.to_datetime(f"{date_input} {time_input}")

    from_street = st.sidebar.selectbox('Select FROM_STREET', street_data['FROM_STREET'].unique())

    # Dynamically filter TO_STREET based on selected FROM_STREET
    to_street_options = street_data.loc[street_data['FROM_STREET'] == from_street, 'TO_STREET'].unique()
    to_street = st.sidebar.selectbox('Select TO_STREET', to_street_options)

    # Get coordinates for the selected FROM_STREET and TO_STREET
    from_coords = street_data[(street_data['FROM_STREET'] == from_street) & 
                            (street_data['TO_STREET'] == to_street)].iloc[0]

    to_coords = street_data[(street_data['FROM_STREET'] == from_street) & 
                            (street_data['TO_STREET'] == to_street)].iloc[0]

    start_latitude = from_coords['START_LATITUDE']
    start_longitude = from_coords['START_LONGITUDE']
    end_latitude = to_coords['END_LATITUDE']
    end_longitude = to_coords['END_LONGITUDE']


    # Again, specific to my module. 
    def interpolate_coords(lat1, lon1, lat2, lon2, num_points=10):
        latitudes = np.linspace(lat1, lat2, num_points)
        longitudes = np.linspace(lon1, lon2, num_points)
        return list(zip(latitudes, longitudes))

    # Resuable, for predicting bus count
    if st.sidebar.button('Predict Bus Count and Display Heatmap'):
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

        X_new_transformed = pipeline.transform(X_new)
        predictions = model.predict(X_new_transformed).astype(int)

        st.write(f"Predicted Bus Count: {predictions[0]}")

        # You would require the part til here ^

        
        intermediate_coords = interpolate_coords(start_latitude, start_longitude, end_latitude, end_longitude, num_points=20)

        heatmap_data = []
        for i, (lat, lon) in enumerate(intermediate_coords):
            bus_count = predictions[0] * (1 - (i / len(intermediate_coords)))
            heatmap_data.append([lat, lon, bus_count])

        map_center = [start_latitude, start_longitude]
        zoom_level = 17  # Set a higher zoom level for a closer view

        # Create the folium map centered around the junction with a zoomed-in view
        m = folium.Map(location=map_center, zoom_start=zoom_level)

        # To calculate the bounds of all coordinates
        bounds = [[start_latitude, start_longitude], [end_latitude, end_longitude]]


        HeatMap(heatmap_data).add_to(m)

        colormap = linear.PuRd_09.scale(min([row[2] for row in heatmap_data]), max([row[2] for row in heatmap_data]))

        for lat, lon, bus_count in heatmap_data:
            color = colormap(bus_count)
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color=color,
                fill=True,
                fill_opacity=0.6,
                tooltip=f"Bus Count: {bus_count.astype(int)}"
            ).add_to(m)


        m.fit_bounds(bounds=bounds)
        folium_static(m)
    
