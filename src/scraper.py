import requests


def scrape_gtfs_rt(url):
    """Fetches GTFS-Realtime (GTFS-RT) data from the given URL.

    This function retrieves the latest Toronto Transit Commission (TTC) GTFS-RT feed,
    which may contain real-time vehicle positions, trip updates, or alerts.

    Args:
        url (str): The URL of the GTFS-RT feed.

    Returns:
        bytes: Raw Protobuf data if the request is successful.
        None: If the request fails.

    Raises:
        requests.exceptions.RequestException: If the request encounters a network issue.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        #Return raw Protobuf data
        return response.content  
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
