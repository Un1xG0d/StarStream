import calculations
import ipinfo
import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template
from geopy.geocoders import Nominatim

def get_distance_between(coords_1, coords_2):
	distance, elevation_angle = calculations.get_distance_and_elevation_angle(coords_1, coords_2)
	distance_miles = distance * 0.621371
	return distance_miles

def get_geocoded_location(coords):
	geolocator = Nominatim(user_agent="GetLoc")
	try:
		return geolocator.reverse(coords).raw["address"]["state"]
	except:
		return "None"

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_user_location():
	handler = ipinfo.getHandler(os.getenv("IPINFO_TOKEN"))
	location = handler.getDetails().loc.split(",")
	return [float(location[0]), float(location[1])]

def load_json(filename):
	with open(filename) as file:
		lines = []
		for line in file.readlines():
			lines.append(json.loads(line))
		return lines

def read_file(filename):
	with open(filename) as file:
		return file.read()

load_dotenv()
app = Flask(__name__)
user_location = get_user_location()

@app.route("/")
def index():
	iss_location = get_iss_location()
	distance = round(get_distance_between(user_location, iss_location), 1)
	iss_geocoded_location = get_geocoded_location(iss_location)
	recordings = load_json("logs/recordings.json")
	unique_dates = []
	for recording in recordings:
		if recording["timestamp"].split(" ")[0] not in unique_dates:
			unique_dates.append(recording["timestamp"].split(" ")[0])
	return render_template("index.html", distance=distance, iss_location=iss_geocoded_location, recordings=recordings, unique_dates=unique_dates)

@app.route("/logs")
def logs():
	tracker_output = read_file("logs/tracker_output.log").split("\n")
	return render_template("logs.html", logs=tracker_output)

@app.route("/recordings")
def recordings():
	recordings = load_json("logs/recordings.json")
	return render_template("recordings.html", recordings=recordings)
