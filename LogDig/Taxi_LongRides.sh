#!/bin/bash
echo "Start"

MY_PATH="/home/esa/projects/LA"

SCRIPT_PATH=${MY_PATH}"/LogDig/"
LOGS_PATH=${MY_PATH}"/LogFile/PreProsessed/TaxiRides/"
RESULT_PATH=${MY_PATH}"/LogRes/TaxiRides/"
ANALYZE_PATH=${MY_PATH}"/LogAna/"
ANALYZE_FILE="Taxi_LongRides"

python ${SCRIPT_PATH}LogDig.py \
		-date 01.01.2013 \
		-start_time 00:00:00 \
		-stop_time 23:59:59 \
		-input_logs_path $LOGS_PATH \
		-input_ssd_path $LOGS_PATH \
		-output_files_path $RESULT_PATH \
		-analyze_file_path $ANALYZE_PATH \
		-analyze_file $ANALYZE_FILE \
		-analyze_file_mode NEW \
		-analyzing_mode NORMAL:0 \
		-gui_enable 1 \
		-gui_seq_draw_mode "time"

#		-analyzing_mode COMPARE:3 ^
#		-analyzing_mode NORMAL:0 ^
#		-gui_seq_draw_mode "search"
