import pandas as pd
import math

def get_route_id(short_name):
    """Fetch the GTFS route_id for a given bus number."""
    try:
        routes_data = pd.read_csv(
            "./TTC-GTFS-Static/routes.txt",
            dtype={"route_id": str, "route_short_name": str},
        )
        matching_route = routes_data[routes_data["route_short_name"] == str(short_name)]

        if matching_route.empty:
            print(f"Warning: No route_id found for bus number {short_name}.")
            return None

        return str(matching_route.iloc[0]["route_id"])
    except FileNotFoundError:
        print("Error: Missing GTFS-Static files (routes.txt).")
        return None


def preprocess_and_cache_data(bus_number):
    """Process and filter GTFS static data for a given bus number."""
    route_id = get_route_id(bus_number)
    if not route_id:
        print(f"Warning: No data found for bus {bus_number}.")
        return None

    try:
        trips_data = pd.read_csv(
            "./TTC-GTFS-Static/trips.txt",
            usecols=["route_id", "trip_id", "shape_id"],
            dtype={"route_id": str, "trip_id": str, "shape_id": str},
        )
        filtered_trips = trips_data[trips_data["route_id"] == route_id]
        shape_ids = filtered_trips["shape_id"].unique()

        if len(shape_ids) == 0:
            print(f"No shape_id found for route_id {route_id} (Bus {bus_number}).")
            return None

        shapes_data = pd.read_csv(
            "./TTC-GTFS-Static/shapes.txt",
            usecols=["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"],
            dtype={"shape_id": str},
        )
        filtered_shapes = shapes_data[shapes_data["shape_id"].isin(shape_ids)]

        # Only save CSVs if data exists
        if not filtered_trips.empty:
            filtered_trips.to_csv("./filtered_trips.csv", index=False)
        if not filtered_shapes.empty:
            filtered_shapes.to_csv("./filtered_shapes.csv", index=False)

        return route_id

    except FileNotFoundError:
        print("Error: Missing GTFS-Static files (trips.txt or shapes.txt).")
        return None


def get_route_color(route_id):
    """Get the designated color of the bus route."""
    try:
        routes_info = pd.read_csv(
            "./TTC-GTFS-Static/routes.txt", dtype={"route_id": str}
        )
        route = routes_info[routes_info["route_id"] == str(route_id)]

        if not route.empty:
            return (
                f"#{route.iloc[0]['route_color']}"
                if "route_color" in route.columns
                else "#000000"
            )
        else:
            print(f"Warning: No color data found for route {route_id}.")
            return "#000000"
    except FileNotFoundError:
        print("Error: Missing GTFS-Static file (routes.txt).")
        return "#000000"


def get_optimal_map_view(shape_df):
    """
    Determines the best center coordinate and zoom level for the bus route.

    Args:
        shape_df (pd.DataFrame): DataFrame containing shape points with `shape_pt_lat` and `shape_pt_lon`.

    Returns:
        tuple: (center_lat, center_lon, zoom_level)
    """
    if shape_df.empty:
        return (43.7, -79.4, 12)  # Default to central Toronto if no data

    # Find bounding box (min/max lat & lon)
    min_lat, max_lat = shape_df["shape_pt_lat"].min(), shape_df["shape_pt_lat"].max()
    min_lon, max_lon = shape_df["shape_pt_lon"].min(), shape_df["shape_pt_lon"].max()

    # Compute center of the route
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    # Estimate zoom level based on distance
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    max_diff = max(lat_diff, lon_diff)

    # Define a simple mapping from coordinate span to zoom level (approximate)
    if max_diff < 0.01:  # Very small route
        zoom_level = 15
    elif max_diff < 0.05:
        zoom_level = 14
    elif max_diff < 0.1:
        zoom_level = 13
    elif max_diff < 0.5:
        zoom_level = 12
    elif max_diff < 1.0:
        zoom_level = 11
    else:
        zoom_level = 10  # Large routes

    return (center_lat, center_lon, zoom_level)
