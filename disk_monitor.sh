#!/bin/bash

LOG_DIR="./disk_monitor"
CSV_FILE="$LOG_DIR/disk_monitoring_$(date +%F_%H-%M-%S).csv"
MONITOR_PID_FILE="/tmp/disk_monitor.pid"

start_monitoring() {
  mkdir -p "$LOG_DIR"
  echo "timestamp,free_space,free_inodes" > "$CSV_FILE"
  
  while true
  do
    current_date=$(date +%F)
    if [[ "$current_date" != "$(basename $CSV_FILE .csv | cut -d'_' -f3)" ]]; then
      CSV_FILE="$LOG_DIR/disk_monitoring_$(date +%F_%H-%M-%S).csv"
      echo "timestamp,free_space,free_inodes" > "$CSV_FILE"
    fi
    
    timestamp=$(date +%F_%T)
    free_space=$(df --output=avail / | tail -n 1)
    free_inodes=$(df --output=iavail / | tail -n 1)
    
    echo "$timestamp,$free_space,$free_inodes" >> "$CSV_FILE"
    
    sleep 60
  done &
  
  echo $! > "$MONITOR_PID_FILE"
  echo "Monitor started with PID $!"
}

stop_monitoring() {
  if [ -f "$MONITOR_PID_FILE" ]; then
    kill $(cat "$MONITOR_PID_FILE")
    rm "$MONITOR_PID_FILE"
    echo "Monitor stopped."
  else
    echo "Monitor is not running."
  fi
}

status_monitoring() {
  if [ -f "$MONITOR_PID_FILE" ]; then
    echo "Monitor is running with PID $(cat "$MONITOR_PID_FILE")."
  else
    echo "Monitor is not running."
  fi
}

case "$1" in
  START)
    start_monitoring
    ;;
  STOP)
    stop_monitoring
    ;;
  STATUS)
    status_monitoring
    ;;
  *)
    echo "Use: $0 {START|STOP|STATUS}"
    exit 1
    ;;
esac
