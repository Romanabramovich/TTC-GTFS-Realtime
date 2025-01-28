import requests

#Parse through GTFS-RT TTC vehicles ProtoBuf data
def scrape_gtfs_rt(url):
    response = requests.get(url)
    if response.status_code == 200:
        #Return Raw Protobuf
        return response.content
    else: 
        print(f"Error fetching data: {response.status_code}")
        return None


#NEXT STEP : AUTOMATE ON A TIMER
