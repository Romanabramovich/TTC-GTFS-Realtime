import pandas as pd
import folium
from folium.plugins import MarkerCluster

subway_ids = [73605, 73606, 73607]

def preprocess_and_cache_data(subway_ids):
    #Filter columns in static trips data 
    trips_data = pd.read_csv("./TTC-GTFS-Static/trips.txt", usecols = ["route_id", "trip_id", "shape_id"])
    filtered_trips = trips_data[trips_data["route_id"].isin(subway_ids)]
    shape_ids = filtered_trips["shape_id"].unique()
    
    #Filter columns in static shapes data
    shapes_data = pd.read_csv("./TTC-GTFS-Static/shapes.txt", usecols=["shape_id", "shape_pt_lat", "shape_pt_lon"])
    filtered_shapes = shapes_data[shapes_data["shape_id"].isin(shape_ids)]

    #Filter coloumns in trips data
    filtered_trips.to_csv("./filtered_trips.csv", index=False)
    filtered_shapes.to_csv("./filtered_shapes.csv", index=False)
    
def visualize_route(route_ids):
    filtered_trips = pd.read_csv("./filtered_trips.csv")
    filtered_shapes = pd.read_csv("./filtered_shapes.csv")
    
    toronto_map = folium.Map(location=[43.6532, -79.3832], zoom_start=12, tiles="CartoDB positron")
    
    for route_id in route_ids:
            
        #Filter trips to find route shapes associated with route_id
        shape_ids = filtered_trips[filtered_trips["route_id"] == route_id]["shape_id"].unique()
        
        #Filter routes to only include relevant route shapes
        route_shapes = filtered_shapes[filtered_shapes["shape_id"].isin(shape_ids)]
        
        #Route color
        route_color = get_route_color(route_id)
        
        #Add route to map
        for _, group in route_shapes.groupby("shape_id"):
            points = group[["shape_pt_lat", "shape_pt_lon"]].values.tolist()
            folium.PolyLine(points, color = route_color, weight=2.5).add_to(toronto_map)
        
    map_path = "./templates/toronto_map.html"
    toronto_map.save(map_path)

def get_route_color(route_id):
    routes_info = pd.read_csv("./TTC-GTFS-Static/routes.txt")

    route = routes_info[routes_info["route_id"] == route_id]
    
    if not route.empty:
        route_color = route.iloc[0]["route_color"] if "route_color" in route.columns else "000000"
        return f"#{route_color}"
    else:
        return "#000000"
    
# Preprocess and cache the data
preprocess_and_cache_data(subway_ids)

# Visualize the selected routes
visualize_route(subway_ids)

