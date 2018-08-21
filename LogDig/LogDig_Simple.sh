#!/bin/bash
echo "Start"

MY_PATH="/home/esa/projects/LA"

SCRIPT_PATH=${MY_PATH}"/LogDig/"
LOGS_PATH=${MY_PATH}"/LogFile/PreProsessed/Simple/"
SSD_PATH=${MY_PATH}"/SSDFile/Simple/"
RESULT_PATH=${MY_PATH}"/LogRes/Simple/"
ANALYZE_PATH=${MY_PATH}"/LogAna/"
ANALYZE_FILE="logdig_Simple"

python ${SCRIPT_PATH}LogDig.py \
	-date 21.06.2016 \
	-start_time 12:00:00 \
	-stop_time 12:20:00 \
	-input_logs_path ${LOGS_PATH} \
	-input_ssd_path ${SSD_PATH} \
	-output_files_path ${RESULT_PATH} \
	-analyze_file_path ${ANALYZE_PATH} \
	-analyze_file ${ANALYZE_FILE} \
	-analyze_file_mode NEW \
	-analyzing_mode NORMAL:0 \
	-gui_enable 0 \
	-gui_seq_draw_mode "order" \
	-ge_kml_enable 0

#	-analyzing_mode COMPARE:3 ^
#	-analyzing_mode NORMAL:0 ^
#	-gui_seq_draw_mode "search"
