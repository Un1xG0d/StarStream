# AutoARISS
## Overview
The idea behind this project is to automate the receiving and logging of communications from the [amateur radio repeater on the International Space Station](https://www.ariss.org/).

## Getting Started
### Install dependencies
Install all required modules with the command:
```
pip3 install -r requirements.txt
```

### Start the tracking script
Start the tracking script as a background process:
```
python3 tracker.py &
```

This script will constantly query the location of the ISS and will start recording when the distance is less than 500 miles away from your current location. You can adjust the distance in the `minimum_distance` variable of the `config` object.

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
