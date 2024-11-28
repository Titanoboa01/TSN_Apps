#!/bin/bash

sudo pyhon3 taprio_exporter.py &
PID3=$!

sudo python3 send_combined1.py &
PID1=$!

sudo python3 send_combined2.py &
PID2=$!

sleep 10

sudo pkill -P $PID1
sudo pkill -P $PID2
sudo pkill -P $PID3
kill $PID1
kill $PID2
kill $PID3
