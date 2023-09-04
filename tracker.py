import geopy.distance
import ipinfo
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

config = {
	"user_location": [0, 0],
	"minimum_distance": 500
}

def append_to_log(filename, contents):
	with open(filename, "a") as file:
		file.write(contents)

def get_user_location():
	handler = ipinfo.getHandler(os.getenv("IPINFO_TOKEN"))
	location = handler.getDetails().loc.split(",")
	return [float(location[0]), float(location[1])]

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_distance_between(coords_1, coords_2):
	return geopy.distance.geodesic(coords_1, coords_2).miles

def main():
	append_to_log("logs/tracker_output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Started tracker." + "\n")
	config["user_location"] = get_user_location()
	while True:
		iss_location = get_iss_location()
		distance = get_distance_between(config["user_location"], iss_location)

		if distance < config["minimum_distance"]:
			timestamp = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
			append_to_log("logs/tracker_output.log", "[" + timestamp + "] ISS became within the minimum distance." + "\n")
			append_to_log("logs/tracker_output.log", "[" + timestamp + "] ISS is currently " + str(round(distance, 1)) + " miles away." + "\n")
			recording_output = {
				"timestamp": timestamp,
				"user_location": str(config["user_location"]),
				"iss_location": str(iss_location),
				"distance": str(round(distance, 1)),
				"audio_file": ""
			}
			append_to_log("logs/recordings.json", json.dumps(recording_output) + "\n")
			# TODO - use the SDR to start receiving on the ISS frequency (437.800 MHz)
			# TODO - convert the received signal to an audio file
			# TODO - convert the raw audio file to a wav
			# TODO - transcribe the audio file

		time.sleep(30)

main()