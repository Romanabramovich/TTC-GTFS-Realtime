from google.transit import gtfs_realtime_pb2
from config import vehicles_url
from scraper import scrape_gtfs_rt
from datetime import datetime, timezone, timedelta
import pandas as pd



def parse_protobuf_to_dataframe(file_path):
    #Read raw Protobuf data
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(scrape_gtfs_rt(file_path))
    #Parse entities into a DataFrame
    data = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
                vehicle = entity.vehicle
                
                vehicle_speed = round(vehicle.position.speed, 2)
                utc_time = datetime.fromtimestamp(vehicle.timestamp, tz=timezone.utc)
                eastern_time = timezone(timedelta(hours=-5))
                local_time = utc_time.astimezone(eastern_time)
                formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
                
                data.append(
                {
                    "route_id" : vehicle.trip.route_id, 
                    "vehicle_id": vehicle.vehicle.id, 
                    "latitude" : vehicle.position.latitude,
                    "longitude" : vehicle.position.longitude,
                    "bearing" : vehicle.position.bearing, 
                    "speed" : vehicle_speed,  
                    "last_updated" : formatted_time,                   
                    "occupancy_status" : vehicle.occupancy_status
                        }
                    )      
    return pd.DataFrame(data)
      
      
    
vehicle_df = parse_protobuf_to_dataframe(vehicles_url)
print(vehicle_df)
            