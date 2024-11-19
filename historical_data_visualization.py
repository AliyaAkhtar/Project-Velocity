import streamlit as st
import pandas as pd
import altair as alt
if "page" not in st.session_state:
    st.session_state.page = "home"
def navigate_to(page_name):
    st.session_state.page = page_name
def historical_data():
# App title and description
    st.title("🚦Interactive Traffic Data Visualization Dashboard")
    st.write("Visualize and analyze 2018 historical traffic data using various chart types to gain valuable insights into traffic patterns and trends.")
    traffic_data = pd.read_csv(r'chicago-traffic-tracker-historical-congestion-estimates-by-segment-2018-current-1.csv')
    # Convert 'TIME' to datetime format, allowing errors and setting invalid dates to NaT
    traffic_data['TIME'] = pd.to_datetime(traffic_data['TIME'], format='%m/%d/%Y %H:%M:%S %p', errors='coerce')

    #  Drop rows where 'TIME' is NaT (invalid date)
    traffic_data = traffic_data.dropna(subset=['TIME'])
    # col1, col2, col3 = st.columns(3)
    # with col1:
        
    #     if st.button("Back"):
    #         navigate_to("traffic_prediction")
    
    # Sidebar filters for selecting specific street segments
    if st.sidebar.button('Back'):
        navigate_to("home")
    st.sidebar.header("Filter Options")
    
    from_street_filter = st.sidebar.selectbox("Select Start Street", options=['All'] + list(traffic_data['FROM_STREET'].unique()))
    to_street_filter = st.sidebar.selectbox("Select End Street", options=['All'] + list(traffic_data['TO_STREET'].unique()))

    # Date and Time filters
    date_filter = st.sidebar.date_input(
        "Select Date",
        min_value=traffic_data['TIME'].min().date(),
        max_value=traffic_data['TIME'].max().date(),
        value=traffic_data['TIME'].min().date()
    )
    time_range_filter = st.sidebar.slider("Select Time Range", 
                                        min_value=pd.to_datetime("00:00:00").time(), 
                                        max_value=pd.to_datetime("23:59:59").time(), 
                                        value=(pd.to_datetime("06:00:00").time(), pd.to_datetime("18:00:00").time()))

    # Apply filters only if specific options are selected
    if from_street_filter != 'All':
        traffic_data = traffic_data[traffic_data['FROM_STREET'] == from_street_filter]
    if to_street_filter != 'All':
        traffic_data = traffic_data[traffic_data['TO_STREET'] == to_street_filter]

    # Filter by selected date and time range
    traffic_data = traffic_data[traffic_data['TIME'].dt.date == date_filter]
    traffic_data = traffic_data[(traffic_data['TIME'].dt.time >= time_range_filter[0]) & (traffic_data['TIME'].dt.time <= time_range_filter[1])]

    # If traffic_data is empty, show a warning message
    if traffic_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Limit the filtered data to 500 rows by default
        traffic_data = traffic_data.head(500)

        # Line chart for Bus Count Over Time
        st.write("### Bus Count Over Time")
        line_chart = alt.Chart(traffic_data).mark_line().encode(
            x='TIME:T',
            y='BUS_COUNT:Q',
            tooltip=['TIME:T', 'BUS_COUNT:Q', 'FROM_STREET:N', 'TO_STREET:N']
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)

        # Bar chart for Aggregated Bus Count by Street Segment
        st.write("### Aggregated Bus Count by Street Segment")
        street_segment_data = traffic_data.groupby(['FROM_STREET', 'TO_STREET']).agg({'BUS_COUNT': 'sum'}).reset_index()
        bar_chart = alt.Chart(street_segment_data).mark_bar().encode(
            x='FROM_STREET:N',
            y='BUS_COUNT:Q',
            color='TO_STREET:N',
            tooltip=['FROM_STREET:N', 'TO_STREET:N', 'BUS_COUNT:Q']
        ).interactive()
        st.altair_chart(bar_chart, use_container_width=True)

        # Pie chart for Bus Count Proportion by Street Segment
        st.write("### Bus Count Proportion by Street Segment")
        segment_data = traffic_data.groupby(['FROM_STREET', 'TO_STREET']).agg({'BUS_COUNT': 'sum'}).reset_index()
        pie_chart = alt.Chart(segment_data).mark_arc().encode(
            theta=alt.Theta(field="BUS_COUNT", type="quantitative"),
            color=alt.Color(field="FROM_STREET", type="nominal"),
            tooltip=['FROM_STREET', 'TO_STREET', 'BUS_COUNT']
        )
        st.altair_chart(pie_chart, use_container_width=True)

        # Insights Section
        st.write("### Insights")
        st.write("- **Line Chart**: Shows the bus count over time, allowing you to observe trends for the selected street segment.")
        st.write("- **Bar Chart**: Displays daily aggregated bus counts to identify peak days.")
        st.write("- **Pie Chart**: Illustrates the proportion of bus counts by street segments, helping to compare traffic volumes between different streets.")