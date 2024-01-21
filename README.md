# AutoARISS
## Overview
The idea behind this project is to automate the receiving and logging of communications from the [amateur radio repeater on the International Space Station](https://www.ariss.org/).

It uses the real-time location of the ISS to determine distance from the user and automatically starts receiving through an attached SDR when the conditions are deemed acceptable.

It can also automatically capture and process NOAA weather satellite images.

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
Install [Raspberry Pi OS Lite (64 bit)](https://www.raspberrypi.com/software/) onto your Raspberry Pi, configure the WiFi settings, and create an account with the username `admin`.

This is the headless mode without a GUI, which will make the system last longer on battery power.

### Install dependencies
Install required software with the commands:
```
sudo apt install -y ffmpeg gpsd gpsd-clients python3-pip rtl-sdr sox
pip3 install -r requirements.txt
```

You will also need to install the [NOAA-APT image decoder](https://noaa-apt.mbernardi.com.ar/):
```
wget https://github.com/martinber/noaa-apt/releases/download/v1.4.1/noaa-apt-1.4.1-aarch64-linux-gnu-nogui.zip -O /home/admin/AutoARISS/decoder/noaa-apt-1.4.1-aarch64-linux-gnu-nogui.zip
unzip /home/admin/AutoARISS/decoder/noaa-apt-1.4.1-aarch64-linux-gnu-nogui.zip -d /home/admin/AutoARISS/decoder/
rm -rf /home/admin/AutoARISS/decoder/noaa-apt-1.4.1-aarch64-linux-gnu-nogui.zip
```

You may need to configure GPSD to use your [USB GPS receiver](https://www.amazon.com/GlobalSat-BU-353-S4-Receiver-Black-Improved-New/dp/B098L799NH):
```
sudo sed -i 's/GPSD_OPTIONS=""/GPSD_OPTIONS="\/dev\/ttyUSB0"/' /etc/default/gpsd
```

### Set up API accounts
You will need to create an [OpenAI API key](https://openai.com/blog/openai-api) to handle the audio-to-text transcriptions, and an [ngrok token](https://ngrok.com/) to expose the Flask app to the internet without any additional setup like port forwarding.

You will also need to create a [Gmail app password](https://myaccount.google.com/apppasswords) to send the latest dashboard URL to yourself when the app is started.

If you want to capture images from the NOAA satellites, you will also need an API key for the [N2YO API](https://www.n2yo.com/login/register/).

Once you have these, create a `.env` file in the root project directory and populate it with your personal tokens:
```
GMAIL_ADDRESS=example@gmail.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxxxxx
N2YO_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
NGROK_AUTHTOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Connect your SDR
Before starting the trackers, make sure your SDR is connected via USB. I am using the RTL-SDR kit from [this link](https://a.co/d/3p9rCar).

### Run the bootstrap script
Run `bootstrap.sh` once to configure a crontab that automatically starts both the tracking scripts and the web dashboard on boot.
```
bash bootstrap.sh
```

### Start the ISS tracking script
Start the ISS tracking script as a background process:
```
python3 tracker_iss.py &
```

This script will constantly query the location of the ISS and will start recording when the distance is less than 400 miles away from your current location and the elevation is more than 25 degrees. You can adjust these variables in the `config` object.

### Start the NOAA tracking script
Start the NOAA tracking script as a background process:
```
python3 tracker_noaa.py &
```

This script collects a list of NOAA satellite passes overhead of your location. It constantly compares the timestamps of the future passes to the current timestamp, and starts recording when the satellite is nearby. It will automatically process each recording into a satellite image, which you can view on the web interface.

### Launch the web interface
```
python3 web.py
```

The Dashboard page has general information on the status of the ISS, your recordings, and a map of the real-time position of the ISS.

The Recordings page lets you analyze individual captures, play the converted audio files, read transcripts of the communications, and view any processed satellite images.

The Controls page allows you to specify parameters and manually capture a recording.

The Logs page displays the most recent output of the tracker scripts.

## References
[NOAA-APT Image Decoder Documentation](https://noaa-apt.mbernardi.com.ar/usage.html#terminal-1)

[N2YO API Documentation](https://www.n2yo.com/api/#radiopasses)

[Where the ISS at? API Documentation](https://wheretheiss.at/w/developer)

[Listening to radio with Python](https://epxx.co/artigos/pythonfm_en.html)
