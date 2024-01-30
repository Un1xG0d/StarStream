import calculations
import json
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
from subprocess import Popen, PIPE

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def append_to_log(filename, contents):
	with open(filename, "a") as file:
		file.write(contents)

def execute_command(command):
	project_dir = os.path.abspath("./")
	p = Popen(command, cwd=project_dir, stdout=PIPE, stderr=PIPE, shell=True)
	stdout, stderr = p.communicate()
	if stderr.decode("utf-8") != "":
		print(stderr.decode("utf-8"))

def transcribe_audio(timestamp_epoch):
	return openai.Audio.transcribe("whisper-1", open("static/recordings/" + timestamp_epoch + ".mp3", "rb"))["text"]

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

def start_manual_recording(frequency, seconds_to_record):
	timestamp = datetime.now()
	timestamp_readable = timestamp.strftime("%m-%d-%Y %H:%M:%S")
	timestamp_epoch = timestamp.strftime("%s")
	append_to_log("logs/output.log", "[" + timestamp_readable + "] Started manual recording on " + frequency + " MHz." + "\n")
	recording_output = {
		"timestamp": timestamp_readable,
		"user_location": "None",
		"iss_location": "None",
		"distance": "None",
		"elevation_angle": "None",
		"frequency": frequency,
		"audio_file": "",
		"transcript": "",
		"image": ""
	}
	append_to_log("logs/recordings.json", json.dumps(recording_output) + "\n")
	execute_command("timeout " + seconds_to_record + "s rtl_fm -f " + frequency + "M -s 55k -E wav -E deemp -F 9 static/recordings/" + timestamp_epoch + ".raw")
	execute_command("sox -t raw -r 55k -es -b 16 -c 1 static/recordings/" + timestamp_epoch + ".raw static/recordings/" + timestamp_epoch + ".wav")
	execute_command("rm -rf static/recordings/" + timestamp_epoch + ".raw")
	update_audio_file(timestamp_readable, timestamp_epoch)
	append_to_log("logs/output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Saved recording to: " + timestamp_epoch + ".wav" + "\n")
	if "137" in frequency:
		noaa_satellites = [{"name": "NOAA 15", "id": 25338, "downlink": 137.62}, {"name": "NOAA 18", "id": 28654, "downlink": 137.9125}, {"name": "NOAA 19", "id": 33591, "downlink": 137.1}]
		for sat in noaa_satellites:
			if float(frequency) == sat["downlink"]:
				execute_command("decoder/noaa-apt static/recordings/" + timestamp_epoch + ".wav --sat " + sat["name"].lower().replace(" ", "_") + " -o static/images/" + timestamp_epoch + ".png --rotate yes")
				update_image(timestamp_readable, timestamp_epoch)
				append_to_log("logs/output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Finished processing image." + "\n")
	else:
		execute_command("sox static/recordings/" + timestamp_epoch + ".wav -C 1 static/recordings/" + timestamp_epoch + ".mp3")
		transcript = transcribe_audio(timestamp_epoch)
		update_transcript(timestamp_readable, transcript)
		append_to_log("logs/output.log", "[" + datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] Finished transcribing audio." + "\n")
		execute_command("rm -rf static/recordings/" + timestamp_epoch + ".mp3")