import calculations
import controls
import mailer
import natsort
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
from geopy.geocoders import Nominatim
from gps3.agps3threaded import AGPS3mechanism
from operator import itemgetter
from pyngrok import ngrok

def check_logs_exist():
	if not os.path.isfile("logs/recordings.json"):
		open("logs/recordings.json", "a").close()
	if not os.path.isfile("logs/output.log"):
		open("logs/output.log", "a").close()

def get_distance_between(coords_1, coords_2):
	distance, elevation_angle = calculations.get_distance_and_elevation_angle(coords_1, coords_2)
	distance_miles = distance * 0.621371
	return distance_miles

def get_geocoded_location(coords, region):
	geolocator = Nominatim(user_agent="GetLoc")
	try:
		return geolocator.reverse([coords[0], coords[1]]).raw["address"][region]
	except:
		return "None"

def get_iss_location():
	r = requests.get("https://api.wheretheiss.at/v1/satellites/25544").json()
	return [float(r["latitude"]), float(r["longitude"]), float(r["altitude"])]

def get_noaa_passes():
	passes = []
	noaa_satellites = [{"name": "NOAA 15", "id": 25338, "downlink": 137.62}, {"name": "NOAA 18", "id": 28654, "downlink": 137.9125}, {"name": "NOAA 19", "id": 33591, "downlink": 137.1}]
	for sat in noaa_satellites:
		r = requests.get("https://api.n2yo.com/rest/v1/satellite/radiopasses/" + str(sat["id"]) + "/" + str(user_location[0]) + "/" + str(user_location[1]) + "/0/1/40/&apiKey=" + os.getenv("N2YO_API_KEY")).json()
		for p in r["passes"]:
			local_time = datetime.fromtimestamp(p["startUTC"]).strftime("%m-%d-%Y %H:%M")
			duration = datetime.fromtimestamp(p["endUTC"]) - datetime.fromtimestamp(p["startUTC"])
			passes.append({"name": sat["name"], "next_pass_utc": p["startUTC"], "next_pass_local": local_time, "max_elevation": int(round(p["maxEl"], 0)), "duration": int(duration.total_seconds()), "downlink": sat["downlink"]})
	passes = natsort.natsorted(passes, key=itemgetter(*["next_pass_utc"]))
	return passes

def get_user_location():
	print("Attempting to get current location...")
	if type(agps_thread.data_stream.lat) is float:
		print(f"Got user location: [{agps_thread.data_stream.lat},{agps_thread.data_stream.lon}]")
		return [agps_thread.data_stream.lat, agps_thread.data_stream.lon]
	else:
		time.sleep(15)
		get_user_location()
	print(f"Got user location: [{agps_thread.data_stream.lat},{agps_thread.data_stream.lon}]")
	return [agps_thread.data_stream.lat, agps_thread.data_stream.lon]

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
agps_thread = AGPS3mechanism()
agps_thread.stream_data()
agps_thread.run_thread()

@app.route("/", methods=["GET"])
def dashboard_route():
	iss_location = get_iss_location()
	distance = round(get_distance_between(user_location, iss_location), 1)
	user_geocoded_location = get_geocoded_location(user_location, "city")
	iss_geocoded_location = get_geocoded_location(iss_location, "state")
	passes = get_noaa_passes()
	recordings = load_json("logs/recordings.json")
	return render_template("index.html", user_location=user_geocoded_location, iss_location=iss_geocoded_location, distance=distance, passes=passes, recordings=recordings)

@app.route("/recordings", methods=["GET"])
def recordings_route():
	recordings = load_json("logs/recordings.json")
	return render_template("recordings.html", recordings=recordings)

@app.route("/controls", methods=["GET", "POST"])
def controls_route():
	if request.method == "GET":
		return render_template("controls.html")
	if request.method == "POST":
		controls.start_manual_recording(request.form["frequency"], request.form["seconds_to_record"])
		return redirect("/recordings")

@app.route("/logs", methods=["GET"])
def logs_route():
	tracker_output = read_file("logs/output.log").split("\n")
	return render_template("logs.html", logs=tracker_output)

if __name__ == "__main__":
	check_logs_exist()
	user_location = get_user_location()
	port = 8000
	ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))
	tunnel = ngrok.connect(port)
	mailer.send_email(datetime.now().strftime("%m-%d-%Y %H:%M"), tunnel.public_url)
	app.run(host="0.0.0.0", port=port)
