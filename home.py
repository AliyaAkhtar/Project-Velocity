import streamlit as st
from traffic_signal_management import traffic_prediction_app
from heat_congestion_map import heat_map
from historical_data_visualization import historical_data
import streamlit.components.v1 as components

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"  # Default page

# Function to handle page navigation
def navigate_to(page_name):
    st.session_state.page = page_name

# Define the Home Page
def home_page():
    st.sidebar.header("Predict Traffic, Optimize Journeys!")
   
    st.sidebar.markdown(
    """
    <style>
    @keyframes typing {
        0% { width: 0; }
        100% { width: 100%; }
    }

    .typing-text {
        font-size: 25px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        border-right: 1px solid black;
        width: 2;
        margin:3px;
        animation: typing 3s steps(80) 1s forwards; 
        
    }

    .typing-text1 {
        font-size: 25px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        border-right: 1px solid black;
        width: 0;
        animation: typing 3s steps(80) 1s forwards; 
        animation-delay: 4s;
    }
    .typing-text2 {
        font-size: 25px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        border-right: 1px solid black;
        width: 0;
        animation: typing 3s steps(80) 1s forwards; 
          animation-delay: 7s;
    }

    .typing-container {
        display: flex;
        flex-direction: column;
        gap: 20px; /* Space between lines */
    }
    </style>

    <div class="typing-container">
        <div class="typing-text">
        Manage Traffic Flow
        </div>
        <div class="typing-text1">
            with AI Predictions
        </div>
        <div class="typing-text2">
            and Smart Signal Control.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    video_html = """
    <style>
        html, body {
        margin: 0;
        padding: 0;
        height: 100%;  
        width: 100%;
          
        }
        .container {
            display: flex;
            align-items: center;  
            justify-content: space-between; 
            padding: 20px;
        }

        /* Style for the slider container */
        .slider-container {
            width: 20%;  
            display: flex;
            flex-direction: column;
            align-items: flex-start;  
            gap: 15px;
        }

        /* Slider styling */
        .slider {
            width: 100%;
        }

        /* Text for the slider */
        .slider-text {
            font-size: 18px;
            color: white;
        }
                .image-container {
            display: flex;
            justify-content: space-around; 
            gap: 10px; 
        }

        /* Style for each image and its container */
        .image-container .image-item {
            position: relative; 
        }

        /* Image style */
        .image-container img {
            height: 200px;
            width: 225px;
            max-width: 300px;
            transition: opacity 0.3s ease; 
        }

       
        .image-container .image-text {
            position: absolute;
            top: 50%; 
            left: 50%;  
            transform: translate(-50%, -50%); 
            color: white;
            font-size: 20px;
            font-weight: bold;
            opacity: 0;  
            transition: opacity 0.3s ease; 
        }

        .image-container .image-item:hover img {
            opacity: 0.6;  
        }

        .image-container .image-item:hover .image-text {
            opacity: 1;  
        }
        .background-video {
            position: fixed;
            top: 0;
            left: 0;
            width: 800px;
            height: 100%;
            object-fit: cover;
            z-index: -1;
        }
        .content {
            position: relative;
            z-index: 1;
            text-align: center;
            color: white;
            font-family: Arial, sans-serif;
            margin-top: 50px;
        }
        .content h1 {
            font-size: 70px;
            margin-bottom: 20px;
        }
        .content p {
            font-size: 24px;
            margin-bottom: 50px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
        }
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        @media (max-width: 768px) {
        .sidebar {
            width: 50%;  
        }

        .content-area {
            width: 50%;  
        }
        }
    </style>
     
    <video style="width:1200px;float:left" class="background-video" autoplay loop muted>
        <source src="https://static.vecteezy.com/system/resources/previews/040/334/978/mp4/night-car-traffic-in-central-streets-in-tula-russia-october-18-2021-free-video.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <div class="content">
        <h1>VeloCity</h1>
        <p>Smart Traffic Prediction and Control System</p>
        
    </div>
    <div class="image-container">
        <div class="image-item">
          <img src="https://img.freepik.com/free-vector/hand-drawn-illustrated-gathering-data-concept_23-2149139706.jpg?t=st=1731988759~exp=1731992359~hmac=813e268e98cf25b6640166d0a8c0b0535b98bc85db7b55a49435d054a519a14a&w=900" alt="Data Visualization Dashboard">
          <div class="image-text" style="font-family: Arial, sans-serif;">Data Visualization Dashboard</div>
         </div>

        <div class="image-item">
         <img src="https://img.freepik.com/free-vector/map-light-concept-illustration_114360-192.jpg?t=st=1731988735~exp=1731992335~hmac=502ba9116963a3f0ef76581933f6ee8d6912c0da355da40e523af8396993aeac&w=740">
         <div class="image-text" style="font-family: Arial, sans-serif;">Traffic Congestion with Heatmaps</div>
        </div>
        
         <div class="image-item">
        <img src="https://img.freepik.com/free-vector/surface-transport-abstract-concept-vector-illustration-road-transport-movement-goods-people-road-rail-truck-highway-roundabout-traffic-car-driving-fast-bus-stop-abstract-metaphor_335657-1726.jpg?t=st=1731988798~exp=1731992398~hmac=8f43fc4d3f0047c73f25a4a964e8d849b8bd661b50bdb5ef4b59672825b68a61&w=740" alt="Traffic Junction">
        <div class="image-text" style="font-family: Arial, sans-serif;">Smart Traffic Signals Management</div>
        </div>
    </div>
   
    """
   
    components.html(video_html,height=400)
   
    col1, col2, col3 = st.columns(3)
    st.markdown(
        """
        <style>
        .stButton>button {
            width: 100%; 
            height: 50px; 
            background-color: #cccccc
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #d3d3d3
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # First Column
    with col1:
        
        if st.button("Data Visualization Dashboard"):
            navigate_to("historical_data")
    
    # Second Column
    with col2:
       
        if st.button("Traffic Congestion with Heatmaps"):
            navigate_to("heat_map")

    # Third Column
    with col3:
        
        if st.button("Smart Traffic Signals Management"):
            navigate_to("traffic_prediction")

def heat_map_page():
    heat_map()  
    if st.button("Back to Home"):
        navigate_to("home")
def historical_data_page():
    historical_data()
    if st.button("Back to Home"):
        navigate_to("home")

# Render the appropriate page
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "traffic_prediction":
    traffic_prediction_app()
elif st.session_state.page == "heat_map":
    heat_map()
elif st.session_state.page == "historical_data":
    historical_data()
    
