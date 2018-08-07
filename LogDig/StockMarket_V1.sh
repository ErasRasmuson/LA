#!/bin/bash
echo "Start"

MY_PATH="/home/esa/projects/LA"

SCRIPT_PATH=${MY_PATH}"/LogDig/"
LOGS_PATH=${MY_PATH}"/LogFile/PreProsessed/StockMarket/"
RESULT_PATH=${MY_PATH}"/LogRes/StockMarket_V1/"
ANALYZE_PATH=${MY_PATH}"/LogAna/"
ANALYZE_FILE="StockMarket_V1"

python ${SCRIPT_PATH}LogDig.py \
		-date 06.08.2018 \
		-start_time 10:00:00 \
		-stop_time 12:00:00 \
		-input_logs_path $LOGS_PATH \
		-input_ssd_path $LOGS_PATH \
		-output_files_path $RESULT_PATH \
		-analyze_file_path $ANALYZE_PATH \
		-analyze_file $ANALYZE_FILE \
		-analyze_file_mode NEW \
		-analyzing_mode NORMAL:0 \
		-gui_enable 0 \
		-gui_seq_draw_mode "time"

#		-analyzing_mode COMPARE:3 ^
#		-analyzing_mode NORMAL:0 ^
#		-gui_seq_draw_mode "search"
