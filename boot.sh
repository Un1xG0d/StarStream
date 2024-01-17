#!/bin/bash
gpsmon &
sleep 30
cd /home/admin/AutoARISS
python3 tracker_iss.py &
python3 web.py
