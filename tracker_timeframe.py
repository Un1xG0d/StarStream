import geocoder
import geopy.distance
import json
import requests
import time
from datetime import datetime

def append_to_log(filename, contents):
	with open(filename, "a") as file:
		file.write(contents)

def get_user_location():
	return geocoder.ip("me").latlng

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_distance_between(coords_1, coords_2):
	return geopy.distance.geodesic(coords_1, coords_2).miles

def main():
	overpass_estimate = input("Enter estimated time of overpass (09-04-2023 03:25): ")
	default_overpass_estimate = "09-04-2023 03:25"
	if overpass_estimate == "":
		overpass_estimate = default_overpass_estimate
	check_minutes_before_eta = 5
	while True:
		eta_date, eta_time = overpass_estimate.split(" ")
		eta = datetime(int(eta_date.split("-")[2]), int(eta_date.split("-")[0]), int(eta_date.split("-")[1]), int(eta_time.split(":")[0]), int(eta_time.split(":")[1]), 00)
		current = datetime.now()
		difference = eta - current
		minutes_to_overpass = round(difference.total_seconds() / 60)
		print("Minutes to overpass: " + str(minutes_to_overpass))
		while abs(minutes_to_overpass) <= check_minutes_before_eta:
			print("Less than " + str(check_minutes_before_eta) + " minutes to overpass.\nLogging data!")
			user_location = get_user_location()
			iss_location = get_iss_location()
			distance = round(get_distance_between(user_location, iss_location), 10)
			output = {
				"timestamp": datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
				"user_location": str(user_location),
				"iss_location": str(iss_location),
				"distance": str(distance)
			}
			append_to_log("logs/overpass_" + eta_date + ".json", json.dumps(output) + "\n")
			time.sleep(5)
		else:
			print("No overpass within " + str(check_minutes_before_eta) + " minutes! Sleeping.")
			time.sleep(60)

main()