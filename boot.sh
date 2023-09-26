#!/bin/bash
gpsmon &
sleep 30
cd /home/admin/AutoARISS
python3 tracker.py &
python3 web.py
