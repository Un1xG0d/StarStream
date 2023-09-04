import geocoder
import geopy.distance
import requests
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table

def get_user_location():
	return geocoder.ip("me").latlng

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_distance_between(coords_1, coords_2):
	return geopy.distance.geodesic(coords_1, coords_2).miles

def main():
	console = Console()
	while True:
		user_location = get_user_location()
		iss_location = get_iss_location()
		distance = round(get_distance_between(user_location, iss_location), 10)

		table = Table(show_header=True, header_style="bold")
		table.title = "[not italic]:rocket:[/] ISS Tracker [not italic]:rocket:[/]"
		table.add_column("Timestamp")
		table.add_column("User Location", justify="right", width=20)
		table.add_column("ISS Location", justify="right", width=20)
		table.add_column("Distance", justify="right", width=16)
		table.add_row(datetime.now().strftime("%m-%d-%Y %H:%M:%S"), str(user_location), str(iss_location), str(distance))
		console.clear()
		console.print(table)
		
		time.sleep(1)

main()