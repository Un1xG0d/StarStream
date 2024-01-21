import json
import natsort
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from gps3.agps3threaded import AGPS3mechanism
from operator import itemgetter
from subprocess import Popen, PIPE

load_dotenv()
agps_thread = AGPS3mechanism()
agps_thread.stream_data()
agps_thread.run_thread()

config = {
	"user_location": [0, 0],
	"interval_seconds": 30
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

def get_noaa_passes():
	passes = []
	noaa_satellites = [{"name": "NOAA 15", "id": 25338, "downlink": 137.62}, {"name": "NOAA 18", "id": 28654, "downlink": 137.9125}, {"name": "NOAA 19", "id": 33591, "downlink": 137.1}]
	for sat in noaa_satellites:
		r = requests.get("https://api.n2yo.com/rest/v1/satellite/radiopasses/" + str(sat["id"]) + "/" + str(config["user_location"][0]) + "/" + str(config["user_location"][1]) + "/0/1/40/&apiKey=" + os.getenv("N2YO_API_KEY")).json()
		for p in r["passes"]:
			local_time = datetime.fromtimestamp(p["startUTC"]).strftime("%m-%d-%Y %H:%M")
			duration = datetime.fromtimestamp(p["endUTC"]) - datetime.fromtimestamp(p["startUTC"])
			passes.append({"name": sat["name"], "next_pass_utc": p["startUTC"], "next_pass_local": local_time, "max_elevation": int(round(p["maxEl"], 0)), "duration": int(duration.total_seconds()), "downlink": sat["downlink"]})
	passes = natsort.natsorted(passes, key=itemgetter(*["next_pass_utc"]))
	return passes

def get_user_location():
	print("Attempting to get current location...")
	time.sleep(15)
	if type(agps_thread.data_stream.lat) is float:
		print(f"Got user location: [{agps_thread.data_stream.lat},{agps_thread.data_stream.lon}]")
		return [agps_thread.data_stream.lat, agps_thread.data_stream.lon]
	else:
		get_user_location()
	print(f"Got user location: [{agps_thread.data_stream.lat},{agps_thread.data_stream.lon}]")
	return [agps_thread.data_stream.lat, agps_thread.data_stream.lon]

def update_audio_file(timestamp_readable, timestamp_epoch):
	lines = []
	with open("logs/recordings.json") as file:
		for line in file.readlines():
			lines.append(json.loads(line))
	for line in lines:
		if line["timestamp"] == timestamp_readable:
			line["audio_file"] = "recordings/" + timestamp_epoch + ".wav"
	with open("logs/recordings.json", "w") as file:
		for line in lines:
			file.write(f"{json.dumps(line)}\n")

def update_image(timestamp_readable, timestamp_epoch):
	lines = []
	with open("logs/recordings.json") as file:
		for line in file.readlines():
			lines.append(json.loads(line))
	for line in lines:
		if line["timestamp"] == timestamp_readable:
			line["image"] = "images/" + timestamp_epoch + ".png"
	with open("logs/recordings.json", "w") as file:
		for line in lines:
			file.write(f"{json.dumps(line)}\n")

def main():
	config["user_location"] = get_user_location()
	passes = get_noaa_passes()
	while True:
		for p in passes:
			if abs(p["next_pass_utc"] - int(datetime.now().strftime("%s"))) <= config["interval_seconds"]:
				timestamp = datetime.now()
				timestamp_readable = timestamp.strftime("%m-%d-%Y %H:%M:%S")
				timestamp_epoch = timestamp.strftime("%s")
				recording_output = {
					"timestamp": timestamp_readable,
					"user_location": str(config["user_location"]),
					"iss_location": "None",
					"distance": "None",
					"elevation_angle": "None",
					"frequency": str(p["downlink"]),
					"audio_file": "",
					"transcript": "",
					"image": ""
				}
				append_to_log("logs/recordings.json", json.dumps(recording_output) + "\n")
				execute_command("timeout " + str(p["duration"]) + "s rtl_fm -f " + str(p["downlink"]) + "M -s 55k -E wav -E deemp -F 9 static/recordings/" + timestamp_epoch + ".raw")
				execute_command("sox -t raw -r 55k -es -b 16 -c 1 static/recordings/" + timestamp_epoch + ".raw static/recordings/" + timestamp_epoch + ".wav rate 11025")
				execute_command("rm -rf static/recordings/" + timestamp_epoch + ".raw")
				update_audio_file(timestamp_readable, timestamp_epoch)
				append_to_log("logs/tracker_output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Saved recording to: " + timestamp_epoch + ".wav" + "\n")
				execute_command("decoder/noaa-apt static/recordings/" + timestamp_epoch + ".wav --sat " + p["name"].lower().replace(" ", "_") + " -o static/images/" + timestamp_epoch + ".png --rotate yes")
				update_image(timestamp_readable, timestamp_epoch)
				append_to_log("logs/tracker_output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Finished processing image." + "\n")

		print("Sleeping for " + str(config["interval_seconds"]) + " seconds.")
		time.sleep(config["interval_seconds"])

main()