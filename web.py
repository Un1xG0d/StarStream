import calculations
import controls
import mailer
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from gps3.agps3threaded import AGPS3mechanism
from pyngrok import ngrok

def check_logs_exist():
	if not os.path.isfile("logs/recordings.json"):
		open("logs/recordings.json", "a").close()
	if not os.path.isfile("logs/tracker_output.log"):
		open("logs/tracker_output.log", "a").close()

def get_distance_between(coords_1, coords_2):
	distance, elevation_angle = calculations.get_distance_and_elevation_angle(coords_1, coords_2)
	distance_miles = distance * 0.621371
	return distance_miles

def get_geocoded_location(coords, region):
	geolocator = Nominatim(user_agent="GetLoc")
	try:
		return geolocator.reverse(coords).raw["address"][region]
	except:
		return "None"

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_user_location():
	print("Attempting to get current location...")
	time.sleep(45)
	if type(agps_thread.data_stream.lat) is float:
		return [agps_thread.data_stream.lat, agps_thread.data_stream.lon]
	else:
		get_user_location()

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
	recordings = load_json("logs/recordings.json")
	return render_template("index.html", user_location=user_geocoded_location, iss_location=iss_geocoded_location, distance=distance, recordings=recordings)

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
	tracker_output = read_file("logs/tracker_output.log").split("\n")
	return render_template("logs.html", logs=tracker_output)

if __name__ == "__main__":
	check_logs_exist()
	user_location = get_user_location()
	port = 8000
	ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))
	tunnel = ngrok.connect(port)
	mailer.send_email(datetime.now().strftime("%m-%d-%Y %H:%M"), tunnel.public_url)
	app.run(host="0.0.0.0", port=port)
