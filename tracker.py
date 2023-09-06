import geopy.distance
import ipinfo
import json
import openai
import os
import pyproj
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from subprocess import Popen, PIPE

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

config = {
	"user_location": [0, 0],
	"minimum_distance": 200,
	"minimum_elevation_angle": 30,
	"interval_seconds": 30,
	"frequency": 437.8,
	"seconds_to_record": 60,
	"sample_rate": 256
}

def append_to_log(filename, contents):
	with open(filename, "a") as file:
		file.write(contents)

def execute_command(command):
	project_dir = os.path.abspath("./")
	p = Popen(command, cwd=project_dir, stdout=PIPE, stderr=PIPE, shell=True)
	stdout, stderr = p.communicate()
	if stderr.decode("utf-8") != "":
		print(stderr.decode("utf-8"))

def get_user_location():
	handler = ipinfo.getHandler(os.getenv("IPINFO_TOKEN"))
	location = handler.getDetails().loc.split(",")
	return [float(location[0]), float(location[1])]

def get_elevation_angle(coords_1, coords_2):
	geodesic = pyproj.Geod(ellps="WGS84")
	forward_azimuth, back_azimuth, distance = geodesic.inv(coords_1[1], coords_1[0], coords_2[1], coords_2[0])
	return forward_azimuth

def get_iss_location():
	r = requests.get("http://api.open-notify.org/iss-now.json")
	return [float(r.json()["iss_position"]["latitude"]), float(r.json()["iss_position"]["longitude"])]

def get_distance_between(coords_1, coords_2):
	return geopy.distance.geodesic(coords_1, coords_2).miles

def transcribe_audio(timestamp_epoch):
	return openai.Audio.transcribe("whisper-1", open("recordings/" + timestamp_epoch + ".mp3", "rb"))["text"]

def update_audio_file(timestamp_readable, timestamp_epoch):
	lines = []
	with open("logs/recordings.json") as file:
		for line in file.readlines():
			lines.append(json.loads(line))
	for line in lines:
		if line["timestamp"] == timestamp_readable:
			line["audio_file"] = "recordings/" + timestamp_epoch + ".mp3"
	with open("logs/recordings.json", "w") as file:
		for line in lines:
			file.write(f"{json.dumps(line)}\n")

def update_transcript(timestamp_readable, transcript):
	lines = []
	with open("logs/recordings.json") as file:
		for line in file.readlines():
			lines.append(json.loads(line))
	for line in lines:
		if line["timestamp"] == timestamp_readable:
			line["transcript"] = transcript
	with open("logs/recordings.json", "w") as file:
		for line in lines:
			file.write(f"{json.dumps(line)}\n")

def main():
	append_to_log("logs/tracker_output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Started tracker." + "\n")
	config["user_location"] = get_user_location()
	while True:
		iss_location = get_iss_location()
		distance = get_distance_between(config["user_location"], iss_location)
		elevation_angle = get_elevation_angle(config["user_location"], iss_location)

		if distance < config["minimum_distance"] and elevation_angle > config["minimum_elevation_angle"]:
			timestamp = datetime.now()
			timestamp_readable = timestamp.strftime("%m-%d-%Y %H:%M:%S")
			timestamp_epoch = timestamp.strftime("%s")
			append_to_log("logs/tracker_output.log", "[" + timestamp_readable + "] The ISS became within the minimum distance." + "\n")
			append_to_log("logs/tracker_output.log", "[" + timestamp_readable + "] The ISS is currently " + str(round(distance, 1)) + " miles away." + "\n")
			append_to_log("logs/tracker_output.log", "[" + timestamp_readable + "] The elevation angle is " + str(round(elevation_angle, 1)) + " degrees." + "\n")
			recording_output = {
				"timestamp": timestamp_readable,
				"user_location": str(config["user_location"]),
				"iss_location": str(iss_location),
				"distance": str(round(distance, 1)),
				"elevation_angle": str(round(elevation_angle, 1)),
				"audio_file": "",
				"transcript": ""
			}
			append_to_log("logs/recordings.json", json.dumps(recording_output) + "\n")
			execute_command("rtl_sdr -f " + str(config["frequency"]) + "M -s " + str(config["sample_rate"]) + "k -n " + str(config["sample_rate"] * config["seconds_to_record"] * 1000) + " recordings/" + timestamp_epoch + ".iq")
			append_to_log("logs/tracker_output.log", "[" + timestamp_readable + "] Started recording on " + str(config["frequency"]) + " MHz." + "\n")
			execute_command("cat recordings/" + timestamp_epoch + ".iq | ./demodulator.py > recordings/" + timestamp_epoch + ".raw")
			execute_command("ffmpeg -f s16le -ac 1 -ar " + str(config["sample_rate"]) + "000 -acodec pcm_s16le -i recordings/" + timestamp_epoch + ".raw -af 'highpass=f=200, lowpass=f=3000, volume=4' recordings/" + timestamp_epoch + ".mp3")
			execute_command("rm -rf recordings/" + timestamp_epoch + ".iq recordings/" + timestamp_epoch + ".raw")
			update_audio_file(timestamp_readable, timestamp_epoch)
			transcript = transcribe_audio(timestamp_epoch)
			update_transcript(timestamp_readable, transcript)
			append_to_log("logs/tracker_output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Saved recording to: recordings/" + timestamp_epoch + ".mp3" + "\n")

		print("Sleeping for " + str(config["interval_seconds"]) + " seconds.")
		time.sleep(config["interval_seconds"])

main()