from google.transit import gtfs_realtime_pb2
from src.config import vehicles_url
from src.scraper import scrape_gtfs_rt
from datetime import datetime, timezone, timedelta
import pandas as pd


def parse_protobuf_to_dataframe(bus_number):
    """Parses GTFS-Realtime vehicle data into a Pandas DataFrame for a specific bus route.

    This function retrieves real-time vehicle data from the GTFS-Realtime feed, filters
    vehicles based on the provided bus route number (`route_short_name` in GTFS-Static data, but `route_id` in GTFS-Realtime data), and formats the data
    into a Pandas DataFrame.

    Args:
        bus_number (int or str): The `route_id` of the bus route to filter vehicles for.

    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - route_id (str): The ID of the bus route.
            - vehicle_id (str): Unique identifier for the vehicle.
            - latitude (float): Latitude coordinate of the vehicle's current position.
            - longitude (float): Longitude coordinate of the vehicle's current position.
            - bearing (float): Direction the vehicle is facing in degrees.
            - speed (float): Speed of the vehicle in km/h.
            - occupancy_status (str): The occupancy level of the vehicle (e.g., "EMPTY", "FULL").
            - last_updated (str): The last recorded timestamp of the vehicle in local Eastern Time (YYYY-MM-DD HH:MM:SS).

    Raises:
        google.protobuf.message.DecodeError: If the GTFS-RT data cannot be parsed correctly.
        KeyError: If an expected field is missing in the Protobuf data.

    """

    # Fetch raw Protobuf data
    raw_data = scrape_gtfs_rt(vehicles_url)
    if raw_data is None:
        print("Error: GTFS-RT data could not be fetched.")

        # Return an empty DataFrame if no data is available
        return pd.DataFrame()

    # Parse Protobuf
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(raw_data)
    except Exception as e:
        print(f"Error: Failed to parse GTFS-RT data: {e}")
        return pd.DataFrame()

    # Extract vehicle data
    data = []
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle

            # Ensure the correct route_id is used
            if vehicle.trip.route_id != str(bus_number):

                # Skip if not the correct bus
                continue

            # Handle missing timestamp
            timestamp = getattr(vehicle, "timestamp", None)
            if timestamp:
                utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                eastern_time = timezone(timedelta(hours=-5))
                formatted_time = utc_time.astimezone(eastern_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                formatted_time = "Unknown"

            # Handle missing position data
            if hasattr(vehicle, "position"):
                latitude = getattr(vehicle.position, "latitude", None)
                longitude = getattr(vehicle.position, "longitude", None)
                bearing = getattr(vehicle.position, "bearing", None)
                speed = round(getattr(vehicle.position, "speed", 0) * 3.6, 2)
            else:
                latitude, longitude, bearing, speed = None, None, None, 0

            # Map occupancy status
            occupancy_mapping = {
                0: "EMPTY",
                1: "MANY_SEATS_AVAILABLE",
                2: "FEW_SEATS_AVAILABLE",
                3: "STANDING_ROOM_ONLY",
                4: "CRUSHED_STANDING_ROOM_ONLY",
                5: "FULL",
                6: "NOT_ACCEPTING_PASSENGERS",
            }
            occupancy_status = occupancy_mapping.get(
                getattr(vehicle, "occupancy_status", -1), "UNKNOWN"
            )

            # Append vehicle data to list
            data.append(
                {
                    "route_id": vehicle.trip.route_id,
                    "vehicle_id": vehicle.vehicle.id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "bearing": bearing,
                    "speed": speed,
                    "occupancy_status": occupancy_status,
                    "last_updated": formatted_time,
                }
            )

    # Convert list to DataFrame
    return pd.DataFrame(data)


def get_recent_timestamp():

    raw_data = scrape_gtfs_rt(vehicles_url)
    if raw_data is None:
        print("Error: GTFS-RT data could not be fetched.")
        return None

    # Parse Protobuf
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(raw_data)
    except Exception as e:
        print(f"Error: Failed to parse GTFS-RT data: {e}")
        return None

    # Safely get timestamp
    update_timestamp = getattr(feed.header, "timestamp", None)
    if update_timestamp is None:
        return None  # Better than returning "Unknown"

    else:
        utc_time = datetime.fromtimestamp(update_timestamp, tz=timezone.utc)
        eastern_time = timezone(timedelta(hours=-5))
        formatted_update_timestamp = utc_time.astimezone(eastern_time).strftime(
            "%Y-%m-%d %I:%M:%S %p"  # 12-hour format with AM/PM
        )

    return formatted_update_timestamp
