# AutoARISS
## Overview
The idea behind this project is to automate the receiving and logging of communications from the [amateur radio repeater on the International Space Station](https://www.ariss.org/).

It uses the real-time location of the ISS to determine distance from the user and automatically starts receiving through an attached SDR when the conditions are deemed acceptable.

<h1 align="center">
  <img src="https://github.com/Un1xG0d/AutoARISS/blob/master/images/picture_go_kit.png">
  <br>
  <img src="https://github.com/Un1xG0d/AutoARISS/blob/master/images/screenshot_dashboard.png">
  <br>
  <img src="https://github.com/Un1xG0d/AutoARISS/blob/master/images/screenshot_recordings.png">
  <br>
  <img src="https://github.com/Un1xG0d/AutoARISS/blob/master/images/screenshot_logs.png">
</h1>

## Getting Started
### Configure Raspberry Pi
Install [Raspberry Pi OS Lite (64 bit)](https://www.raspberrypi.com/software/) onto your Raspberry Pi and configure the WiFi & SSH settings.

This is the headless mode without a GUI, which will make the system last longer on battery power.

### Install dependencies
Install all required software with the commands:
```
pip3 install -r requirements.txt
sudo apt install -y ffmpeg gpsd gpsd-clients python3-pip rtl-sdr
```

You may need to configure GPSD to use your [USB GPS receiver](https://www.amazon.com/GlobalSat-BU-353-S4-Receiver-Black-Improved-New/dp/B098L799NH):
```
sudo sed -i 's/GPSD_OPTIONS=""/GPSD_OPTIONS="\/dev\/ttyUSB0"/' /etc/default/gpsd
```

### Set up API accounts
You will need to create an [OpenAI API key](https://openai.com/blog/openai-api) to handle the audio-to-text transcriptions, and an [ngrok token](https://ngrok.com/) to expose the Flask app to the internet without any additional setup like port forwarding.

Once you have these, create a `.env` file in the root project directory and populate it with your personal tokens:
```
NGROK_AUTHTOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Connect your SDR
Before starting the tracker, make sure your SDR is connected via USB. I am using the RTL-SDR kit from [this link](https://a.co/d/3p9rCar).

### Run the bootstrap script
Run `bootstrap.sh` to configure a crontab that automatically starts both the tracking script and the web dashboard on boot.
```
bash bootstrap.sh
```

### Start the tracking script
Start the tracking script as a background process:
```
python3 tracker.py &
```

This script will constantly query the location of the ISS and will start recording when the distance is less than 400 miles away from your current location and the elevation is more than 25 degrees. You can adjust these variables in the `config` object.

### Launch the web dashboard
```
python3 web.py
```

The Dashboard page has general information on the status of the ISS, your recordings, and a map of the real-time position of the ISS.

The Recordings page lets you analyze individual captures, play the converted audio files, and read transcripts of the communications.

The Logs page displays the most recent output of the tracker script.

## References
[Open Notify API](http://api.open-notify.org/)

[Listening to radio with Python](https://epxx.co/artigos/pythonfm_en.html)
