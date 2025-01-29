from google.transit import gtfs_realtime_pb2
from config import vehicles_url
from scraper import scrape_gtfs_rt
from datetime import datetime, timezone, timedelta
import pandas as pd


def parse_protobuf_to_dataframe(route_id):
    # Read raw Protobuf data
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(scrape_gtfs_rt(vehicles_url))
    # Parse entities into a DataFrame
    data = []
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            if vehicle.trip.route_id == str(route_id):
                vehicle_speed = round(getattr(vehicle.position, "speed", 0), 2) * 3.6

                # Timestamp formatting
                utc_time = datetime.fromtimestamp(vehicle.timestamp, tz=timezone.utc)
                eastern_time = timezone(timedelta(hours=-5))
                local_time = utc_time.astimezone(eastern_time)
                formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")

                # Occupancy Status mapping from integer to string representation
                occupancy = vehicle.occupancy_status
                occupancy_mapping = {
                    0: "EMPTY",
                    1: "MANY_SEATS_AVAILABLE",
                    2: "FEW_SEATS_AVAILABLE",
                    3: "STANDING_ROOM_ONLY",
                    4: "CRUSHED_STANDING_ROOM_ONLY",
                    5: "FULL",
                    6: "NOT_ACCEPTING_PASSENGERS",
                }
                occupancy_status = occupancy_mapping.get(occupancy, "UNKNOWN")

                data.append(
                    {
                        "route_id": vehicle.trip.route_id,
                        "vehicle_id": vehicle.vehicle.id,
                        "latitude": vehicle.position.latitude,
                        "longitude": vehicle.position.longitude,
                        "bearing": vehicle.position.bearing,
                        "speed": vehicle_speed,
                        "occupancy_status": occupancy_status,
                        "last_updated": formatted_time,
                    }
                )
    return pd.DataFrame(data)


print(parse_protobuf_to_dataframe(105))
