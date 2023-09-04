# AutoARISS
## Overview
The idea behind this project is to automate the receiving and logging of communications from the [amateur radio repeater on the International Space Station](https://www.ariss.org/).

## Installing dependencies
Install all required modules with the command:
```
pip3 install -r requirements.txt
```

## Components
### Realtime distance tracker
The script `tracker_live.py` updates every second and displays the users' location, the current location of the ISS, and the distance (in miles) between them.

### Scheduled logging
The script `tracker_timeframe.py` asks for a future date & time as input. This is an estimated time of when the ISS will pass over your location. It should be in your local time zone, in 24 hour format, formatted like `09-04-2023 03:25`.

The script will start logging data 5 minutes before the estimated overpass and stop 5 minutes after. You can configure this timeframe with the `log_minutes_before_after_eta` variable.

## Future plans
Right now, you must enter an estimated date & time of the next overpass. You can find this information online and with smartphone apps like [ISS Spotter](https://apps.apple.com/us/app/iss-spotter/id523486350). In the future, once a reliable `distance` value has been determined where an attached SDR can start receiving a signal, this will no longer be needed and the signal capture/processing can happen automatically.

## References
[Open Notify API](http://api.open-notify.org/)
