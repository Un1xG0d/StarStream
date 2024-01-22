gpsmon &
sleep 30
cd /home/admin/StarStream
python3 tracker_iss.py &
python3 tracker_noaa.py &
python3 web.py
