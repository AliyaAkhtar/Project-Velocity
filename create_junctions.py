import pandas as pd
import numpy as np
from scipy.spatial import KDTree

# Input and output file names
input_file = 'new traffic data.xlsx'
output_file = 'raw_junction_data.xlsx'

data = pd.read_excel(input_file)

# Combine all possible coordinate pairs (start and end points) for proximity checks
data['Start Coordinates'] = list(zip(data['START_LATITUDE'], data['START_LONGITUDE']))
data['End Coordinates'] = list(zip(data['END_LATITUDE'], data['END_LONGITUDE']))
coordinates = data['Start Coordinates'].tolist() + data['End Coordinates'].tolist()

# Create a KDTree for fast spatial querying
tree = KDTree(coordinates)

# Parameters
distance_threshold = 0.001
min_streets_per_junction = 6  
max_streets_per_junction = 8  

# Initialize junction data
junctions = []
visited_indices = set()
junction_id = 1

# Iterate through the dataset to find nearby points and form junctions
for idx, coord in enumerate(coordinates):
    if idx in visited_indices:
        continue  

    # Find all nearby coordinates within the threshold
    nearby_indices = tree.query_ball_point(coord, distance_threshold)

    # Filter out visited indices
    nearby_indices = [i for i in nearby_indices if i not in visited_indices]

    # A valid junction must have between 6 to 8 streets (which would be blended into 3 to 4)
    if min_streets_per_junction <= len(nearby_indices) <= max_streets_per_junction:  # 6 to 8 streets
        # Mark the indices as visited
        visited_indices.update(nearby_indices)

        # Calculate the average coordinates for the junction
        nearby_coords = [coordinates[i] for i in nearby_indices]
        junction_coords = np.mean(nearby_coords, axis=0)

        # Create a record for the junction
        junction_record = {
            'Junction ID': f"J-{junction_id}",
            'Junction Latitude': junction_coords[0],
            'Junction Longitude': junction_coords[1],
        }

        # Add details of the streets contributing to the junction
        street_indices = [i % len(data) for i in nearby_indices]  # Map indices back to original rows
        for i, street_idx in enumerate(street_indices, start=1):
            street = data.iloc[street_idx]
            junction_record[f'Street{i} Start Latitude'] = street['START_LATITUDE']
            junction_record[f'Street{i} Start Longitude'] = street['START_LONGITUDE']
            junction_record[f'Street{i} End Latitude'] = street['END_LATITUDE']
            junction_record[f'Street{i} End Longitude'] = street['END_LONGITUDE']

        # Add the record to the list of junctions
        junctions.append(junction_record)
        junction_id += 1

# Save the junction data to an Excel file
junctions_df = pd.DataFrame(junctions)
junctions_df.to_excel(output_file, index=False)

print(f"Junctions with {min_streets_per_junction} to {max_streets_per_junction} streets saved to {output_file}")