from src.df_processing import parse_protobuf_to_dataframe
from src.utils import preprocess_and_cache_data, get_route_color, get_optimal_map_view
import pandas as pd
import folium
import os


def get_static_bus_route(bus_number):
    """Visualizes the bus route and live vehicle locations on a map."""
    route_id = preprocess_and_cache_data(bus_number)
    if not route_id:
        print(f"🚨 No valid route_id found for bus {bus_number}.")
        return None  # Return None if no route ID

    filtered_trips = pd.read_csv("./filtered_trips.csv", dtype={"shape_id": str})
    filtered_shapes = pd.read_csv(
        "./filtered_shapes.csv", dtype={"shape_pt_lon": float, "shape_pt_lat": float}
    )

    center_lat, center_lon, zoom_level = get_optimal_map_view(filtered_shapes)

    toronto_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles="CartoDB positron",
    )

    # Add the route shape to the map
    shape_ids = filtered_trips["shape_id"].unique().tolist()

    if len(shape_ids) == 0:
        print(f"🚨 No shape data found for bus {bus_number} (route_id {route_id})!")
        return None  # Stop execution if no shape IDs exist

    route_color = get_route_color(route_id)
    shape_data_exists = False  # Flag to check if any shape was added

    for shape_id, group in filtered_shapes.groupby("shape_id"):
        group = group.sort_values("shape_pt_sequence")
        points = group[["shape_pt_lat", "shape_pt_lon"]].values.tolist()

        if len(points) == 0:
            print(f"⚠️ Warning: No points found for shape_id {shape_id}!")
            continue  # Skip this shape and move to the next one

        shape_data_exists = True  # At least one shape exists
        folium.PolyLine(points, color=route_color, weight=3, opacity=0.6).add_to(
            toronto_map
        )

    if not shape_data_exists:
        print(f"🚨 No valid shape data available for route {route_id}.")
        return None  # Don't save a blank map

    # Get live bus locations
    vehicle_df = parse_protobuf_to_dataframe(bus_number)

    # Ensure "templates/" directory exists before saving
    templates_path = os.path.join(os.getcwd(), "templates")
    if not os.path.exists(templates_path):
        os.makedirs(templates_path)  # Create the templates directory if missing

    # Set correct path for bus icon
    bus_icon_path = os.path.join("static", "images", "ttc_bus.png")

    # Add live bus locations to map
    for _, vehicle in vehicle_df.iterrows():

        popup_html = f"""
        <b>Vehicle ID:</b> {vehicle["vehicle_id"]}<br>
        <b>Speed:</b> {vehicle["speed"]} km/h<br>
        <b>Occupancy:</b> {vehicle["occupancy_status"]}<br>
        """
        bus_icon = folium.CustomIcon(bus_icon_path, icon_size=(30, 25))
        folium.Marker(
            location=[vehicle["latitude"], vehicle["longitude"]],
            icon=bus_icon,
            popup=popup_html,
        ).add_to(toronto_map)

    # Save the map inside the templates folder
    map_path = os.path.join(templates_path, "toronto_map.html")
    toronto_map.save(map_path)
    print(f"✅ Map successfully saved at {map_path}")

    return "toronto_map.html"
