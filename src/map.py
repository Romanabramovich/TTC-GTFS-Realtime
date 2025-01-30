from folium.plugins import MarkerCluster
from df_processing import parse_protobuf_to_dataframe
import pandas as pd
import folium
import os


def get_route_id(short_name):
    routes_data = pd.read_csv(
        "./TTC-GTFS-Static/routes.txt", dtype={"route_id": str, "route_short_name": str}
    )
    matching_route = routes_data[routes_data["route_short_name"] == str(short_name)]

    if matching_route.empty:
        print(f"Error: No route_id found for bus number {short_name}.")
        return None

    print(f"Route id for {short_name} is \n{matching_route}")
    return str(matching_route.iloc[0]["route_id"])


def preprocess_and_cache_data(bus_number):
    route_id = get_route_id(bus_number)
    if not route_id:
        return None
    print(f"Preprocesing route ID #{route_id}")

    # Filter columns in static trips data
    trips_data = pd.read_csv(
        "./TTC-GTFS-Static/trips.txt",
        usecols=["route_id", "trip_id", "shape_id"],
        dtype={"route_id": str, "trip_id": str, "shape_id": str},
    )
    filtered_trips = trips_data[trips_data["route_id"] == route_id]
    # print(f"the filtered trips for route {route_id} are\n {filtered_trips}")
    shape_ids = filtered_trips["shape_id"].unique()
    # print(f"\nThe unique shape IDs for route {route_id} are \n {shape_ids}")

    if len(shape_ids) == 0:
        print(f"No shape_id found for route_id {route_id} (Bus {bus_number}).")
        return None

    # Filter columns in static shapes data
    shapes_data = pd.read_csv(
        "./TTC-GTFS-Static/shapes.txt",
        usecols=["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"],
        dtype={"shape_id": str},
    )
    filtered_shapes = shapes_data[shapes_data["shape_id"].isin(shape_ids)]
    # print(f"Filtered shape data is: \n{filtered_shapes}")

    # Filter coloumns in trips data
    filtered_trips.to_csv("./filtered_trips.csv", index=False)
    filtered_shapes.to_csv("./filtered_shapes.csv", index=False)

    return route_id


def get_route_color(route_id):
    routes_info = pd.read_csv("./TTC-GTFS-Static/routes.txt", dtype={"route_id": str})

    route = routes_info[routes_info["route_id"] == str(route_id)]
    # print(f"Route Route\n {route}")
    if not route.empty:
        route_color = (
            route.iloc[0]["route_color"] if "route_color" in route.columns else "000000"
        )
        print(f"route color is {route_color}")
        return f"#{route_color}"
    else:
        return "000000"


def get_live_bus_locations(toronto_map, vehicle_df):
    marker_cluster = MarkerCluster().add_to(toronto_map)
    # path_to_image = "../images/ttc_bus.png"

    for _, vehicle in vehicle_df.iterrows():
        bus_icon = folium.CustomIcon(
            r"C:\Users\roman\TTC-GTFS-Realtime\images\ttc_bus.png", icon_size=(30, 25)
        )
        folium.Marker(
            location=[vehicle["latitude"], vehicle["longitude"]], icon=bus_icon
        ).add_to(toronto_map)

    """
    # Now use `bus_icon` in folium.Marker
    for _, vehicle in vehicle_df.iterrows():
        folium.Marker(location=[vehicle["latitude"], vehicle["longitude"]]).add_to(
            marker_cluster
        )

    return marker_cluster
    """


def get_static_bus_route(bus_number):
    """Visualizes the bus route and live vehicle locations on a map."""
    route_id = preprocess_and_cache_data(bus_number)
    if not route_id:
        return  # Stop if no valid route_id
    print(f"---------------Now Visualizing route {route_id} ----------------")
    filtered_trips = pd.read_csv("./filtered_trips.csv", dtype={"shape_id": str})
    # print(filtered_trips)
    filtered_shapes = pd.read_csv(
        "./filtered_shapes.csv", dtype={"shape_pt_lon": float, "shape_pt_lat": float}
    )
    # print(filtered_shapes)

    toronto_map = folium.Map(
        location=[43.72525, -79.402278], zoom_start=12, tiles="CartoDB positron"
    )

    # Add the route shape to the map
    shape_ids = filtered_trips["shape_id"].unique().tolist()
    # print(f"\nThese shape IDS are\n{shape_ids}")

    if len(shape_ids) == 0:
        print(f"No shape data found for bus number {bus_number} (route_id {route_id})!")
    else:
        route_color = get_route_color(route_id)
        for shape_id, group in filtered_shapes.groupby("shape_id"):
            group = group.sort_values("shape_pt_sequence")
            points = group[["shape_pt_lat", "shape_pt_lon"]].values.tolist()

            if len(points) == 0:
                print(f"Warning: No points found for shape_id {shape_id}!")

            folium.PolyLine(points, color=route_color, weight=5, opacity=0.8).add_to(
                toronto_map
            )

    # Get live bus locations
    vehicle_df = parse_protobuf_to_dataframe(bus_number)
    get_live_bus_locations(toronto_map, vehicle_df)

    # Save the map
    map_path = "./templates/toronto_map.html"
    toronto_map.save(map_path)


bus_number = "504"
# Visualize the selected routes
get_static_bus_route(bus_number)
