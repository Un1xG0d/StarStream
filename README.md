# AutoARISS
## Overview
The idea behind this project is to automate the receiving and logging of communications from the [amateur radio repeater on the International Space Station](https://www.ariss.org/).

It uses the real-time location of the ISS to determine distance from the user and automatically starts receiving through an attached SDR when the conditions are deemed acceptable.

<h1 align="center">
  <img src="https://github.com/Un1xG0d/AutoARISS/blob/master/images/screenshot_dashboard_1.png">
</h1>

## Getting Started
### Install dependencies
Install all required modules with the command:
```
pip3 install -r requirements.txt
sudo port install ffmpeg rtl-sdr
```

> NOTE: You will need to install [MacPorts](https://www.macports.org/install.php) first, if you don’t already have it.

### Set up IPInfo access
In order to prevent rate limiting, you will need to create a free account for the [IP Geolocation API](https://ipinfo.io/products/ip-geolocation-api).

Once you have your access token, create a `.env` file in the root directory and populate it with your personal token:
```
IPINFO_TOKEN=xxxxxxxxxxxxxx
```

### Connect your SDR
Before starting the tracker, make sure your SDR is connected via USB. I am using the RTL-SDR kit from [this link](https://a.co/d/3p9rCar).

### Start the tracking script
Start the tracking script as a background process:
```
python3 tracker.py &
```

This script will constantly query the location of the ISS and will start recording when the distance is less than 200 miles away from your current location. You can adjust the distance in the `minimum_distance` variable of the `config` object.

### Launch the web dashboard
```
export FLASK_APP=app
flask run
```

The Dashboard page has general information on the status of the ISS, your recordings, and a map of the real-time position of the ISS.

The Recordings page lets you analyze individual captures, play the converted audio files, and read transcripts of the communications.

The Logs page displays the most recent output of the tracker script.

## References
[Open Notify API](http://api.open-notify.org/)

[Listening to radio with Python](https://epxx.co/artigos/pythonfm_en.html)
