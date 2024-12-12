#!/bin/bash

sudo python3 recv_combined.py &
PID1=$!

sudo python3 recv_combined2.py &
PID2=$!

sleep 20

sudo pkill -P $PID1
sudo pkill -P $PID2
kill $PID1
kill $PID2
