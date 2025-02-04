from dotenv import load_dotenv
import os

load_dotenv()

vehicles_url = os.getenv("vehicles_url")
trips_url = os.getenv("trips_url")
alerts_url = os.getenv("alerts_url")

